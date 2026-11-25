import sys
import time

import serial

# Port serial si viteza
PORT = "/dev/ttyUSB0"
BAUD = 115200


# Reseteaza placa, arata tot
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
