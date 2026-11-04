"""Reseteaza placa si arata jurnalul simplificat si colorat.
Ascunde zgomotul (ROM, bootloader, memorie) si liniile stricate.
Pentru tot jurnalul, folositi start_log_raw.py.
Utilizare:
  PY=~/.espressif/python_env/idf5.1_py3.14_env/bin/python
  $PY start_log.py        # pana la Ctrl+C
  $PY start_log.py 15     # 15 secunde"""
import os
import re
import sys
import time

import serial

PORT = "/dev/ttyUSB0"
BAUD = 115200
LINE = re.compile(r"^([IWE]) \((\d+)\) ([\w.-]+): ?(.*)$")
INCEPUT_LINIE = re.compile(r"[IWE] \(\d+\) ")
ANSI = re.compile(r"\x1b\[[0-9;]*m")
TAGS_ASCUNSE = {"boot", "boot.esp32", "esp_image", "cpu_start", "heap_init", "spi_flash",
                "app_start", "phy_init", "wifi_init"}
WIFI_UTILE = ("mode :", "state:", "connected with", "security:")
COLOR = sys.stdout.isatty() or "FORCE_COLOR" in os.environ
GRI, VERDE, GALBEN, ROSU, CYAN, RESET = "90", "92", "93", "91", "96", "0"


def vopsea(cod, text):
    return "\x1b[%sm%s\x1b[0m" % (cod, text) if COLOR else text


def stricata(linie):
    return "�" in linie or any(ord(c) < 32 and c != "\t" for c in linie) \
        or len(INCEPUT_LINIE.findall(linie)) > 1


def util(nivel, tag, text):
    if nivel in "WE":
        return not (tag == "spi_flash" or "Password length" in text)
    if tag in TAGS_ASCUNSE:
        return False
    if tag == "wifi":
        return text.startswith(WIFI_UTILE)
    return True


def formateaza(nivel, ms, tag, text):
    culoare = {"W": GALBEN, "E": ROSU}.get(nivel) or (VERDE if tag == "CSI_NODE" else CYAN if tag == "wifi" else RESET)
    timp = vopsea(GRI, "%7.2f s" % (int(ms) / 1000))
    return "%s %s  %s %s" % (vopsea(culoare, nivel), timp, vopsea(culoare, "%-9s" % tag), vopsea(culoare, text))


def main():
    limita = float(sys.argv[1]) if len(sys.argv) > 1 else None
    port = serial.Serial(PORT, BAUD, timeout=0.2)
    port.dtr = False
    port.rts = True
    time.sleep(0.1)
    port.rts = False
    start = time.time()
    buf = b""
    try:
        while limita is None or time.time() - start < limita:
            buf += port.read(4096)
            while b"\n" in buf:
                brut, buf = buf.split(b"\n", 1)
                linie = ANSI.sub("", brut.decode("utf-8", "replace").rstrip())
                m = LINE.match(linie)
                if m and not stricata(linie) and util(m[1], m[3], m[4]):
                    print(formateaza(m[1], m[2], m[3], m[4]), flush=True)
    except KeyboardInterrupt:
        pass


main()
