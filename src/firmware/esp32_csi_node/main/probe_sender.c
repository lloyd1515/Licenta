#include "probe_sender.h"
#include "csi_log.h"
#include "esp_log.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Constantele emitatorului
#define PROBE_SOURCE_OFFSET 10
#define FAILURE_REPORT_EVERY 500
#define PROBE_TASK_STACK 2048
#define PROBE_TASK_PRIORITY 5
#define PROBE_TASK_CORE 0

// Cadrul probe request broadcast
static uint8_t probe[64] = {
    PROBE_REQUEST_FRAME_TYPE, 0x00, 0x00, 0x00,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
};

// Task: probe la 10 ms
static void probe_sender_task(void *arg) {
    esp_err_t last_err = ESP_OK;
    for (unsigned n = 1, failed = 0;; n++) {
        esp_err_t err = esp_wifi_80211_tx(WIFI_IF_STA, probe, sizeof(probe), true);
        if (err != ESP_OK) { failed++; last_err = err; }
        if (n % FAILURE_REPORT_EVERY == 0 && failed) {
            ESP_LOGW(CSI_LOG_TAG, "probe: %u din %d esuate in 5 s (%s)", failed, FAILURE_REPORT_EVERY,
                     esp_err_to_name(last_err));
            failed = 0;
        }
        vTaskDelay(1);
    }
}

// Scrie MAC-ul, porneste task-ul
void probe_sender_start(void) {
    ESP_ERROR_CHECK(esp_wifi_get_mac(WIFI_IF_STA, probe + PROBE_SOURCE_OFFSET));
    xTaskCreatePinnedToCore(probe_sender_task, "probe_sender", PROBE_TASK_STACK, NULL, PROBE_TASK_PRIORITY, NULL,
                            PROBE_TASK_CORE);
}
