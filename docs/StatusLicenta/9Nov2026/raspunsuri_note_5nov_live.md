# Răspunsuri la notele din 5 noiembrie 2026, scrise live

13 nov. 2026 · Cod: `src/firmware/esp32_csi_node/main/main.c` · ESP-IDF v5.1.7 · Dezasamblare: `objdump -dr`.
Detaliile, cu toate sursele: `raspunsuri_tehnice_5nov.html`.

## „De studiat ce face biblioteca”

- Stratul 1, header-ele `esp_wifi.h` și `esp_wifi_types.h`: numele funcțiilor, parametrii și erorile. Le documentează Espressif.
- Stratul 2, bibliotecile închise: `libnet80211.a` (funcțiile `esp_wifi_*`), `libpp.a` (pachete, CSI, `hal_mac_*`), `libphy.a` (radioul).
- Stratul 3, regiștrii din cip: bibliotecile scriu biți la adrese fixe.
- Studiul bibliografic: citez header-ele și ghidul `wifi.rst`. Dezasamblarea o marchez ca analiză proprie.

## „Ce fac funcțiile cu regiștrii de control”

- Funcțiile `esp_wifi_set_*` nu scriu direct în regiștri. Verifică erorile, apoi trimit un mesaj task-ului Wi-Fi (`ieee80211_ioctl`).
- În task-ul Wi-Fi, funcțiile `hal_*` și `phy_*` scriu regiștrii: citesc, schimbă un bit, scriu înapoi.
- `esp_wifi_set_csi(true)` → `hal_mac_set_csi` → registrul 0x3FF7309C, bitul 23 = 1.
- `esp_wifi_set_promiscuous(true)` → `hal_sniffer_rx_set_promis` → 0x3FF730F8, 0x3FF730FC, 0x3FF73104, 0x3FF73C40.
- Sursa: `objdump -dr` pe bibliotecile din ESP-IDF v5.1.7. Espressif nu descrie acești regiștri.

## „Cum se modifică parametrii de recepție”

- Ce păstrează măsurarea: câmpurile din `wifi_csi_config_t`. `ic_csi_set_config` le trimite la `phy_chan_dump_cfg`, care scrie registrul 0x3FF5CD0C.
- Biții din 0x3FF5CD0C: 0 = `htltf_en`, 1 = `lltf_en`, 2 = `stbc_htltf2_en`, 3 = `manu_scale`, 4–7 = `shift`. În proiect: 0x02, doar LLTF.
- Filtrul de canal și media LTF: `phy_chan_filt_set`. CSI pentru ACK: bitul 29 din 0x3FF730F8 și 0x3FF730FC.
- Ce cadre dau CSI: doar cadrele OFDM, care au LLTF. Probe-urile pleacă la 6 Mbps (linia 103). Măsurat: la 1 Mbps, 0 CSI.
- Câte cadre: modul promiscuu cu MASK_ALL (liniile 107–109) primește cadrele tuturor de pe canal.

## „!” Cum scoate funcția CSI din controllerul Wi-Fi

1. `esp_wifi_set_csi_rx_cb(on_csi, NULL)` scrie adresa lui `on_csi` în variabila `g_wdev_csi_rx`. RAM, niciun registru.
2. `esp_wifi_set_csi(true)` pune bitul 23 din 0x3FF7309C pe 1.
3. La fiecare cadru OFDM, hardware-ul estimează canalul din LLTF.
4. `wdev_csi_rx_process` (libpp.a, task-ul Wi-Fi) alocă 64 de octeți, completează `wifi_csi_info_t` și apelează `on_csi`.
5. După return, `info` se eliberează. De aceea `on_csi` copiază 128 de octeți în coadă, iar `udp_sender_task` îi trimite la PC.

## Sursa cadrelor: probe-ul vecinului

- `esp_wifi_config_80211_tx_rate(..., WIFI_PHY_RATE_6M)` scrie rata în RAM (`g_80211_tx_rate`), nu într-un registru.
- `esp_wifi_80211_tx` verifică cadrul, alocă un buffer, citește rata și pune cadrul în coada task-ului Wi-Fi. Hardware-ul MAC îl emite.
