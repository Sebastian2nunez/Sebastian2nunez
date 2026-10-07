#!/usr/bin/env python3
"""Mini benchmark para comparar modelos locales (API compatible con OpenAI, p. ej. llama-server).

Solo usa la librería estándar. Ejecuta el código que generan los modelos: usa un contenedor o VM
si no te fías de lo que pueda escribir un modelo.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime

from tasks import TASKS

HERE = os.path.dirname(os.path.abspath(__file__))
SYSTEM = "Eres un asistente experto en programación y lógica. Sigue el formato pedido al pie de la letra."


# ------------------------------------------------------------------ cliente
def chat(model_cfg, prompt, max_tokens, temperature, timeout):
    body = {
        "model": model_cfg.get("model", "default"),
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }
    body.update(model_cfg.get("extra", {}))
    req = urllib.request.Request(
        model_cfg["base_url"].rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + model_cfg.get("api_key", "none"),
        },
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    elapsed = time.time() - t0
    msg = data["choices"][0]["message"]
    usage = data.get("usage", {})
    tokens = usage.get("completion_tokens", 0)
    tps = data.get("timings", {}).get("predicted_per_second") or (tokens / elapsed if elapsed else 0)
    return {
        "content": msg.get("content") or "",
        "reasoning": msg.get("reasoning_content") or "",
        "finish": data["choices"][0].get("finish_reason"),
        "tokens": tokens,
        "elapsed": elapsed,
        "tps": tps,
    }


# ------------------------------------------------------------------ corrección
def strip_think(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    return re.sub(r"^.*?</think>", "", text, flags=re.S).strip()


def extract_code(text):
    blocks = re.findall(r"```(?:python|py)?[ \t]*\n(.*?)```", text, flags=re.S)
    blocks = [b for b in blocks if "def " in b or "class " in b]
    return blocks[-1] if blocks else None


def run_python(source, timeout):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "run.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(source)
        try:
            p = subprocess.run(
                [sys.executable, path], cwd=d, stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return False, "timeout"
        if p.returncode == 0:
            return True, ""
        lines = (p.stderr or p.stdout).strip().splitlines()
        return False, lines[-1] if lines else "error"


def grade(task, text, test_timeout):
    """Devuelve (ok, detalle)."""
    text = strip_think(text)
    kind = task["kind"]
    if kind == "code":
        code = extract_code(text)
        if code is None:
            return False, "sin bloque de código"
        return run_python(code + "\n\n# --- tests ---\n" + task["tests"], test_timeout)
    if kind == "answer":
        found = re.findall(r"RESPUESTA:\s*\**\s*(-?\d+)", text)
        if not found:
            return False, "sin línea RESPUESTA"
        return int(found[-1]) == task["expected"], f"dio {found[-1]}, esperado {task['expected']}"
    if kind == "json":
        i, j = text.find("{"), text.rfind("}")
        if i < 0 or j < i:
            return False, "sin JSON"
        try:
            obj = json.loads(text[i:j + 1])
        except json.JSONDecodeError:
            return False, "JSON inválido"
        ok = obj.get(task["expected_key"]) == task["expected_value"]
        return ok, f"{task['expected_key']}={obj.get(task['expected_key'])!r}"
    raise ValueError(kind)


# ------------------------------------------------------------------ selftest
def selftest(args):
    bad = 0
    for t in TASKS:
        ref = t["reference"]
        resp = f"```python\n{ref}\n```" if t["kind"] == "code" else ref
        ok_ref, d1 = grade(t, resp, args.test_timeout)
        ok_bad, _ = grade(t, "```python\ndef nada():\n    pass\n```" if t["kind"] == "code" else "no sé", args.test_timeout)
        status = "ok" if ok_ref and not ok_bad else "FALLO"
        if status != "ok":
            bad += 1
        print(f"{status:6} {t['id']:20} referencia_pasa={ok_ref} respuesta_mala_pasa={ok_bad} {d1 if not ok_ref else ''}")
    print("\nTodas las tareas son correctas." if not bad else f"\n{bad} tarea(s) mal definidas.")
    return 1 if bad else 0


# ------------------------------------------------------------------ ejecución
def load_models(path):
    if not os.path.exists(path):
        sys.exit(f"No encuentro {path}. Copia models.example.json a models.json y edítalo.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)["models"]


def run_model(cfg, tasks, args):
    rows = []
    for t in tasks:
        samples = []
        for s in range(args.samples):
            try:
                r = chat(cfg, t["prompt"], args.max_tokens, args.temperature, args.timeout)
                ok, detail = grade(t, r["content"], args.test_timeout)
                if r["finish"] == "length" and not ok:
                    detail = "cortado por max_tokens; " + detail
            except Exception as e:  # red, servidor caído, etc.
                r = {"content": "", "reasoning": "", "finish": "error", "tokens": 0, "elapsed": 0, "tps": 0}
                ok, detail = False, f"error: {e}"
            samples.append({"ok": ok, "detail": detail, **r})
            mark = "✓" if ok else "✗"
            print(f"  {cfg['name']:20} {t['id']:20} #{s + 1} {mark} {r['elapsed']:6.1f}s {r['tokens']:5d}tok  {'' if ok else detail}", flush=True)
        rows.append({"task": t["id"], "category": t["category"], "samples": samples})
    return rows


def summarize(name, rows, n):
    allsamples = [s for r in rows for s in r["samples"]]
    tasks = len(rows)
    p1 = sum(s["ok"] for s in allsamples) / max(1, len(allsamples))
    pn = sum(any(s["ok"] for s in r["samples"]) for r in rows) / max(1, tasks)
    ok_samples = [s for s in allsamples if s["elapsed"]]
    avg_t = sum(s["elapsed"] for s in ok_samples) / max(1, len(ok_samples))
    avg_tok = sum(s["tokens"] for s in ok_samples) / max(1, len(ok_samples))
    avg_tps = sum(s["tps"] for s in ok_samples) / max(1, len(ok_samples))
    cats = {}
    for r in rows:
        c = cats.setdefault(r["category"], [0, 0])
        c[0] += sum(s["ok"] for s in r["samples"])
        c[1] += len(r["samples"])
    return {"name": name, "pass1": p1, "passN": pn, "n": n, "avg_s": avg_t, "avg_tok": avg_tok,
            "avg_tps": avg_tps, "cats": {k: v[0] / v[1] for k, v in cats.items()}}


def markdown(summaries, rows_by_model, tasks):
    n = summaries[0]["n"]
    cats = sorted({c for s in summaries for c in s["cats"]})
    out = ["| modelo | pass@1 | pass@%d | %s | s/resp | tokens/resp | tok/s |" % (n, " | ".join(cats)),
           "|---|---|---|" + "---|" * len(cats) + "---|---|---|"]
    for s in summaries:
        out.append("| %s | %.0f%% | %.0f%% | %s | %.1f | %.0f | %.1f |" % (
            s["name"], 100 * s["pass1"], 100 * s["passN"],
            " | ".join("%.0f%%" % (100 * s["cats"].get(c, 0)) for c in cats),
            s["avg_s"], s["avg_tok"], s["avg_tps"]))
    out += ["", "| tarea | " + " | ".join(s["name"] for s in summaries) + " |", "|---|" + "---|" * len(summaries)]
    for t in tasks:
        cells = []
        for s in summaries:
            r = next(r for r in rows_by_model[s["name"]] if r["task"] == t["id"])
            cells.append("%d/%d" % (sum(x["ok"] for x in r["samples"]), len(r["samples"])))
        out.append(f"| {t['id']} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", default=os.path.join(HERE, "models.json"))
    ap.add_argument("--model", action="append", help="nombre del modelo a ejecutar (repetible); por defecto todos")
    ap.add_argument("--tasks", help="ids de tareas separados por coma")
    ap.add_argument("--category", help="codigo, modding o logica")
    ap.add_argument("--samples", type=int, default=1, help="intentos por tarea (da pass@N)")
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--temperature", type=float, default=0.6)
    ap.add_argument("--timeout", type=int, default=900, help="segundos por petición")
    ap.add_argument("--test-timeout", type=int, default=10, help="segundos para ejecutar los tests")
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    ap.add_argument("--selftest", action="store_true", help="comprueba las tareas sin ningún modelo")
    ap.add_argument("--list", action="store_true", help="lista las tareas")
    args = ap.parse_args()

    if args.list:
        for t in TASKS:
            print(f"{t['id']:20} {t['category']:8} {t['kind']}")
        return 0
    if args.selftest:
        return selftest(args)

    tasks = TASKS
    if args.tasks:
        ids = set(args.tasks.split(","))
        tasks = [t for t in tasks if t["id"] in ids]
    if args.category:
        tasks = [t for t in tasks if t["category"] == args.category]
    if not tasks:
        sys.exit("Ninguna tarea coincide con el filtro.")

    models = load_models(args.models)
    if args.model:
        models = [m for m in models if m["name"] in args.model]
    if not models:
        sys.exit("Ningún modelo coincide.")

    summaries, rows_by_model = [], {}
    for cfg in models:
        print(f"\n== {cfg['name']} ({cfg['base_url']}) ==")
        rows = run_model(cfg, tasks, args)
        rows_by_model[cfg["name"]] = rows
        summaries.append(summarize(cfg["name"], rows, args.samples))

    md = markdown(summaries, rows_by_model, tasks)
    print("\n" + md)
    os.makedirs(args.out, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(os.path.join(args.out, f"{stamp}.json"), "w", encoding="utf-8") as f:
        json.dump({"args": vars(args), "summaries": summaries, "rows": rows_by_model}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(args.out, f"{stamp}.md"), "w", encoding="utf-8") as f:
        f.write(md + "\n")
    print(f"\nGuardado en {args.out}/{stamp}.json y .md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
