# 04 – Hotspot pe date mobile: testele rulate din nou

9 Nov 2026, seara. Schimbarea: telefonul ia internetul din date mobile, nu din Wi-Fi.

## Comanda 1: canalul hotspot-ului

```bash
nmcli -f SSID,BSSID,CHAN,FREQ,SIGNAL dev wifi list --rescan yes
```

<pre>
SSID                          BSSID              CHAN  FREQ      SIGNAL
<mark>zaqmlp                        F6:2B:8C:E2:21:AC  11    2462 MHz  100</mark>  [1]
</pre>

1. Același hotspot (același BSSID), dar acum pe canalul 11, nu pe canalul 1.

## Comanda 2: pasul 1, neschimbat (canalul 1)

`bash ruleaza.sh`, 30 de secunde de jurnal.

<pre>
I (753) wifi:ic_enable_sniffer
I (753) main_task: Returned from app_main()
<mark>I (11973) PAS1: CSI #0  len=256  rssi=-75</mark>  [2]
I (12203) PAS1: CSI #1  len=128  rssi=-76
I (29953) PAS1: CSI #3  len=128  rssi=-78
</pre>

2. Doar 4 CSI în 30 s. Hotspot-ul nu mai este pe canalul 1.

Linia `CSI #2` lipsește din captură. Probabil s-a stricat pe portul serial.

## Comanda 3: pasul 1 pe canalul 11

Copie a pasului 1, cu o singură linie schimbată: `esp_wifi_set_channel(11, WIFI_SECOND_CHAN_NONE);`

<pre>
<mark>I (1072) PAS1: CSI #0  len=128  rssi=-38</mark>  [3]
<mark>I (2292) PAS1: CSI #1  len=256  rssi=-65</mark>  [4]
I (2292) PAS1: CSI #2  len=256  rssi=-64
<mark>I (2352) PAS1: CSI #3  len=384  rssi=-62</mark>  [5]
I (2562) PAS1: CSI #4  len=256  rssi=-64
I (3232) PAS1: CSI #5  len=384  rssi=-62
I (7972) PAS1: CSI #6  len=128  rssi=-62
I (12232) PAS1: CSI #7  len=384  rssi=-62
I (12232) PAS1: CSI #8  len=384  rssi=-62
I (12542) PAS1: CSI #9  len=128  rssi=-38
I (15042) PAS1: CSI #10  len=256  rssi=-70
I (15142) PAS1: CSI #11  len=256  rssi=-68
I (15342) PAS1: CSI #12  len=256  rssi=-70
I (15352) PAS1: CSI #13  len=256  rssi=-70
I (20232) PAS1: CSI #14  len=384  rssi=-62
I (23642) PAS1: CSI #15  len=128  rssi=-76
I (23642) PAS1: CSI #16  len=128  rssi=-76
I (23682) PAS1: CSI #17  len=384  rssi=-63
I (23722) PAS1: CSI #18  len=384  rssi=-64
I (23842) PAS1: CSI #19  len=384  rssi=-62
</pre>

3. Sursă foarte aproape (−38 dBm). Diagnosticul de mai jos arată că nu este hotspot-ul.
4. `len=256` = LLTF + HT-LTF. Cadru 802.11n, fără STBC. Pe canalul 1 nu am văzut acest caz.
5. `len=384` = LLTF + HT-LTF + STBC-HT-LTF. Pe canalul 11 sunt multe cadre 802.11n.

## Comanda 4: diagnosticul, în 4 variante

Același firmware ca în `03_diagnostic_hotspot.md`. Schimbăm doar canalul și filtrul.

<pre>
== canal 1, filtru implicit
I (3742) DIAG: hotspot: 11b=0 ofdm=0 ht=0 | csi hotspot=0 csi total=1
I (6742) DIAG: hotspot: 11b=0 ofdm=0 ht=0 | csi hotspot=0 csi total=0
== canal 1, MASK_ALL
<mark>I (3682) DIAG: hotspot: 11b=0 ofdm=0 ht=0 | csi hotspot=0 csi total=1075</mark>  [6]
I (6682) DIAG: hotspot: 11b=0 ofdm=0 ht=0 | csi hotspot=0 csi total=1048
== canal 11, MASK_ALL
<mark>I (6692) DIAG: hotspot: 11b=33 ofdm=0 ht=0 | csi hotspot=0 csi total=7</mark>  [7]
I (12692) DIAG: hotspot: 11b=33 ofdm=0 ht=0 | csi hotspot=0 csi total=14
== canal 11, filtru implicit
<mark>I (3742) DIAG: hotspot: 11b=29 ofdm=0 ht=0 | csi hotspot=0 csi total=2</mark>  [8]
I (6742) DIAG: hotspot: 11b=33 ofdm=0 ht=0 | csi hotspot=0 csi total=12
</pre>

Am păstrat 2 linii din fiecare variantă. Celelalte linii au valori apropiate.

6. Canalul 1 cu `MASK_ALL`: cam 400 CSI/s, fără hotspot. Sursa este altă rețea.
7. Hotspot-ul trimite tot 802.11b, cam 10 cadre/s. CSI de la hotspot: tot 0.
8. Pe canalul 11, filtrul nu schimbă mult rezultatul: 1–4 CSI/s.

## Comparație

| Ce măsurăm | Înainte (hotspot pe Wi-Fi) | Acum (hotspot pe date mobile) |
|---|---|---|
| Canalul hotspot-ului | 1 | 11 |
| Tipul beacon-urilor | 802.11b, ~10/s | 802.11b, ~10/s |
| CSI de la hotspot | 0 | 0 |
| Pasul 1 pe canalul 1 | 20 CSI în ~38 s | 4 CSI în 30 s |
| Canalul 1, `MASK_ALL` | ~130 CSI/s | ~400 CSI/s |
| Canalul 11, `MASK_ALL` | nu am testat | ~2 CSI/s |

## Concluzii

- Singura diferență mare: hotspot-ul a trecut de pe canalul 1 pe canalul 11.
- Hotspot-ul tot nu dă CSI. Beacon-urile rămân 802.11b, indiferent de sursa de internet.
- Hotspot-ul dă CSI doar când trimite date OFDM sau HT unui client conectat.
- Exemplu: la primul test, firmware-ul vechi s-a conectat la hotspot. Atunci au venit CSI cu −47 dBm.
- Cele 130–400 CSI/s de pe canalul 1 cu `MASK_ALL` nu vin de la hotspot.
- Ipoteză, netestată: vin de la rețeaua `deco` de pe canalul 5. Canalele 1 și 5 se suprapun parțial.
