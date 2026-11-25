#include <stdlib.h>
#include "csi_capture.h"
#include "csi_log.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "nvs_flash.h"
#include "probe_sender.h"
#include "udp_transport.h"
#include "node_wifi.h"

// Marimea cozii CSI
#define CSI_QUEUE_BYTES (16 * 1024)

// Porneste modulele in ordine
void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    RingbufHandle_t queue = xRingbufferCreate(CSI_QUEUE_BYTES, RINGBUF_TYPE_NOSPLIT);
    if (!queue) {
        ESP_LOGE(CSI_LOG_TAG, "nu pot aloca coada CSI de %d octeti", CSI_QUEUE_BYTES);
        abort();
    }
    node_wifi_start();
    csi_capture_start(queue);
    ESP_LOGI(CSI_LOG_TAG, "Nodul ESP32 #%d initializat (SSID %s)", CONFIG_CSI_NODE_ID, CONFIG_CSI_WIFI_SSID);
    udp_transport_start(queue);
    probe_sender_start();
}
