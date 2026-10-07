"""Tareas del benchmark.

Cada tarea es un dict con:
  id, category, kind ("code" | "answer" | "json"), prompt
  code   -> tests (código Python con asserts que se añade al final de la solución)
  answer -> expected (int), el modelo debe terminar con "RESPUESTA: <número>"
  json   -> expected_key/expected_value sobre el JSON que devuelve el modelo
  reference -> respuesta correcta conocida (solo para --selftest)
"""

GAME_API = """\
API del juego (el objeto `game` se pasa a tu función; no hay nada más):
- game.on(event_name: str, callback)   registra un callback.
    Eventos: "player_join"  -> callback(player)
             "block_break"  -> callback(player, block)
- player.name: str
- player.give(item_id: str, count: int = 1)
- player.send_message(text: str)
- block.id: str
"""

TASKS = []


def task(**kw):
    TASKS.append(kw)


# ---------------------------------------------------------------- código
task(
    id="parse_config", category="codigo", kind="code",
    prompt="""Escribe en Python una función `parse_config(text: str) -> dict`.
Reglas:
- Cada línea tiene la forma `clave = valor`; solo cuenta el primer `=`.
- Se ignoran líneas vacías, líneas sin `=` y líneas que (tras recortar espacios) empiezan por `#`.
- Se recortan los espacios de clave y valor.
- Si el valor es un entero (`42`, `-7`) se convierte a int; `true`/`false` (cualquier mayúscula) a bool; el resto queda como str.
- Si una clave se repite gana la última.
Devuelve solo el código en un bloque ```python.""",
    tests='''
assert parse_config("a=1\\n b = hello \\n  # c=3\\n\\nd=TRUE\\ne=false\\na=-7\\nnoeq\\nurl=http://x?a=b") == {"a": -7, "b": "hello", "d": True, "e": False, "url": "http://x?a=b"}
assert parse_config("") == {}
assert parse_config("x = 3.5") == {"x": "3.5"}
''',
    reference='''
def parse_config(text):
    out = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        k, v = k.strip(), v.strip()
        if v.lower() == "true":
            val = True
        elif v.lower() == "false":
            val = False
        else:
            try:
                val = int(v)
            except ValueError:
                val = v
        out[k] = val
    return out
''',
)

task(
    id="lru_cache", category="codigo", kind="code",
    prompt="""Escribe en Python una clase `LRUCache(capacity)` con `get(key)` (devuelve el valor o -1) y `put(key, value)`.
Al superar la capacidad se expulsa la clave menos usada recientemente. Tanto `get` como `put` (también al actualizar una clave existente) cuentan como uso.
Devuelve solo el código en un bloque ```python.""",
    tests='''
c = LRUCache(2); c.put(1, 1); c.put(2, 2)
assert c.get(1) == 1
c.put(3, 3)
assert c.get(2) == -1
c.put(4, 4)
assert c.get(1) == -1 and c.get(3) == 3 and c.get(4) == 4
c = LRUCache(2); c.put(1, 1); c.put(2, 2); c.put(1, 10); c.put(3, 3)
assert c.get(2) == -1 and c.get(1) == 10
c = LRUCache(1); c.put(1, 1); c.put(2, 2)
assert c.get(1) == -1 and c.get(2) == 2
''',
    reference='''
from collections import OrderedDict
class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.d = OrderedDict()
    def get(self, key):
        if key not in self.d:
            return -1
        self.d.move_to_end(key)
        return self.d[key]
    def put(self, key, value):
        self.d[key] = value
        self.d.move_to_end(key)
        if len(self.d) > self.cap:
            self.d.popitem(last=False)
''',
)

task(
    id="fix_binary_search", category="codigo", kind="code",
    prompt="""Esta función tiene errores (se cuelga o no encuentra algunos elementos). Corrígela y devuelve la función completa en un bloque ```python.

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid
        else:
            hi = mid - 1
    return -1
```""",
    tests='''
arr = list(range(0, 100, 3))
for i, v in enumerate(arr):
    assert binary_search(arr, v) == i
assert binary_search(arr, 1) == -1
assert binary_search(arr, 100) == -1
assert binary_search([], 5) == -1
assert binary_search([5], 5) == 0
assert binary_search([5], 4) == -1
assert binary_search([5], 6) == -1
''',
    reference='''
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
''',
)

task(
    id="merge_intervals", category="codigo", kind="code",
    prompt="""Escribe en Python `merge_intervals(intervals)` que recibe una lista de tuplas `(inicio, fin)` sin ordenar y devuelve la lista de tuplas fusionadas y ordenadas.
Los intervalos que se solapan o se tocan (el fin de uno es el inicio de otro) se fusionan. No modifiques la lista de entrada.
Devuelve solo el código en un bloque ```python.""",
    tests='''
assert merge_intervals([(1, 3), (2, 6), (8, 10), (15, 18)]) == [(1, 6), (8, 10), (15, 18)]
assert merge_intervals([(1, 4), (4, 5)]) == [(1, 5)]
assert merge_intervals([]) == []
assert merge_intervals([(5, 6), (1, 2)]) == [(1, 2), (5, 6)]
assert merge_intervals([(1, 10), (2, 3)]) == [(1, 10)]
orig = [(5, 6), (1, 2)]
merge_intervals(orig)
assert orig == [(5, 6), (1, 2)]
''',
    reference='''
def merge_intervals(intervals):
    out = []
    for a, b in sorted(intervals):
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out
''',
)

# ---------------------------------------------------------------- modding
task(
    id="inventory_stacks", category="modding", kind="code",
    prompt="""Escribe en Python una clase `Inventory(slots, max_stack=64)` para un juego.
- `add(item, count)` añade objetos: primero rellena los stacks existentes del mismo objeto (en orden), luego usa huecos vacíos. Devuelve cuántos objetos NO cupieron.
- `count(item)` devuelve el total de ese objeto.
Cada hueco guarda un solo tipo de objeto, hasta `max_stack`.
Devuelve solo el código en un bloque ```python.""",
    tests='''
inv = Inventory(2, 64)
assert inv.add("stone", 100) == 0
assert inv.count("stone") == 100
assert inv.add("stone", 50) == 22
assert inv.count("stone") == 128
assert inv.add("dirt", 1) == 1
inv = Inventory(3, 10)
inv.add("a", 5); inv.add("b", 5)
assert inv.add("a", 8) == 0
assert inv.count("a") == 13
assert inv.add("b", 20) == 15
assert inv.count("b") == 10
''',
    reference='''
class Inventory:
    def __init__(self, slots, max_stack=64):
        self.n = slots
        self.max = max_stack
        self.stacks = []
    def add(self, item, count):
        for s in self.stacks:
            if s[0] == item and count:
                put = min(self.max - s[1], count)
                s[1] += put
                count -= put
        while count and len(self.stacks) < self.n:
            put = min(self.max, count)
            self.stacks.append([item, put])
            count -= put
        return count
    def count(self, item):
        return sum(s[1] for s in self.stacks if s[0] == item)
''',
)

task(
    id="event_bus", category="modding", kind="code",
    prompt="""Escribe en Python una clase `EventBus` para un sistema de mods:
- `on(event, callback, priority=0)` registra un callback.
- `off(event, callback)` lo quita.
- `emit(event, *args)` llama a los callbacks de ese evento por prioridad descendente (a igual prioridad, en orden de registro) pasándoles `*args`. Si un callback devuelve el string `"cancel"`, se detiene la cadena y `emit` devuelve False; si no, devuelve True. Un evento sin callbacks devuelve True.
Devuelve solo el código en un bloque ```python.""",
    tests='''
bus = EventBus(); log = []
bus.on("x", lambda: log.append("a"))
bus.on("x", lambda: log.append("hi"), priority=5)
bus.on("x", lambda: log.append("b"))
assert bus.emit("x") is True and log == ["hi", "a", "b"]
log.clear()
def cancel():
    log.append("c")
    return "cancel"
bus.on("x", cancel, priority=1)
assert bus.emit("x") is False and log == ["hi", "c"]
bus.off("x", cancel); log.clear()
assert bus.emit("x") is True and log == ["hi", "a", "b"]
assert bus.emit("none") is True
bus.on("y", lambda v: log.append(v)); log.clear()
bus.emit("y", 7)
assert log == [7]
''',
    reference='''
class EventBus:
    def __init__(self):
        self.h = {}
        self.seq = 0
    def on(self, event, callback, priority=0):
        self.seq += 1
        self.h.setdefault(event, []).append((priority, self.seq, callback))
    def off(self, event, callback):
        self.h[event] = [t for t in self.h.get(event, []) if t[2] != callback]
    def emit(self, event, *args):
        for _, _, cb in sorted(self.h.get(event, []), key=lambda t: (-t[0], t[1])):
            if cb(*args) == "cancel":
                return False
        return True
''',
)

task(
    id="follow_api_docs", category="modding", kind="code",
    prompt=GAME_API + """
Escribe `install(game)` que:
- cuando un jugador entra, le envía el mensaje `Bienvenido, <nombre>!` y le da 1 "bread";
- cuando un jugador rompe un bloque con id "diamond_ore", le da 2 "diamond" y le envía `¡Diamantes!`; otros bloques no hacen nada.
Usa SOLO la API documentada. Devuelve solo el código en un bloque ```python.""",
    tests='''
class FakePlayer:
    def __init__(self, name):
        self.name = name; self.items = []; self.messages = []
    def give(self, item_id, count=1):
        self.items.append((item_id, count))
    def send_message(self, text):
        self.messages.append(text)

class FakeBlock:
    def __init__(self, id):
        self.id = id

class FakeGame:
    def __init__(self):
        self.h = {}
    def on(self, event, callback):
        self.h.setdefault(event, []).append(callback)
    def fire(self, event, *args):
        for cb in self.h.get(event, []):
            cb(*args)

g = FakeGame(); install(g)
p = FakePlayer("Ana")
g.fire("player_join", p)
assert p.messages == ["Bienvenido, Ana!"] and p.items == [("bread", 1)]
g.fire("block_break", p, FakeBlock("diamond_ore"))
assert ("diamond", 2) in p.items and p.messages[-1] == "¡Diamantes!"
n = len(p.items)
g.fire("block_break", p, FakeBlock("stone"))
assert len(p.items) == n and len(p.messages) == 2
''',
    reference='''
def install(game):
    def join(player):
        player.send_message(f"Bienvenido, {player.name}!")
        player.give("bread", 1)
    def brk(player, block):
        if block.id == "diamond_ore":
            player.give("diamond", 2)
            player.send_message("¡Diamantes!")
    game.on("player_join", join)
    game.on("block_break", brk)
''',
)

task(
    id="no_invent_api", category="modding", kind="json",
    prompt=GAME_API + """
Quiero que cuando un jugador entre, el clima pase a ser despejado usando `game.set_weather("clear")`.
Comprueba la API documentada. Responde SOLO con JSON, sin texto extra:
- si la API documentada NO permite hacerlo: {"possible": false, "reason": "..."}
- si sí se puede: {"possible": true, "code": "..."}""",
    expected_key="possible", expected_value=False,
    reference='{"possible": false, "reason": "set_weather no esta en la API"}',
)

# ---------------------------------------------------------------- lógica
task(
    id="bird_trains", category="logica", kind="answer",
    prompt="""Dos trenes están a 300 km de distancia y se acercan en línea recta, uno a 60 km/h y el otro a 90 km/h. Un pájaro vuela a 120 km/h de un tren al otro y de vuelta, sin parar, hasta que los trenes se cruzan. ¿Cuántos km recorre el pájaro?
Razona y termina con una línea `RESPUESTA: <número>`.""",
    expected=240, reference="RESPUESTA: 240",
)

task(
    id="water_jugs", category="logica", kind="answer",
    prompt="""Tienes una jarra de 3 litros y otra de 5 litros, sin marcas, y agua ilimitada. Cada acción (llenar una jarra, vaciar una jarra o verter de una a otra hasta que una se llene o la otra se vacíe) cuenta como un paso. ¿Cuál es el número MÍNIMO de pasos para tener exactamente 4 litros en la jarra de 5?
Razona y termina con una línea `RESPUESTA: <número>`.""",
    expected=6, reference="RESPUESTA: 6",
)

task(
    id="clock_hands", category="logica", kind="answer",
    prompt="""En un reloj analógico de 12 horas, ¿cuántas veces se superponen la aguja de la hora y la del minuto en un día completo de 24 horas (de las 00:00 incluida a las 24:00 sin incluir)?
Razona y termina con una línea `RESPUESTA: <número>`.""",
    expected=22, reference="RESPUESTA: 22",
)

task(
    id="count_divisible", category="logica", kind="answer",
    prompt="""¿Cuántos enteros entre 1 y 1000 (ambos incluidos) son divisibles por 3 o por 5, pero NO por 15?
Razona y termina con una línea `RESPUESTA: <número>`.""",
    expected=401, reference="RESPUESTA: 401",
)
