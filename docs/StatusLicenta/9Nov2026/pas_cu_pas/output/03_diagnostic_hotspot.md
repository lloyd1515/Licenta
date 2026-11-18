# 03 – De ce hotspot-ul nu dă CSI

Întrebarea: hotspot-ul `zaqmlp` este pornit, pe canalul 1. De ce pasul 1 nu primește CSI de la el?

## Comanda 1: canalul hotspot-ului, văzut de laptop

```bash
nmcli -f SSID,BSSID,CHAN,FREQ,SIGNAL dev wifi list --rescan yes
```

<pre>
SSID                          BSSID              CHAN  FREQ      SIGNAL
<mark>zaqmlp                        F6:2B:8C:E2:21:AC  1     2412 MHz  89</mark>  [1]
</pre>

1. Hotspot-ul este pe canalul 1 (2412 MHz), cu semnal puternic. Canalul plăcii este corect.

## Comanda 2: firmware de diagnostic

Firmware-ul este o copie a pasului 1, cu două funcții noi:

- `on_rx` numără cadrele trimise de hotspot, pe tipuri: 802.11b, OFDM (a/g), HT (n).
- `on_csi` numără măsurătorile CSI: de la hotspot și în total.
- La fiecare 3 secunde, placa afișează contoarele și le pune la zero.

```c
static void on_rx(void *buf, wifi_promiscuous_pkt_type_t t) {
    wifi_promiscuous_pkt_t *p = buf;
    if (memcmp(p->payload + 10, HS, 6)) return;      // doar cadrele trimise de hotspot
    if (p->rx_ctrl.sig_mode == 1) rx_ht++;            // 802.11n
    else if (p->rx_ctrl.rate <= 3) rx_b++;            // 802.11b: 1, 2, 5.5, 11 Mbps
    else rx_ofdm++;                                   // 802.11a/g
}
```

### Varianta A: cu filtrul `WIFI_PROMIS_FILTER_MASK_ALL`

<pre>
I    0.48 s  main_task Started on CPU0
I    0.49 s  main_task Calling app_main()
I    0.69 s  wifi      mode : sta (fc:e8:c0:e1:1e:d0)
<mark>I    3.69 s  DIAG      hotspot: 11b=31 ofdm=0 ht=0 | csi hotspot=0 csi total=393</mark>  [2]
I    9.69 s  DIAG      hotspot: 11b=29 ofdm=0 ht=0 | csi hotspot=0 csi total=314
I   12.69 s  DIAG      hotspot: 11b=32 ofdm=0 ht=0 | csi hotspot=0 csi total=404
I   15.69 s  DIAG      hotspot: 11b=30 ofdm=0 ht=0 | csi hotspot=0 csi total=386
I   18.69 s  DIAG      hotspot: 11b=32 ofdm=0 ht=0 | csi hotspot=0 csi total=429
</pre>

### Varianta B: fără filtru (filtrul implicit, ca în pasul 1)

<pre>
<mark>I    3.74 s  DIAG      hotspot: 11b=29 ofdm=0 ht=0 | csi hotspot=0 csi total=0</mark>  [3]
I    6.74 s  DIAG      hotspot: 11b=31 ofdm=0 ht=0 | csi hotspot=0 csi total=0
I    9.74 s  DIAG      hotspot: 11b=32 ofdm=0 ht=0 | csi hotspot=0 csi total=0
I   12.74 s  DIAG      hotspot: 11b=46 ofdm=0 ht=0 | csi hotspot=0 csi total=0
I   15.74 s  DIAG      hotspot: 11b=29 ofdm=0 ht=0 | csi hotspot=0 csi total=0
I   18.74 s  DIAG      hotspot: 11b=32 ofdm=0 ht=0 | csi hotspot=0 csi total=0
</pre>

2. Hotspot-ul trimite cam 10 cadre/s, toate 802.11b. 802.11b nu are LLTF, deci nu dă CSI.
3. Fără filtrul `MASK_ALL`, placa nu primește aproape niciun CSI. Cu filtrul, primește cam 130 pe secundă.

## Concluzii

- Beacon-urile hotspot-ului sunt 802.11b. Ele nu dau CSI.
- Hotspot-ul dă CSI doar când trimite date OFDM sau HT, de exemplu spre laptop.
- Filtrul promiscuu schimbă mult numărul de măsurători CSI.
- Filtrul implicit primește toate cadrele, fără tipul `MISC`. `MASK_ALL` activează toți biții, inclusiv `MISC` și `FCSFAIL` (cadre cu erori).
- Încă nu știm care bit dă cele 130 de CSI pe secundă. Testăm în task-ul 2.
- Sursa: `esp_wifi_types.h`, liniile 530–544, și `esp_wifi.h`, linia 849.
