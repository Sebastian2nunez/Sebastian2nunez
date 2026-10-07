# ai-bench

Mini benchmark para comparar modelos locales de IA (Bonsai 2 27B, Qwen3 Coder 30B…) en **programación, modding y lógica**.
Sin dependencias: solo Python 3.8+ y un servidor compatible con OpenAI (`llama-server` de llama.cpp sirve).

> ⚠️ El benchmark **ejecuta el código que escribe el modelo** para corregirlo. Úsalo en un contenedor o VM si no te fías.

## Qué mide
12 tareas, corrección automática (nada de "a ojo"):

| categoría | tareas |
|---|---|
| `codigo` | `parse_config`, `lru_cache`, `fix_binary_search`, `merge_intervals` |
| `modding` | `inventory_stacks`, `event_bus`, `follow_api_docs` (usar una API documentada), `no_invent_api` (decir "no existe" en vez de inventarla) |
| `logica` | 4 problemas con respuesta numérica exacta |

Por modelo saca: **pass@1** (acierto medio), **pass@N** (acierta alguna de N muestras: mide lo que ganas generando varias respuestas y verificando), segundos y tokens por respuesta, tok/s.

## Uso
```bash
cp models.example.json models.json     # edita nombres y puertos
python3 bench.py --selftest            # comprueba que las tareas están bien (no necesita modelo)
python3 bench.py --list                # lista las tareas

# un modelo cada vez (con 8 GB de VRAM, un solo servidor a la vez):
llama-server -m bonsai.gguf -ngl 99 -c 16384 -fa on --jinja --port 8080
python3 bench.py --model bonsai-2-27b

# luego cambia de servidor/puerto y ejecuta el otro:
python3 bench.py --model qwen3-coder-30b
```

Opciones útiles:
- `--samples 4` → 4 intentos por tarea (da pass@4). Más lento, pero muestra cuánto ayuda el muestreo múltiple.
- `--category modding` / `--tasks event_bus,lru_cache` → solo algunas tareas.
- `--max-tokens 16384` si el modelo piensa mucho y se corta (aparece como "cortado por max_tokens").
- `"extra"` en `models.json` se mezcla en la petición, p. ej. `{"chat_template_kwargs": {"enable_thinking": false}}` para desactivar el pensamiento si tu plantilla lo admite.

Cada ejecución guarda `results/<fecha>.json` (con las respuestas completas, para revisar fallos) y `.md` (tabla resumen). Ambos quedan fuera de git.

## Añadir tus propias tareas (por ejemplo de tu juego)
Edita `tasks.py` y añade un `task(...)` con prompt, `tests` (asserts que se pegan al final del código del modelo) y una `reference` correcta. Luego `python3 bench.py --selftest` valida que los tests aceptan la referencia y rechazan una respuesta vacía.
La tarea `follow_api_docs` es la plantilla: cambia la API ficticia por la de tu juego y pon fakes en los tests.

## Limitaciones
- Son pruebas de una sola respuesta. No miden el bucle de agente de Cline u OpenCode (editar ficheros, compilar, corregir). Para eso, haz también una prueba manual con una tarea tuya en cada herramienta.
- 12 tareas dan una idea, no una clasificación definitiva: con `--samples` mayor y tareas propias se afina.
