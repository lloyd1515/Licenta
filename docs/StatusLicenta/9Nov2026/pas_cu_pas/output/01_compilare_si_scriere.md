# 01 – Compilare și scriere pe placă

Comanda (9 Nov 2026):

```bash
idf.py -B ~/esp/pas-cu-pas -DSDKCONFIG=~/esp/pas-cu-pas-sdkconfig -b 115200 -p /dev/ttyUSB0 build flash
```

`ruleaza.sh` rulează aceeași comandă, plus `monitor` la final.

Liniile marcate sunt importante. Explicațiile sunt sub output.

<pre>
Executing action: all (aliases: build)
Running ninja in directory /home/vlads4r4/esp/pas-cu-pas
Executing "ninja all"...
[1/4] cd /home/vlads4r4/esp/pas-cu-pas/esp-idf/esptool_py && .../check_sizes.py --offset 0x8000 partition --type app .../partition-table.bin .../pas_cu_pas.bin
<mark>pas_cu_pas.bin binary size 0x95c20 bytes. Smallest app partition is 0x100000 bytes. 0x6a3e0 bytes (42%) free.</mark>  [1]
[2/4] Performing build step for 'bootloader'
[1/1] cd .../bootloader/esp-idf/esptool_py && .../check_sizes.py --offset 0x8000 bootloader 0x1000 .../bootloader.bin
<mark>Bootloader binary size 0x68b0 bytes. 0x750 bytes (7%) free.</mark>  [2]
[3/4] No install step for 'bootloader'
[4/4] Completed 'bootloader'
<mark>Executing action: flash</mark>  [3]
Running ninja in directory /home/vlads4r4/esp/pas-cu-pas
Executing "ninja flash"...
[1/5] ... (aceleași verificări de mărime ca mai sus)
[4/5] cd .../esptool_py && .../cmake ... -P .../run_serial_tool.cmake
<mark>esptool.py --chip esp32 -p /dev/ttyUSB0 -b 115200 ... write_flash ... 0x1000 bootloader/bootloader.bin 0x10000 pas_cu_pas.bin 0x8000 partition_table/partition-table.bin</mark>  [4]
esptool.py v4.13.0
Serial port /dev/ttyUSB0
<mark>Connecting....</mark>  [5]
<mark>Chip is ESP32-D0WDQ6 (revision v1.1)</mark>  [6]
Features: WiFi, BT, Dual Core, 240MHz, VRef calibration in efuse, Coding Scheme None
<mark>Crystal is 40MHz</mark>  [7]
<mark>MAC: fc:e8:c0:e1:1e:d0</mark>  [8]
Uploading stub...
Running stub...
Stub running...
Configuring flash size...
Flash will be erased from 0x00001000 to 0x00007fff...
Flash will be erased from 0x00010000 to 0x000a5fff...
Flash will be erased from 0x00008000 to 0x00008fff...
SHA digest in image updated
Compressed 26800 bytes to 16793...
Writing at 0x00001000... (50 %)
Writing at 0x000076a8... (100 %)
Wrote 26800 bytes (16793 compressed) at 0x00001000 in 1.8 seconds (effective 119.8 kbit/s)...
<mark>Hash of data verified.</mark>  [9]
Compressed 613408 bytes to 393622...
Writing at 0x00010000... (4 %)
... (liniile 8 % ... 96 % sunt omise)
Writing at 0x000a5a2f... (100 %)
<mark>Wrote 613408 bytes (393622 compressed) at 0x00010000 in 34.7 seconds (effective 141.6 kbit/s)...</mark>  [10]
Hash of data verified.
Compressed 3072 bytes to 103...
Writing at 0x00008000... (100 %)
Wrote 3072 bytes (103 compressed) at 0x00008000 in 0.1 seconds (effective 333.6 kbit/s)...
Hash of data verified.

Leaving...
<mark>Hard resetting via RTS pin...</mark>  [11]
Done
</pre>

## Explicații

1. Programul nostru are 613 KB. Partiția pentru program are 1 MB. Rămâne 42 % liber.
2. Bootloader-ul este programul mic care pornește primul și încarcă aplicația noastră.
3. Compilarea s-a terminat. Acum începe scrierea pe placă.
4. `esptool.py` scrie trei fișiere, la trei adrese din memoria flash.
5. PC-ul resetează placa în modul de programare și așteaptă răspunsul ei.
6. Modelul exact al chipului de pe placă: ESP32, revizia v1.1.
7. Cristalul este corect, 40 MHz. La eroarea de la 460800 baud, valoarea era greșită.
8. Adresa MAC a plăcii. Ea apare și în jurnalul Wi-Fi.
9. Placa a verificat datele scrise. Datele sunt corecte.
10. Aplicația noastră, la adresa `0x10000`. Scrierea durează 35 s la 115200 baud.
11. PC-ul repornește placa. Placa rulează acum programul nou.

## Notă

Prima încercare de scriere a eșuat la 16 %, cu `The chip stopped responding`. A doua încercare a reușit. Legătura USB nu este complet stabilă.
