#include "csi_capture.h"
#include "csi_log.h"
#include "csi_packet.h"
#include "esp_log.h"
#include "esp_wifi.h"
#include "probe_sender.h"

// Limite pentru jurnal
#define FIRST_LOGGED_FRAMES 10
#define DROP_LOG_EVERY 100

static RingbufHandle_t csi_queue;

// Callback CSI: pachet in coada
static void IRAM_ATTR on_csi(void *ctx, wifi_csi_info_t *info) {
    static uint16_t next_seq;
    static unsigned dropped;
    if (!info || !info->buf || info->len == 0) return;
    if (!info->hdr || info->hdr[0] != PROBE_REQUEST_FRAME_TYPE) return;
    if (next_seq < FIRST_LOGGED_FRAMES)
        ESP_LOGI(CSI_LOG_TAG, "CSI #%u len=%u first_word_invalid=%d sig_mode=%d rssi=%d",
                 next_seq, info->len, info->first_word_invalid, info->rx_ctrl.sig_mode, info->rx_ctrl.rssi);
    csi_packet_t packet = csi_packet_build(info, next_seq++);
    if (xRingbufferSend(csi_queue, &packet, sizeof(packet), 0) != pdTRUE && dropped++ % DROP_LOG_EVERY == 0)
        ESP_LOGW(CSI_LOG_TAG, "coada plina: %u pachete CSI pierdute", dropped);
}

// Promiscuu, LLTF, callback, pornire
void csi_capture_start(RingbufHandle_t queue) {
    csi_queue = queue;
    wifi_promiscuous_filter_t filter = {.filter_mask = WIFI_PROMIS_FILTER_MASK_ALL};
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_filter(&filter));
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));
    wifi_csi_config_t csi = {.lltf_en = true, .channel_filter_en = false};
    ESP_ERROR_CHECK(esp_wifi_set_csi_config(&csi));
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(on_csi, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_csi(true));
}
