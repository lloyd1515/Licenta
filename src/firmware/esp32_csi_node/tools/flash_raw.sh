#!/bin/bash
# Compileaza si scrie firmware
# Jurnal complet, fara filtre
# Rulare: WIFI_SSID=... WIFI_PASS=... bash flash_raw.sh

# Opreste la prima eroare
set -e
# Cere numele retelei
: "${WIFI_SSID:?Seteaza WIFI_SSID}"
# Cere parola retelei
: "${WIFI_PASS:?Seteaza WIFI_PASS}"
# Portul serial al placii
PORT="${PORT:-/dev/ttyUSB0}"
# Folderul proiectului firmware
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
# Compilare si config, afara repo
OUT="${OUT:-$HOME/esp/csi-node}"
# Creeaza folderul de iesire
mkdir -p "$OUT"
# Scrie SSID si parola
printf 'CONFIG_CSI_WIFI_SSID="%s"\nCONFIG_CSI_WIFI_PASSWORD="%s"\n' "$WIFI_SSID" "$WIFI_PASS" > "$OUT/wifi.defaults"
# Doar proprietarul citeste parola
chmod 600 "$OUT/wifi.defaults"
# Activeaza mediul ESP-IDF
. "$HOME/esp/esp-idf/export.sh" > /dev/null
# Intra in folderul proiectului
cd "$PROJ"
# Compileaza si scrie pe placa
idf.py -B "$OUT/build" -DSDKCONFIG="$OUT/sdkconfig" \
  -DSDKCONFIG_DEFAULTS="sdkconfig.defaults;$OUT/wifi.defaults" \
  -p "$PORT" build flash
