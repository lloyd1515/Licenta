#!/bin/bash
# Regenereaza notite_curs_main.md din main.c, ESP-IDF si bibliotecile Wi-Fi (objdump).
# Utilizare: bash unelte/genereaza_curs.sh
set -e
U="$(cd "$(dirname "$0")" && pwd)"
B=$(ls -d ~/.espressif/tools/xtensa-esp32-elf/*/xtensa-esp32-elf/bin)
L=~/esp/esp-idf/components/esp_wifi/lib/esp32
T=$(mktemp -d)
$B/xtensa-esp32-elf-objdump -dr $L/libnet80211.a $L/libpp.a > $T/all.dis
for f in esp_wifi_start ieee80211_ioctl esp_wifi_set_csi_rx_cb wdev_set_csi_rx_cb esp_wifi_set_csi \
         wifi_set_csi ic_set_csi hal_mac_set_csi wdev_csi_rx_process ic_csi_set_config; do
  python3 -I "$U/dis.py" $T/all.dis $f | expand -t8 | sed 's/ \+$//' | grep -v R_XTENSA_SLOT0_OP | sed 1d > $T/$f.txt
done
python3 -I "$U/gen_curs.py" $T "$U/../notite_curs_main.md"
rm -rf $T
