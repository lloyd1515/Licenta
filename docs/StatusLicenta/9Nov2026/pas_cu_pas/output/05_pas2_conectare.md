# 05 – Pasul 2: placa se conectează la hotspot

Comanda (9 Nov 2026): `bash ruleaza.sh`, 40 de secunde de jurnal. Hotspot pe date mobile, canalul 11.

Am scos liniile de pornire (boot, heap, buffere). Ele sunt la fel ca în `02_jurnal_placa.md`.

<pre>
I (535) main_task: Calling app_main()
I (555) wifi:wifi driver task: 3ffbfb68, prio:23, stack:6656, core=0
I (555) wifi:config NVS flash: enabled
<mark>W (635) wifi:Password length matches WPA2 standards, authmode threshold changes from OPEN to WPA2</mark>  [1]
I (655) phy_init: phy_version 4863,a3a4459,Oct 28 2025,14:30:06
I (815) wifi:mode : sta (fc:e8:c0:e1:1e:d0)
I (815) wifi:enable tsf
<mark>I (815) main_task: Returned from app_main()</mark>  [2]
<mark>I (2285) wifi:new:<11,0>, old:<1,0>, ap:<255,255>, sta:<11,0>, prof:1</mark>  [3]
<mark>I (2285) wifi:state: init -> auth (b0)</mark>  [4]
I (2345) wifi:state: auth -> assoc (0)
I (2405) wifi:state: assoc -> run (10)
<mark>I (2425) wifi:connected with zaqmlp, aid = 2, channel 11, BW20, bssid = f6:2b:8c:e2:21:ac</mark>  [5]
<mark>I (2425) wifi:security: WPA2-PSK, phy: bgn, rssi: -46</mark>  [6]
<mark>I (2435) wifi:pm start, type: 1</mark>  [7]
I (2435) wifi:dp: 1, bi: 102400, li: 3, scale listen interval from 307200 us to 307200 us
I (2455) wifi:dp: 2, bi: 102400, li: 4, scale listen interval from 307200 us to 409600 us
<mark>I (2455) wifi:AP's beacon interval = 102400 us, DTIM period = 2</mark>  [8]
I (2465) wifi:<ba-add>idx:0 (ifx:0, f6:2b:8c:e2:21:ac), tid:0, ssn:0, winSize:64
<mark>I (3445) esp_netif_handlers: sta ip: 10.136.19.115, mask: 255.255.255.0, gw: 10.136.19.245</mark>  [9]
<mark>I (3445) PAS2: Conectat. IP 10.136.19.115, gateway 10.136.19.245</mark>  [10]
<mark>I (32565) PAS2: CSI #0  len=128  rssi=-46  de la f6:2b:8c:e2:21:ac</mark>  [11]
</pre>

## Explicații

1. Parola are lungimea WPA2. Driverul acceptă doar rețele WPA2 sau mai sigure. Nu este o eroare.
2. `app_main()` s-a terminat. Conectarea continuă în task-ul Wi-Fi, prin evenimente.
3. Placa a găsit hotspot-ul și trece de pe canalul 1 pe canalul 11.
4. Conectarea are 3 etape: autentificare (`auth`), asociere (`assoc`), funcționare (`run`).
5. Placa este conectată la `zaqmlp`, pe canalul 11, la 20 MHz. `bssid` = MAC-ul hotspot-ului.
6. Securitate WPA2. Semnal puternic: −46 dBm. Telefonul este aproape de placă.
7. Economia de energie (power save) pornește. Placa doarme între beacon-uri și pierde cadre.
8. Hotspot-ul trimite un beacon la ~0,1 s (102400 µs).
9. Hotspot-ul a dat plăcii o adresă IP (prin DHCP). Gateway = adresa telefonului.
10. Funcția noastră `on_event` a primit evenimentul `IP_EVENT_STA_GOT_IP`.
11. Un singur CSI în ~30 s, de la hotspot. Fără trafic de date, hotspot-ul nu trimite cadre OFDM.

## Concluzii

- Conectarea funcționează. CSI vine acum de la o sursă cunoscută: MAC `f6:2b:8c:e2:21:ac`.
- Dar CSI vine foarte rar. Placa nu cere date, deci hotspot-ul nu trimite date.
- Pasul 3: placa trimite ping-uri regulate la gateway. Fiecare răspuns aduce un CSI.
- De verificat: economia de energie (linia 7) poate pierde cadre. `esp_wifi_set_ps(WIFI_PS_NONE)` o oprește.
