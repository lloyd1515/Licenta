// Pasul 3: ping regulat la hotspot -> CSI regulat -> amplitudinea, o linie pe secunda
#include <math.h>
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_timer.h"          // nou: esp_timer_get_time(), ceasul placii in microsecunde
#include "nvs_flash.h"
#include "ping/ping_sock.h"     // nou: esp_ping_*, ping-uri ICMP repetate

static const char *TAG = "PAS3";

// nou: sub-frecventele afisate separat (indici LLTF, de la -26 la +26, fara 0)
static const int WATCH[4] = {-20, -7, 7, 20};

// nou: sume pentru secunda curenta; doar on_csi le foloseste, deci nu trebuie protejate
static int     n_pkt;           // cate CSI au venit in secunda curenta
static int     rssi_sum;        // suma RSSI, pentru medie
static double  amp_all_sum;     // suma amplitudinii medii pe cele 52 de sub-frecvente
static double  amp_watch_sum[4];// suma amplitudinii pentru fiecare sub-frecventa din WATCH
static int64_t t_start_us;      // cand a inceput secunda curenta

// nou: amplitudinea unei sub-frecvente k (-26..+26) din bufferul LLTF
//   buf = info->buf; fiecare sub-frecventa ocupa 2 octeti: intai Q (imaginar), apoi I (real)
//   k >= 0 -> intrarea k;  k < 0 -> intrarea 64 + k  (ordinea 0..31, -32..-1 din wifi.rst)
static float amplitude(const int8_t *buf, int k) {
    int entry = k >= 0 ? k : 64 + k;
    int q = buf[2 * entry];
    int i = buf[2 * entry + 1];
    return sqrtf((float)(i * i + q * q));
}

// Driverul Wi-Fi apeleaza aceasta functie la fiecare cadru primit
static void on_csi(void *ctx, wifi_csi_info_t *info) {
    if (info->len < 128) return;   // nou: avem nevoie de tot blocul LLTF (64 x 2 octeti)

    // nou: amplitudinea medie pe sub-frecventele active -26..-1 si +2..+26
    //   sarim peste +1: primii 4 octeti (intrarile 0 si 1) pot fi invalizi (first_word_invalid)
    float sum = 0;
    int count = 0;
    for (int k = -26; k <= 26; k++) {
        if (k == 0 || k == 1) continue;
        sum += amplitude(info->buf, k);
        count++;
    }
    amp_all_sum += sum / count;
    for (int w = 0; w < 4; w++) amp_watch_sum[w] += amplitude(info->buf, WATCH[w]);
    rssi_sum += info->rx_ctrl.rssi;
    n_pkt++;

    // nou: o data pe secunda afisam mediile si incepem o secunda noua
    int64_t now = esp_timer_get_time();
    if (now - t_start_us >= 1000000) {
        ESP_LOGI(TAG, "%3d CSI/s  rssi=%4.0f  A_medie=%5.1f  A[-20]=%5.1f A[-7]=%5.1f A[+7]=%5.1f A[+20]=%5.1f",
                 n_pkt, (double)rssi_sum / n_pkt, amp_all_sum / n_pkt,
                 amp_watch_sum[0] / n_pkt, amp_watch_sum[1] / n_pkt,
                 amp_watch_sum[2] / n_pkt, amp_watch_sum[3] / n_pkt);
        n_pkt = 0; rssi_sum = 0; amp_all_sum = 0;
        for (int w = 0; w < 4; w++) amp_watch_sum[w] = 0;
        t_start_us = now;
    }
}

// nou: porneste ping-uri continue catre gateway (telefonul); fiecare raspuns aduce un CSI
//   gw = adresa gateway-ului, primita de la DHCP
static void start_ping(esp_ip4_addr_t gw) {
    esp_ping_config_t cfg = ESP_PING_DEFAULT_CONFIG();
    cfg.target_addr.type = IPADDR_TYPE_V4;
    cfg.target_addr.u_addr.ip4.addr = gw.addr;
    cfg.count = ESP_PING_COUNT_INFINITE;   // fara oprire
    cfg.interval_ms = 20;                  // 50 de ping-uri pe secunda
    esp_ping_handle_t ping;
    ESP_ERROR_CHECK(esp_ping_new_session(&cfg, NULL, &ping));   // NULL = fara callback-uri
    ESP_ERROR_CHECK(esp_ping_start(ping));
}

// Driverul anunta aici evenimentele: "am pornit", "m-am deconectat", "am primit IP"
static void on_event(void *arg, esp_event_base_t base, int32_t id, void *data) {
    if (base == WIFI_EVENT && (id == WIFI_EVENT_STA_START || id == WIFI_EVENT_STA_DISCONNECTED)) {
        esp_wifi_connect();
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t *got = data;
        ESP_LOGI(TAG, "Conectat. IP " IPSTR ", ping catre gateway " IPSTR, IP2STR(&got->ip_info.ip), IP2STR(&got->ip_info.gw));
        start_ping(got->ip_info.gw);       // nou
    }
}

void app_main(void) {
    // 1. Pornim Wi-Fi-ul si reteaua IP
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, on_event, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, on_event, NULL));

    // 2. Ne conectam la hotspot
    wifi_config_t sta = {.sta = {.ssid = CONFIG_CSI_WIFI_SSID, .password = CONFIG_CSI_WIFI_PASSWORD}};
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &sta));
    ESP_ERROR_CHECK(esp_wifi_start());

    // 3. Cerem CSI: inregistram on_csi, apoi pornim masurarea
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(on_csi, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_csi(true));
}
