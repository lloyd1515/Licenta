"""Genereaza o copie de diagnostic a main.c din proiect: contoare afisate la fiecare 5 s
si motivul deconectarii. Codul proiectului ramane neschimbat in rest.
Utilizare: python3 gen_diag_main.py <main.c proiect> <main.c iesire> <varianta> [NODE_ID]
Variante:
  new       codul reparat
  old_seq   en_sys_seq = false (ca inainte de 12 nov.)
  old_rate  fara esp_wifi_config_80211_tx_rate: probe-urile pleaca la rata implicita
  old_csi   configurarea CSI veche (LLTF + HT-LTF + STBC-HT-LTF + merge)
  rate50    probe la 50 Hz (vTaskDelay(2)); linia DIAG apare atunci la 10 s
Linia DIAG:
  tx ok/err        rezultatul esp_wifi_80211_tx
  rx probe vecin   probe-urile celeilalte placi primite in modul promiscuu, dupa rata (1M, 6M, alta)
  csi total        apeluri on_csi; ht = cadre 11n; len!=128 = alta lungime; fwi = first_word_invalid 1
  csi probe vecin  CSI din probe-urile celeilalte placi (sursa = vecinul, destinatia = broadcast)
  csi date vecin   CSI din alte cadre ale vecinului (de exemplu, UDP catre AP)
  hdr probe        CSI cu hdr[0] = 0x40 (probe request), de la orice sursa; doar acestea ajung la PC
  udp ok/err       rezultatul sendto; errno = codul ultimei erori
  AP bcast / 11b   cadre de date de la AP catre toate statiile (FromDS, destinatie broadcast); 11b = la rate DSSS/CCK
  Contoarele CSI numara toate apelurile on_csi, inainte de filtrul din main.c.
Copia se compileaza intr-o copie a src/firmware/esp32_csi_node (CMakeLists.txt, main/, sdkconfig.defaults).
Rezultate: pas_cu_pas/output/08_main_reparat_12nov.txt."""
import sys

# Placile din test: A pe /dev/ttyUSB0, B pe /dev/ttyUSB1
PLACI = "{0xfc, 0xe8, 0xc0, 0xe1, 0x1e, 0xd0}, {0xfc, 0xe8, 0xc0, 0xe1, 0x1a, 0xec}"

src, dst, variant = sys.argv[1], sys.argv[2], sys.argv[3]
code = open(src).read()


def sub(old, new):
    global code
    assert old in code, old
    code = code.replace(old, new, 1)


sub("static RingbufHandle_t csi_queue;",
    "static RingbufHandle_t csi_queue;\n"
    "static volatile unsigned d_ok, d_err, d_p1, d_p6, d_px, d_csi, d_ht, d_big, d_fwi, d_cprobe, d_cdata, d_h40, d_uok, d_uerr, d_errno, d_rel, d_rel_b;\n"
    "static const uint8_t PLACI[2][6] = {" + PLACI + "};\n"
    "static bool e_vecin(const uint8_t *mac) {  // alta placa din test, nu aceasta\n"
    "    if (!memcmp(mac, probe + 10, 6)) return false;\n"
    "    return !memcmp(mac, PLACI[0], 6) || !memcmp(mac, PLACI[1], 6);\n"
    "}\n"
    "static void on_rx(void *buf, wifi_promiscuous_pkt_type_t type) {\n"
    "    const wifi_promiscuous_pkt_t *p = buf;\n"
    "    if (type == WIFI_PKT_DATA && (p->payload[1] & 0x03) == 0x02 && p->payload[4] == 0xff && p->payload[5] == 0xff) {\n"
    "        d_rel++; d_rel_b += p->rx_ctrl.sig_mode == 0 && p->rx_ctrl.rate < 0x08; return; }  // AP -> toate statiile\n"
    "    if (type != WIFI_PKT_MGMT || p->payload[0] != 0x40 || !e_vecin(p->payload + 10)) return;\n"
    "    if (p->rx_ctrl.sig_mode == 0 && p->rx_ctrl.rate == 0x00) d_p1++;\n"
    "    else if (p->rx_ctrl.sig_mode == 0 && p->rx_ctrl.rate == 0x0B) d_p6++;\n"
    "    else d_px++;\n"
    "}")
sub("    if (!info || !info->buf || info->len == 0) return;\n",
    "    if (!info || !info->buf || info->len == 0) return;\n"
    "    d_csi++; d_ht += info->rx_ctrl.sig_mode == 1; d_fwi += info->first_word_invalid; d_big += info->len != 128; d_h40 += info->hdr && info->hdr[0] == 0x40;\n"
    "    if (e_vecin(info->mac)) { if (!memcmp(info->dmac, \"\\xff\\xff\\xff\\xff\\xff\\xff\", 6)) d_cprobe++; else d_cdata++; }\n")
sub("        if (err != ESP_OK) { failed++;",
    "        if (err == ESP_OK) d_ok++; else d_err++;\n"
    "        static unsigned dn; if (++dn % 500 == 0) {\n"
    "            ESP_LOGI(\"DIAG\", \"5 s: tx ok=%u err=%u | rx probe vecin 1M=%u 6M=%u alta=%u | csi total=%u ht=%u len!=128=%u fwi=%u | csi probe vecin=%u date vecin=%u | hdr probe=%u | udp ok=%u err=%u errno=%u | AP bcast=%u 11b=%u\",\n"
    "                     d_ok, d_err, d_p1, d_p6, d_px, d_csi, d_ht, d_big, d_fwi, d_cprobe, d_cdata, d_h40, d_uok, d_uerr, d_errno, d_rel, d_rel_b);\n"
    "            d_ok = d_err = d_p1 = d_p6 = d_px = d_csi = d_ht = d_big = d_fwi = d_cprobe = d_cdata = d_h40 = d_uok = d_uerr = d_rel = d_rel_b = 0; }\n"
    "        if (err != ESP_OK) { failed++;")
sub("    else if (id == WIFI_EVENT_STA_START || id == WIFI_EVENT_STA_DISCONNECTED)\n",
    "    else if (id == WIFI_EVENT_STA_CONNECTED) ESP_LOGI(\"DIAG\", \"conectat\");\n"
    "    else if (id == WIFI_EVENT_STA_DISCONNECTED)\n"
    "        ESP_LOGI(\"DIAG\", \"deconectat, motiv %d\", ((wifi_event_sta_disconnected_t *)data)->reason);\n"
    "    if (base == WIFI_EVENT && (id == WIFI_EVENT_STA_START || id == WIFI_EVENT_STA_DISCONNECTED))\n")
sub("        sendto(sock, packet, sizeof(*packet), 0, (struct sockaddr *)&dest, sizeof(dest));\n",
    "        if (sendto(sock, packet, sizeof(*packet), 0, (struct sockaddr *)&dest, sizeof(dest)) < 0) { d_uerr++; d_errno = errno; } else d_uok++;\n")
sub("    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));\n",
    "    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_rx_cb(on_rx));\n"
    "    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));\n")
if variant == "old_seq":
    sub("sizeof(probe), true);", "sizeof(probe), false);")
elif variant == "old_rate":
    sub("    ESP_ERROR_CHECK(esp_wifi_config_80211_tx_rate(WIFI_IF_STA, WIFI_PHY_RATE_6M));\n", "")
elif variant == "rate50":
    sub("        vTaskDelay(1);\n", "        vTaskDelay(2);\n")
elif variant == "old_csi":
    sub("{.lltf_en = true, .channel_filter_en = false}",
        "{.lltf_en = true, .htltf_en = true, .stbc_htltf2_en = true, .ltf_merge_en = true}")
elif variant != "new":
    sys.exit("varianta necunoscuta: " + variant)
if len(sys.argv) > 4:
    sub("#define NODE_ID 3\n", "#define NODE_ID " + sys.argv[4] + "\n")
open(dst, "w").write(code)
