// Pasul 1: placa asculta canalul 1 si afiseaza primele 20 de masuratori CSI
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"

static const char *TAG = "PAS1";
static int count = 0;

// Driverul Wi-Fi apeleaza aceasta functie la fiecare cadru primit
static void on_csi(void *ctx, wifi_csi_info_t *info) {
    if (count < 20) {
        ESP_LOGI(TAG, "CSI #%d  len=%u  rssi=%d", count, info->len, info->rx_ctrl.rssi);
    }
    count++;
}

void app_main(void) {
    // 1. Pornim Wi-Fi-ul
    nvs_flash_init();
    esp_event_loop_create_default();
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);
    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_start();

    // 2. Ascultam toate cadrele de pe canalul 1
    esp_wifi_set_promiscuous(true);
    esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);

    // 3. Cerem CSI: inregistram on_csi, apoi pornim masurarea
    esp_wifi_set_csi_rx_cb(on_csi, NULL);
    esp_wifi_set_csi(true);
}
