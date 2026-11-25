#!/bin/bash
# Compilare si flash, jurnal colorat
set -e -o pipefail
: "${WIFI_SSID:?Seteaza WIFI_SSID}"
: "${WIFI_PASS:?Seteaza WIFI_PASS}"
PORT="${PORT:-/dev/ttyUSB0}"
NODE_ID="${NODE_ID:-3}"
if ! [[ "$NODE_ID" =~ ^[0-9]+$ ]] || [ "$NODE_ID" -gt 255 ]; then echo "NODE_ID trebuie sa fie intre 0 si 255" >&2; exit 1; fi
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${OUT:-$HOME/esp/csi-node}"
mkdir -p "$OUT"
printf 'CONFIG_CSI_WIFI_SSID="%s"\nCONFIG_CSI_WIFI_PASSWORD="%s"\n' "$WIFI_SSID" "$WIFI_PASS" > "$OUT/wifi.defaults"
chmod 600 "$OUT/wifi.defaults"
# Scrie ID-ul nodului
printf 'CONFIG_CSI_NODE_ID=%s\n' "$NODE_ID" > "$OUT/node.defaults"
if [ -f "$OUT/sdkconfig" ]; then sed -i '/^CONFIG_CSI_NODE_ID=/d' "$OUT/sdkconfig"; fi
. "$HOME/esp/esp-idf/export.sh" > /dev/null
cd "$PROJ"

if [ -t 1 ] || [ -n "$FORCE_COLOR" ]; then COLOR=1; else COLOR=0; fi

# Filtreaza si coloreaza jurnalul idf
coloreaza() {
  awk -v color="$COLOR" '
    BEGIN { W = 30; activ = 0; hash = 0; app_afisat = 0 }
    function h2n(h,   i, n) { n = 0; h = tolower(h); sub(/^0x/, "", h)
      for (i = 1; i <= length(h); i++) n = n * 16 + index("0123456789abcdef", substr(h, i, 1)) - 1
      return n }
    function sfarsit_bara() { if (activ) { print ""; activ = 0 } }
    function p(cod, s) { sfarsit_bara(); if (color) printf "\033[%sm%s\033[0m\n", cod, s; else print s; fflush() }
    function bara(eticheta, pct,    n, i, s) {
      n = int(pct * W / 100); s = ""
      for (i = 0; i < W; i++) s = s (i < n ? "█" : "░")
      if (color) { printf "\r\033[96m%s \033[92m%s\033[96m %3d%%\033[0m\033[K", eticheta, s, pct; activ = 1 }
      if (pct >= 100) { if (!color) printf "%s %s 100%%", eticheta, s; print ""; activ = 0 }
      fflush()
    }
    /^Writing at 0x[0-9a-f]+\.\.\. \([0-9]+ %\)/ {
      ad = $3; sub(/\.+$/, "", ad); n = h2n(ad)
      et = (n < 32768) ? "Bootloader" : (n < 65536) ? "Partitii  " : "Aplicatie "
      match($0, /\([0-9]+ %\)/); bara(et, substr($0, RSTART + 1, RLENGTH - 4) + 0); next }
    /^\[[0-9]+\/[0-9]+\]/ {
      match($0, /^\[[0-9]+\/[0-9]+\]/); t = substr($0, RSTART + 1, RLENGTH - 2); split(t, a, "/")
      if (a[2] + 0 > 20) { bara("Compilare", int(a[1] * 100 / a[2])) }
      next }
    /(^|[^_[:alnum:].])(error|Error|ERROR|FAILED)[: ]|fatal error|A fatal error/ { p("1;91", $0); next }
    /warning:|WARNING|Warning:/                                { p("93", $0); next }
    /Executing action: all/                                    { p("1;96", "== COMPILARE =="); next }
    /Executing action: flash/                                  { p("1;96", "== SCRIERE =="); next }
    /^esp32_csi_node.bin binary size/ {
      if (!app_afisat) { match($0, /\([0-9]+%\) free/); l = substr($0, RSTART + 1, RLENGTH - 8)
        p("92", sprintf("Aplicatie: %d KB (%s%% liber in partitie)", h2n($4) / 1024 + 0.5, l)); app_afisat = 1 }
      next }
    /^Chip is/                                                 { chip = substr($0, 9); next }
    /^MAC:/                                                    { p("94", "Placa: " chip " | MAC " substr($0, 6)); next }
    /^Hash of data verified/                                   { hash++; next }
    /^$|binary size|^Wrote |^Compressed|^Flash will|^Serial port|^Connecting|^Features|^Crystal|^Uploading stub|^Running stub|^Stub running|^Changing baud|^Changed|^Configuring flash|^SHA digest|^Leaving|^Hard resetting|^Done$|^Successfully created|^Project build complete|^Generated|^Merged|^Creating esp32|^Running ninja|^Executing "|^esptool.py|^Bootloader/ { next }
    { sfarsit_bara(); print; fflush() }
    END { sfarsit_bara(); if (hash > 0) p(hash == 3 ? "92" : "1;91", "Verificare: " hash "/3 parti scrise corect") }'
}

# Compileaza si scrie placa
if idf.py -B "$OUT/build" -DSDKCONFIG="$OUT/sdkconfig" \
  -DSDKCONFIG_DEFAULTS="sdkconfig.defaults;$OUT/wifi.defaults;$OUT/node.defaults" \
  -p "$PORT" build flash 2>&1 | coloreaza; then
  [ "$COLOR" = 1 ] && printf '\033[1;92m>>> GATA: firmware scris pe placa.\033[0m\n' || echo ">>> GATA: firmware scris pe placa."
else
  [ "$COLOR" = 1 ] && printf '\033[1;91m>>> ESEC: vezi liniile rosii de mai sus.\033[0m\n' || echo ">>> ESEC: vezi liniile rosii de mai sus."
  exit 1
fi
