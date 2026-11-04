"""Rulat în gdb: execută un scenariu linie cu linie și salvează starea la fiecare oprire, ca JSON.
Variabile de mediu: SC (nume scenariu), START (funcția de oprire), OVER (fragmente de linii care se sar cu `next`), OUT (fișier JSON), WATCH (JSON: funcție -> expresii)."""
import json
import os
import gdb

SC, START, OUT = os.environ["SC"], os.environ["START"], os.environ["OUT"]
OVER = [o for o in os.environ.get("OVER", "").split("|") if o]
WATCH = json.loads(os.environ.get("WATCH", "{}"))
GLOBALS = ["next_seq", "stub_ring_items", "stub_ring_bytes", "stub_event_bits", "stub_sock_open"]
inf = None
src_cache = {}


def src_line(sal):
    path = sal.symtab.fullname()
    if path not in src_cache:
        src_cache[path] = open(path, encoding="utf-8").read().splitlines()
    return src_cache[path][sal.line - 1]


def raw_bytes(val):
    return bytes(inf.read_memory(val.address, val.type.sizeof))


def fmt(val):
    t = val.type.strip_typedefs()
    c = t.code
    if c in (gdb.TYPE_CODE_INT, gdb.TYPE_CODE_BOOL, gdb.TYPE_CODE_ENUM, gdb.TYPE_CODE_CHAR):
        return {"k": "int", "v": int(val), "w": t.sizeof * 8, "s": t.is_signed if hasattr(t, "is_signed") else int(gdb.parse_and_eval("(%s)-1" % t.name) < 0) if t.name else True}
    if c == gdb.TYPE_CODE_STRUCT:
        return {"k": "struct", "f": [[f.name, fmt(val[f.name])] for f in t.fields() if f.name]}
    if c == gdb.TYPE_CODE_ARRAY:
        lo, hi = t.range()
        n = hi - lo + 1
        el = t.target().strip_typedefs()
        if el.sizeof == 1:
            data = [int(val[i]) for i in range(min(n, 128))]
            signed = bool(int(gdb.parse_and_eval("(%s)-1" % el.name) < 0)) if el.name else False
            return {"k": "bytes", "n": n, "v": [x & 0xFF for x in data], "s": signed}
        return {"k": "text", "v": str(val)}
    if c == gdb.TYPE_CODE_PTR:
        if int(val) == 0:
            return {"k": "ptr", "v": "NULL"}
        if t.target().strip_typedefs().code in (gdb.TYPE_CODE_INT, gdb.TYPE_CODE_CHAR) and t.target().strip_typedefs().sizeof == 1 and "char" in str(t.target()):
            try:
                return {"k": "text", "v": '"%s"' % val.string()}
            except gdb.error:
                pass
        return {"k": "ptr", "v": "→ " + str(t.target())}
    return {"k": "text", "v": str(val)}


def is_junk(val):
    try:
        return all(b == 0xCD for b in raw_bytes(val))
    except Exception:
        return False


def locals_of(frame, cur_line):
    out, seen = [], set()
    try:
        block = frame.block()
    except RuntimeError:
        return out
    while block is not None:
        for sym in block:
            if not (sym.is_variable or sym.is_argument) or sym.name in seen or sym.name.endswith("_"):
                continue
            if sym.is_variable and sym.line >= cur_line:
                continue
            seen.add(sym.name)
            val = sym.value(frame)
            out.append({"n": sym.name, "arg": bool(sym.is_argument), "junk": (not sym.is_argument) and is_junk(val), "d": fmt(val)})
        if block.function is not None:
            break
        block = block.superblock
    return out


def watch_of(frame, fn):
    out = []
    for expr in WATCH.get(fn, []):
        try:
            out.append({"n": expr, "d": fmt(gdb.parse_and_eval(expr))})
        except gdb.error:
            pass
    return out


def log_lines():
    n = int(gdb.parse_and_eval("*(unsigned *)&stub_log_len"))
    if n == 0:
        return []
    return bytes(inf.read_memory(gdb.parse_and_eval("(char *)&stub_log_buf"), n)).decode("utf-8").splitlines()


def globals_now():
    return {g: int(gdb.parse_and_eval("*(int *)&" + g)) & 0xFFFFFFFF if g == "stub_event_bits" else int(gdb.parse_and_eval("*(int *)&" + g)) for g in GLOBALS}


gdb.execute("set pagination off")
gdb.execute("set confirm off")
gdb.execute("set print frame-arguments none")
gdb.execute("break " + START)
gdb.execute("break stub_end_scenario")
gdb.execute("run", to_string=True)
inf = gdb.selected_inferior()
steps, seen_log = [], 0
for _ in range(3000):
    frame = gdb.selected_frame()
    name = frame.name()
    sal = frame.find_sal()
    new_log = log_lines()[seen_log:]
    seen_log += len(new_log)
    if name == "stub_end_scenario":
        steps.append({"end": True, "ev": new_log, "g": globals_now()})
        break
    in_main = sal.symtab is not None and sal.symtab.filename.endswith("main.c")
    if name == "main":
        steps.append({"end": True, "ev": new_log, "g": globals_now()})
        break
    if in_main:
        stack, f = [], frame
        while f is not None and f.find_sal().symtab is not None and f.find_sal().symtab.filename.endswith("main.c"):
            stack.append(f.name())
            f = f.older()
        steps.append({"l": sal.line, "fn": name, "stack": stack, "vars": locals_of(frame, sal.line), "watch": watch_of(frame, name), "ev": new_log, "g": globals_now()})
        text = src_line(sal)
        gdb.execute("next" if any(o in text for o in OVER) else "step", to_string=True)
    else:
        gdb.execute("step", to_string=True)
json.dump({"scenario": SC, "steps": steps}, open(OUT, "w"), ensure_ascii=False)
gdb.execute("kill")
gdb.execute("quit")
