#!/bin/bash
# Compilare si flash, jurnal complet
set -e
: "${WIFI_SSID:?Seteaza WIFI_SSID}"
: "${WIFI_PASS:?Seteaza WIFI_PASS}"
PORT="${PORT:-/dev/ttyUSB0}"
NODE_ID="${NODE_ID:-3}"
if ! [[ "$NODE_ID" =~ ^[0-9]+$ ]] || [ "$NODE_ID" -gt 255 ]; then echo "NODE_ID trebuie sa fie intre 0 si 255" >&2; exit 1; fi
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${OUT:-$HOME/esp/csi-node}"
# Configurare in afara repo
mkdir -p "$OUT"
printf 'CONFIG_CSI_WIFI_SSID="%s"\nCONFIG_CSI_WIFI_PASSWORD="%s"\n' "$WIFI_SSID" "$WIFI_PASS" > "$OUT/wifi.defaults"
chmod 600 "$OUT/wifi.defaults"
printf 'CONFIG_CSI_NODE_ID=%s\n' "$NODE_ID" > "$OUT/node.defaults"
if [ -f "$OUT/sdkconfig" ]; then sed -i '/^CONFIG_CSI_NODE_ID=/d' "$OUT/sdkconfig"; fi
. "$HOME/esp/esp-idf/export.sh" > /dev/null
cd "$PROJ"
# Compileaza si scrie placa
idf.py -B "$OUT/build" -DSDKCONFIG="$OUT/sdkconfig" \
  -DSDKCONFIG_DEFAULTS="sdkconfig.defaults;$OUT/wifi.defaults;$OUT/node.defaults" \
  -p "$PORT" build flash
