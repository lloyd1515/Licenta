"""Compilează main.c pe PC (cu bibliotecile simulate), îl rulează în gdb și scrie assets/dbg-data.js.
Utilizare: python3 build_data.py"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN_DIR = HERE.parents[3] / "src" / "firmware" / "esp32_csi_node" / "main"
OUT = HERE.parent / "assets" / "dbg-data.js"
sys.path.insert(0, str(HERE))
from notes import NOTES  # noqa: E402

MAIN_LINES = (MAIN_DIR / "main.c").read_text(encoding="utf-8").splitlines()

DEBUGGERS = {
    "on_csi": dict(
        first="on_csi", last="on_csi", watch={"on_csi": ["info->len", "info->rx_ctrl.rssi", "info->buf[0]@8"]},
        scenarios=[
            ("normal", "Cadru normal (len = 128)", "on_csi_normal", "on_csi", ""),
            ("long", "Cadru prea lung (len = 200)", "on_csi_long", "on_csi", ""),
            ("empty", "Cadru gol (len = 0)", "on_csi_empty", "on_csi", ""),
            ("two", "Două cadre la rând", "on_csi_two", "on_csi", ""),
            ("full", "Coada este plină", "on_csi_full", "on_csi", ""),
        ]),
    "udp": dict(
        first="open_udp_socket", last="udp_sender_task", watch={"udp_sender_task": ["packet->seq", "packet->rssi_dbm"]},
        scenarios=[
            ("online", "Placa are adresă IP", "udp_online", "udp_sender_task", ""),
            ("offline", "Placa nu are adresă IP", "udp_offline", "udp_sender_task", ""),
        ]),
    "probe": dict(
        first="build_probe_request", last="probe_sender_task",
        watch={"build_probe_request": ["out[0]@64"], "probe_sender_task": ["probe[0]@64"]},
        scenarios=[("loop", "Două ture ale buclei de sondare", "probe", "probe_sender_task", "")]),
    "events": dict(
        first="on_wifi_event", last="on_wifi_event", watch={"on_wifi_event": ["event->ip_info.ip.addr"]},
        scenarios=[
            ("start", "Stația a pornit", "ev_start", "on_wifi_event", ""),
            ("gotip", "Am primit adresă IP", "ev_gotip", "on_wifi_event", ""),
            ("disc", "Conexiunea s-a pierdut", "ev_disc", "on_wifi_event", ""),
        ]),
    "init": dict(
        first="init_wifi", last="init_csi", watch={},
        scenarios=[
            ("wifi", "init_wifi", "init_wifi", "init_wifi", ""),
            ("csi", "init_csi", "init_csi", "init_csi", ""),
        ]),
    "boot": dict(
        first="start_tasks", last="app_main", watch={},
        scenarios=[("boot", "Pornirea plăcii", "boot", "app_main", "init_wifi();|init_csi();")]),
}

# Fragmente verbatim din main.c, fără mișcare: (început, sfârșit), ambele inclusiv, comparate după text fără spații la capete.
SNIPPETS = {
    "includes": [("#include <stdio.h>", '#include "lwip/sockets.h"')],
    "defs": [("#define TAG", "#define MAC_BYTES 6")],
    "packet": [("typedef struct __attribute__((packed)) {", "static uint16_t next_seq = 0;")],
    "bytes": [("#define FRAME_MAGIC", "#define FRAME_MAGIC 0xA55A"), ("typedef struct __attribute__((packed)) {", "} csi_packet_t;")],
    "lang": [("memset(&packet, 0, sizeof(packet));", "memset(&packet, 0, sizeof(packet));"),
             ("size_t copy_len", "memcpy(packet.csi_iq, info->buf, copy_len);")],
    "csi": [("wifi_csi_config_t csi_config = {", "ESP_ERROR_CHECK(esp_wifi_set_csi(true));")],
    "rssi": [("packet.rssi_dbm", "packet.rssi_dbm = info->rx_ctrl.rssi;")],
    "wifi": [("ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));", "ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));"),
             ("wifi_promiscuous_filter_t filter = {", "ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));")],
    "mac": [("static const uint8_t PROBE_FRAME_CONTROL", "static const uint8_t SOURCE_MAC"), ("static void build_probe_request", "}")],
    "seq": [("static uint16_t next_seq", "static uint16_t next_seq = 0;"), ("packet.timestamp_us", "packet.seq = next_seq++;")],
    "task": [("#define UDP_TASK_CORE", "#define WIFI_TASK_PRIORITY 5"), ("xTaskCreatePinnedToCore(udp_sender_task", "xTaskCreatePinnedToCore(probe_sender_task")],
    "isr": [("static void IRAM_ATTR on_csi", "static void IRAM_ATTR on_csi"), ("xRingbufferSendFromISR", "portYIELD_FROM_ISR();")],
    "queue": [("static RingbufHandle_t csi_queue", "static RingbufHandle_t csi_queue = NULL;"), ("xRingbufferSendFromISR", "xRingbufferSendFromISR"),
              ("csi_packet_t *packet = (csi_packet_t *)xRingbufferReceive", "csi_packet_t *packet = (csi_packet_t *)xRingbufferReceive"),
              ("vRingbufferReturnItem", "vRingbufferReturnItem"), ("csi_queue = xRingbufferCreate", "csi_queue = xRingbufferCreate")],
    "sendto": [("if (connected && sock >= 0) {", "}")],
    "flag": [("#define WIFI_CONNECTED_BIT", "#define WIFI_CONNECTED_BIT BIT0"), ("bool connected = xEventGroupGetBits", "bool connected = xEventGroupGetBits"),
             ("xEventGroupClearBits", "xEventGroupClearBits"), ("xEventGroupSetBits", "xEventGroupSetBits")],
}


def find(text, start=0):
    for i in range(start, len(MAIN_LINES)):
        if MAIN_LINES[i].strip().startswith(text):
            return i
    raise SystemExit("nu găsesc în main.c: " + text)


def fn_start(name):
    for i, ln in enumerate(MAIN_LINES):
        if ln and not ln[0].isspace() and (" " + name + "(") in ln and ln.rstrip().endswith("{"):
            return i
    raise SystemExit("funcție negăsită: " + name)


def fn_span(first, last):
    a, b = fn_start(first), fn_start(last)
    while MAIN_LINES[b] != "}":
        b += 1
    return a, b


def chunk_lines(ranges):
    rows = []
    for k, (s, e) in enumerate(ranges):
        a = find(s)
        b = a
        while MAIN_LINES[b].strip() != e and not (e == "}" and MAIN_LINES[b] == "}") and not MAIN_LINES[b].strip().startswith(e):
            b += 1
            if b >= len(MAIN_LINES):
                raise SystemExit("sfârșit negăsit: " + e)
        if k:
            rows.append(None)
        block = MAIN_LINES[a:b + 1]
        indent = min((len(x) - len(x.lstrip()) for x in block if x.strip()), default=0)
        for i, text in enumerate(block):
            rows.append((a + i + 1, text[indent:]))
    return rows


def pack(d):
    k = d["k"]
    if k == "int":
        return {"k": "i", "v": d["v"], "w": d["w"], "s": bool(d["s"])}
    if k == "struct":
        return {"k": "s", "f": [[n, pack(x)] for n, x in d["f"]]}
    if k == "bytes":
        return {"k": "b", "n": d["n"], "h": "".join("%02x" % x for x in d["v"]), "s": bool(d["s"])}
    if k == "ptr":
        return {"k": "p", "v": d["v"]}
    return {"k": "t", "v": d["v"]}


def run_trace(exe, key, sc, tmp):
    name, label, scenario, start, over = sc
    out = Path(tmp) / (scenario + ".json")
    env = dict(os.environ, SC=scenario, START=start, OVER=over, OUT=str(out), WATCH=json.dumps(DEBUGGERS[key]["watch"]))
    r = subprocess.run(["gdb", "-batch", "-x", str(HERE / "trace.py"), "--args", str(exe), scenario], env=env, capture_output=True, text=True)
    if not out.exists():
        raise SystemExit("gdb a eșuat pentru %s:\n%s\n%s" % (scenario, r.stdout[-800:], r.stderr[-800:]))
    return json.loads(out.read_text(encoding="utf-8"))["steps"]


def main():
    with tempfile.TemporaryDirectory() as tmp:
        stub_o, exe = Path(tmp) / "stub_idf.o", Path(tmp) / "csi_dbg"
        inc = ["-I", str(HERE / "stub")]
        subprocess.run(["gcc", "-O0", "-c", "-Wall", *inc, "-o", str(stub_o), str(HERE / "stub" / "stub_idf.c")], check=True)
        subprocess.run(["gcc", "-O0", "-g", "-Wall", "-Wno-unused-function", *inc, "-I", str(MAIN_DIR), "-o", str(exe), str(HERE / "driver.c"), str(stub_o)], check=True)

        layout_c = Path(tmp) / "layout.c"
        layout_c.write_text('#include <stddef.h>\n#include "main.c"\nint main(void){printf("%zu %zu %zu %zu %zu %zu",sizeof(csi_packet_t),offsetof(csi_packet_t,magic),offsetof(csi_packet_t,node_id),offsetof(csi_packet_t,rssi_dbm),offsetof(csi_packet_t,timestamp_us),offsetof(csi_packet_t,seq));printf(" %zu",offsetof(csi_packet_t,csi_iq));return 0;}\n')
        lay = Path(tmp) / "layout"
        subprocess.run(["gcc", "-O0", "-Wno-unused-function", *inc, "-I", str(MAIN_DIR), "-o", str(lay), str(layout_c), str(stub_o)], check=True)
        nums = [int(x) for x in subprocess.run([str(lay)], capture_output=True, text=True, check=True).stdout.split()]
        layout = dict(zip(["size", "magic", "node_id", "rssi_dbm", "timestamp_us", "seq", "csi_iq"], nums))

        data = {"debuggers": {}, "snippets": {}, "layout": layout}
        missing = set()
        for key, cfg in DEBUGGERS.items():
            a, b = fn_span(cfg["first"], cfg["last"])
            code = MAIN_LINES[a:b + 1]
            notes = []
            for ln in code:
                t = ln.strip()
                notes.append(NOTES.get(t, ""))
                if t and t not in ("}", "};", "} else {", "},") and t not in NOTES:
                    missing.add(t)
            scs = []
            for sc in cfg["scenarios"]:
                steps = []
                for s in run_trace(exe, key, sc, tmp):
                    if s.get("end"):
                        steps.append({"end": True, "ev": s["ev"], "g": s["g"]})
                        continue
                    rel = s["l"] - (a + 1) + 1
                    if not 1 <= rel <= len(code):
                        raise SystemExit("linie în afara regiunii %s: %s (%s)" % (key, s["l"], s["fn"]))
                    steps.append({"l": rel, "fn": s["fn"], "st": s["stack"], "ev": s["ev"], "g": s["g"],
                                  "v": [{"n": v["n"], "a": v["arg"], "j": v["junk"], "d": pack(v["d"])} for v in s["vars"]],
                                  "w": [{"n": w["n"], "d": pack(w["d"])} for w in s["watch"]]})
                scs.append({"id": sc[0], "label": sc[1], "steps": steps})
            data["debuggers"][key] = {"code": code, "notes": notes, "scenarios": scs}
        for key, ranges in SNIPPETS.items():
            rows = chunk_lines(ranges)
            code, notes = [], []
            for r in rows:
                if r is None:
                    code.append(None)
                    notes.append("")
                    continue
                code.append(r[1])
                t = r[1].strip()
                notes.append(NOTES.get(t, ""))
                if t and t not in ("}", "};", "} else {", "},") and t not in NOTES:
                    missing.add(t)
            data["snippets"][key] = {"code": code, "notes": notes}
        if missing:
            print("LIPSESC NOTE pentru:")
            for m in sorted(missing):
                print("  ", m)
    js = "/* Generat de debug-harness/build_data.py din main.c rulat în gdb. Nu edita manual. */\nwindow.DBG = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    OUT.write_text(js, encoding="utf-8")
    print("scris", OUT, len(js), "octeți; pași:", {k: [len(s["steps"]) for s in v["scenarios"]] for k, v in data["debuggers"].items()})


if __name__ == "__main__":
    main()
