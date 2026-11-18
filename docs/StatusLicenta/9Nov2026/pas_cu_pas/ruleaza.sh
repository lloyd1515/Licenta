#!/bin/bash
# Compileaza, scrie pe placa si arata jurnalul.
#   ./ruleaza.sh      -> jurnalul ramane deschis; iesire cu Ctrl+]
#   ./ruleaza.sh 30   -> jurnalul se inchide singur dupa 30 de secunde
# Reteaua si parola vin din ~/esp/csi-node/wifi.defaults (in afara repo-ului).
. "$HOME/esp/esp-idf/export.sh" > /dev/null
cd "$(dirname "$0")"
IDF=(idf.py -B "$HOME/esp/pas-cu-pas" -DSDKCONFIG="$HOME/esp/pas-cu-pas-sdkconfig"
     -DSDKCONFIG_DEFAULTS="sdkconfig.defaults;$HOME/esp/csi-node/wifi.defaults" -b 115200 -p /dev/ttyUSB0)

"${IDF[@]}" build || exit 1
for i in 1 2 3; do                       # cablul pierde uneori date: incercam de 3 ori
  "${IDF[@]}" flash && break
  [ "$i" = 3 ] && exit 1
  echo ">>> Scrierea pe placa a esuat. Incerc din nou ($i/3)."
done

if [ -n "$1" ]; then
  timeout --foreground "$1" python -m esp_idf_monitor -p /dev/ttyUSB0 -b 115200 \
    "$HOME/esp/pas-cu-pas/pas_cu_pas.elf"
  stty sane
  echo ">>> Jurnalul s-a inchis dupa $1 secunde."
else
  "${IDF[@]}" monitor
fi
