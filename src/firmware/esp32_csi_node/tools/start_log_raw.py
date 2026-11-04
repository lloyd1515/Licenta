"""Reseteaza placa si arata TOT ce trimite, exact cum vine. Nu filtreaza nimic.
Utilizare:
  PY=~/.espressif/python_env/idf5.1_py3.14_env/bin/python
  $PY start_log_raw.py        # pana la Ctrl+C
  $PY start_log_raw.py 15     # 15 secunde"""
import sys
import time

import serial

PORT = "/dev/ttyUSB0"
BAUD = 115200


def main():
    limita = float(sys.argv[1]) if len(sys.argv) > 1 else None
    port = serial.Serial(PORT, BAUD, timeout=0.2)
    port.dtr = False
    port.rts = True
    time.sleep(0.1)
    port.rts = False
    start = time.time()
    try:
        while limita is None or time.time() - start < limita:
            brut = port.read(4096)
            if brut:
                sys.stdout.write(brut.decode("utf-8", "replace"))
                sys.stdout.flush()
    except KeyboardInterrupt:
        pass


main()
