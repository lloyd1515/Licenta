// CSI pe ESP32: conectare la hotspot, ping regulat, amplitudinea pe sub-frecvente
#include "esp_log.h"            // ESP_LOGI
#include "esp_wifi.h"           // esp_wifi_*
#include "esp_event.h"          // bucla de evenimente
#include "nvs_flash.h"          // memoria pentru setarile Wi-Fi
#include "esp_netif.h"          // adresa IP
#include "esp_mac.h"            // MACSTR
#include "esp_timer.h"          // ceasul in microsecunde
#include "ping/ping_sock.h"     // esp_ping_*
#include <math.h>               // sqrtf

static const char *TAG = "CSI";

// sumele pentru secunda curenta
static int     packets;                 // cate CSI au venit
static int     rssi_total;
static int64_t second_start_us;
static float   amplitude_total[53];     // pe fiecare sub-frecventa k, la pozitia k + 26

// amplitudinea sub-frecventei k (-26..26): 2 octeti, intai Q, apoi I
static float amplitude(const int8_t *csi, int k) {
    int index = k >= 0 ? k : 64 + k;
    int q = csi[2 * index];
    int i = csi[2 * index + 1];
    return sqrtf(i * i + q * q);
}

// media pe sub-frecventa k, in secunda curenta
static float average(int k) {
    return amplitude_total[k + 26] / packets;
}

// driverul Wi-Fi apeleaza aceasta functie la fiecare CSI masurat
static void on_csi(void *ctx, wifi_csi_info_t *info) {
    if (info->len < 128) return;        // avem nevoie de tot blocul LLTF
    for (int k = -26; k <= 26; k++) {
        if (k == 0 || k == 1) continue; // 0 = fara semnal, +1 = poate fi invalid
        amplitude_total[k + 26] += amplitude(info->buf, k);
    }
    packets++;
    rssi_total += info->rx_ctrl.rssi;

    int64_t now = esp_timer_get_time();
    if (now - second_start_us >= 1000000) {
        ESP_LOGI(TAG, "%3d CSI/s  rssi=%4d", packets, rssi_total / packets);
        float all = 0;
        for (int k = -26; k <= 26; k++) if (k != 0 && k != 1) all += average(k);
        ESP_LOGI(TAG, "A_medie=%5.1f  A[-20]=%5.1f A[-7]=%5.1f A[+7]=%5.1f A[+20]=%5.1f",
                 all / 51, average(-20), average(-7), average(7), average(20));
        printf("SPEC");
        for (int k = -26; k <= 26; k++) if (k != 0 && k != 1) printf(" %.0f", average(k));
        printf("\n");
        for (int k = 0; k < 53; k++) amplitude_total[k] = 0;
        packets = 0;
        rssi_total = 0;
        second_start_us = now;
    }
}

// ping la telefon (gateway) la fiecare 20 ms: fiecare raspuns aduce un CSI
static void start_ping(esp_ip4_addr_t gateway) {
    esp_ping_config_t ping = ESP_PING_DEFAULT_CONFIG();
    ping.target_addr.type = IPADDR_TYPE_V4;
    ping.target_addr.u_addr.ip4.addr = gateway.addr;
    ping.count = ESP_PING_COUNT_INFINITE;
    ping.interval_ms = 20;
    esp_ping_handle_t session;
    ESP_ERROR_CHECK(esp_ping_new_session(&ping, NULL, &session));
    ESP_ERROR_CHECK(esp_ping_start(session));
}

// driverul ne anunta aici: "am pornit", "m-am deconectat", "am primit IP"
static void on_event(void *arg, esp_event_base_t base, int32_t id, void *data) {
    if (base == WIFI_EVENT && (id == WIFI_EVENT_STA_START || id == WIFI_EVENT_STA_DISCONNECTED)) {
        esp_wifi_connect();
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t *got_ip = data;
        ESP_LOGI(TAG, "Conectat. IP " IPSTR ", gateway " IPSTR,
                 IP2STR(&got_ip->ip_info.ip), IP2STR(&got_ip->ip_info.gw));
        start_ping(got_ip->ip_info.gw);
    }
}

void app_main(void) {
    ESP_LOGI(TAG, "Salut! app_main a pornit.");

    // 1. pornim Wi-Fi-ul
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();
    wifi_init_config_t wifi_init = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&wifi_init));

    // 2. ne conectam la hotspot
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, on_event, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, on_event, NULL));
    wifi_config_t hotspot = {.sta = {.ssid = CONFIG_CSI_WIFI_SSID,
                                     .password = CONFIG_CSI_WIFI_PASSWORD}};
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &hotspot));
    ESP_ERROR_CHECK(esp_wifi_start());

    // 3. cerem CSI
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(on_csi, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_csi(true));
}
