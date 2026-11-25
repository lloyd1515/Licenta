#include "node_wifi.h"
#include "csi_log.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_wifi.h"

// Reconectare si jurnal IP
static void on_wifi_event(void *arg, esp_event_base_t base, int32_t id, void *data) {
    if (base == IP_EVENT)
        ESP_LOGI(CSI_LOG_TAG, "IP " IPSTR ", UDP catre %s:%d", IP2STR(&((ip_event_got_ip_t *)data)->ip_info.ip),
                 CONFIG_CSI_UDP_HOST, CONFIG_CSI_UDP_PORT);
    else if (id == WIFI_EVENT_STA_START || id == WIFI_EVENT_STA_DISCONNECTED)
        esp_wifi_connect();
}

// Statie, 6 Mbps, fara economie
void node_wifi_start(void) {
    esp_netif_create_default_wifi_sta();
    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&init));
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, on_wifi_event, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, on_wifi_event, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    wifi_config_t sta = {.sta = {.ssid = CONFIG_CSI_WIFI_SSID, .password = CONFIG_CSI_WIFI_PASSWORD}};
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &sta));
    ESP_ERROR_CHECK(esp_wifi_config_80211_tx_rate(WIFI_IF_STA, WIFI_PHY_RATE_6M));
    ESP_ERROR_CHECK(esp_wifi_start());
    ESP_ERROR_CHECK(esp_wifi_set_ps(WIFI_PS_NONE));
}
