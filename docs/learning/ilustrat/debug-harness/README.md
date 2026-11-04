# debug-harness

Rulează `src/firmware/esp32_csi_node/main/main.c` (nemodificat) pe PC, linie cu linie, și produce `../assets/dbg-data.js` pentru depanatorul din pagina `main.c.html`.

- `stub/` — definiții minime ESP-IDF și implementări simulate (coadă, steaguri, socket-uri, Wi-Fi). Structurile Wi-Fi vin din ESP-IDF 5.1, ținta ESP32.
- `driver.c` — include `main.c` și rulează scenariile (cadru CSI normal, coadă plină, placă fără IP și altele).
- `trace.py` — script gdb: execută pas cu pas și salvează variabilele, efectele și starea sistemului.
- `notes.py` — explicația fiecărei linii de cod.
- `build_data.py` — compilează, rulează gdb pentru fiecare scenariu și scrie datele.

Utilizare: `python3 build_data.py` (necesită `gcc` și `gdb` cu Python). Rulează din nou după orice schimbare în `main.c` sau în `notes.py`.

Ce este real: execuția codului din main.c și valorile variabilelor. Ce este simulat: radioul, rețeaua, FreeRTOS, coada circulară (model aproximativ: 8 octeți de antet, aliniere la 4 octeți) și ceasul.
