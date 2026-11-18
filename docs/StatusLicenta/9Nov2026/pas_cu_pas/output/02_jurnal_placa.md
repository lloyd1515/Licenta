# 02 – Jurnalul plăcii (pasul 1)

Comanda (9 Nov 2026), 15 secunde de jurnal complet:

```bash
~/.espressif/python_env/idf5.1_py3.14_env/bin/python ~/dev/Licenta/src/firmware/esp32_csi_node/tools/start_log_raw.py 15
```

`idf.py monitor` din `ruleaza.sh` arată același jurnal.

Formatul unei linii: `I (7733) PAS1: ...` = nivel (I = info), timp în ms de la pornire, etichetă, mesaj.

<pre>
<mark>ets Jun  8 2016 00:22:57</mark>  [1]

<mark>rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)</mark>  [2]
configsip: 0, SPIWP:0xee
clk_drv:0x00,q_drv:0x00,d_drv:0x00,cs0_drv:0x00,hd_drv:0x00,wp_drv:0x00
mode:DIO, clock div:2
load:0x3fff0030,len:7112
load:0x40078000,len:15716
load:0x40080400,len:4
load:0x40080404,len:3876
entry 0x4008064c
<mark>I (29) boot: ESP-IDF v5.1.7 2nd stage bootloader</mark>  [3]
I (29) boot: compile time Nov  9 2026 21:59:38
I (29) boot: Multicore bootloader
I (33) boot: chip revision: v1.1
I (37) boot.esp32: SPI Speed      : 40MHz
I (41) boot.esp32: SPI Mode       : DIO
I (46) boot.esp32: SPI Flash Size : 2MB
I (50) boot: Enabling RNG early entropy source...
<mark>I (56) boot: Partition Table:</mark>  [4]
I (59) boot: ## Label            Usage          Type ST Offset   Length
<mark>I (67) boot:  0 nvs              WiFi data        01 02 00009000 00006000</mark>  [5]
<mark>I (74) boot:  1 phy_init         RF data          01 01 0000f000 00001000</mark>  [6]
<mark>I (82) boot:  2 factory          factory app      00 00 00010000 00100000</mark>  [7]
I (89) boot: End of partition table
I (93) esp_image: segment 0: paddr=00010020 vaddr=3f400020 size=133f0h ( 78832) map
I (130) esp_image: segment 1: paddr=00023418 vaddr=3ffb0000 size=03c38h ( 15416) load
I (137) esp_image: segment 2: paddr=00027058 vaddr=40080000 size=08fc0h ( 36800) load
I (152) esp_image: segment 3: paddr=00030020 vaddr=400d0020 size=68118h (426264) map
I (306) esp_image: segment 4: paddr=00098140 vaddr=40088fc0 size=0dabch ( 55996) load
I (341) boot: Loaded app from partition at offset 0x10000
I (341) boot: Disabling RNG early entropy source...
I (353) cpu_start: Multicore app
I (354) cpu_start: Pro cpu up.
I (354) cpu_start: Starting app cpu, entry point is 0x400813bc
I (0) cpu_start: App cpu up.
I (371) cpu_start: Pro cpu start user code
I (371) cpu_start: cpu freq: 160000000 Hz
I (371) cpu_start: Application information:
<mark>I (376) cpu_start: Project name:     pas_cu_pas</mark>  [8]
I (381) cpu_start: App version:      a3ca16f-dirty
I (386) cpu_start: Compile time:     Nov  9 2026 21:59:35
I (392) cpu_start: ELF file SHA256:  ab917fccdcb01432...
I (398) cpu_start: ESP-IDF:          v5.1.7
I (403) cpu_start: Min chip rev:     v0.0
I (408) cpu_start: Max chip rev:     v3.99
I (413) cpu_start: Chip rev:         v1.1
I (418) heap_init: Initializing. RAM available for dynamic allocation:
I (425) heap_init: At 3FFAE6E0 len 00001920 (6 KiB): DRAM
I (431) heap_init: At 3FFB70F0 len 00028F10 (163 KiB): DRAM
I (437) heap_init: At 3FFE0440 len 00003AE0 (14 KiB): D/IRAM
I (443) heap_init: At 3FFE4350 len 0001BCB0 (111 KiB): D/IRAM
I (450) heap_init: At 40096A7C len 00009584 (37 KiB): IRAM
I (458) spi_flash: detected chip: generic
I (461) spi_flash: flash io: dio
<mark>W (465) spi_flash: Detected size(4096k) larger than the size in the binary image header(2048k). Using the size in the binary image header.</mark>  [9]
I (479) app_start: Starting scheduler on CPU0
I (483) app_start: Starting scheduler on CPU1
I (483) main_task: Started on CPU0
<mark>I (493) main_task: Calling app_main()</mark>  [10]
<mark>I (513) wifi:wifi driver task: 3ffbdb44, prio:23, stack:6656, core=0</mark>  [11]
I (513) wifi:wifi firmware version: a8f8c29
I (513) wifi:wifi certification version: v7.0
<mark>I (513) wifi:config NVS flash: enabled</mark>  [12]
I (513) wifi:config nano formating: disabled
<mark>I (523) wifi:Init data frame dynamic rx buffer num: 32</mark>  [13]
I (523) wifi:Init static rx mgmt buffer num: 5
I (533) wifi:Init management short buffer num: 32
I (533) wifi:Init dynamic tx buffer num: 32
I (543) wifi:Init static rx buffer size: 2212
I (543) wifi:Init static rx buffer num: 10
I (543) wifi:Init dynamic rx buffer num: 32
I (553) wifi_init: rx ba win: 6
I (553) wifi_init: tcpip mbox: 32
I (563) wifi_init: udp mbox: 6
I (563) wifi_init: tcp mbox: 6
I (563) wifi_init: tcp tx win: 5760
I (573) wifi_init: tcp rx win: 5760
I (573) wifi_init: tcp mss: 1440
I (583) wifi_init: WiFi IRAM OP enabled
I (583) wifi_init: WiFi RX IRAM OP enabled
<mark>I (593) phy_init: phy_version 4863,a3a4459,Oct 28 2025,14:30:06</mark>  [14]
<mark>I (673) phy_init: Saving new calibration data due to checksum failure or outdated calibration data, mode(0)</mark>  [15]
<mark>I (693) wifi:mode : sta (fc:e8:c0:e1:1e:d0)</mark>  [16]
I (693) wifi:enable tsf
<mark>I (693) wifi:ic_enable_sniffer</mark>  [17]
<mark>I (693) main_task: Returned from app_main()</mark>  [18]
<mark>I (7733) PAS1: CSI #0  len=128  rssi=-78</mark>  [19]
I (7733) PAS1: CSI #1  len=128  rssi=-79
I (7733) PAS1: CSI #2  len=128  rssi=-79
</pre>

Prima linie din captură era o bucată din pornirea anterioară. Am scos-o.

## Explicații

1. Codul din ROM-ul chipului pornește primul. Data este data ROM-ului, nu data de azi.
2. Motivul pornirii: alimentare sau reset de la PC. Placa pornește din memoria flash.
3. Bootloader-ul ESP-IDF pornește. El citește tabelul de partiții.
4. Memoria flash are zone separate, numite partiții. Fiecare zonă are un rol.
5. `nvs` = zona pentru date salvate. `nvs_flash_init()` o pregătește.
6. `phy_init` = zona pentru parametrii inițiali ai radioului. Proiectul nostru nu o folosește.
7. `factory` = zona pentru programul nostru, la adresa `0x10000`.
8. Rulează proiectul `pas_cu_pas`. Este programul corect.
9. Flash-ul are 4 MB, dar proiectul folosește doar 2 MB. Nu este o problemă.
10. Sistemul apelează funcția noastră `app_main()`.
11. `esp_wifi_init()` creează task-ul Wi-Fi. Acest task apelează `on_csi`.
12. Driverul Wi-Fi poate salva setări în zona `nvs`.
13. Numărul de buffere pentru cadre. Valorile vin din `WIFI_INIT_CONFIG_DEFAULT()`.
14. Versiunea bibliotecii radio (PHY). Codul ei este închis.
15. Placa a calibrat radioul și a salvat calibrarea în zona `nvs`.
16. `esp_wifi_set_mode(WIFI_MODE_STA)` + `esp_wifi_start()`: radioul pornește ca stație.
17. `esp_wifi_set_promiscuous(true)`: modul promiscuu („sniffer”) este pornit.
18. `app_main()` s-a terminat. Task-ul Wi-Fi continuă să ruleze singur.
19. Prima măsurătoare CSI. `len=128` = doar LLTF. `rssi=-78` = sursă îndepărtată.
