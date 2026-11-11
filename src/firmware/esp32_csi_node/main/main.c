#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/ringbuf.h"
#include "esp_wifi.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "nvs_flash.h"
#include "lwip/sockets.h"

#define TAG "CSI_NODE"
#define NODE_ID 3
#define CSI_BYTES 128

// Pachetul UDP: antet "<HBbIH" + 64 subpurtatoare LLTF, fiecare (Q, I); 0 la k=0 si k=1 daca primul cuvant e invalid
typedef struct __attribute__((packed)) {
    uint16_t magic; uint8_t node_id; int8_t rssi_dbm; uint32_t timestamp_us; uint16_t seq;
    int8_t csi_iq[CSI_BYTES];
} csi_packet_t;
_Static_assert(sizeof(csi_packet_t) == 138, "wire packet must be 138 bytes");

// Probe broadcast: tip, durata, destinatie, sursa (MAC-ul statiei, scris in app_main), BSSID; restul zero
static uint8_t probe[64] = {
    0x40, 0x00, 0x00, 0x00,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
};
static RingbufHandle_t csi_queue;

// Ruleaza in task-ul Wi-Fi: doar pune pachetul in coada
static void IRAM_ATTR on_csi(void *ctx, wifi_csi_info_t *info) {
    static uint16_t next_seq;
    static unsigned dropped;
    if (!info || !info->buf || info->len == 0) return;
    if (!info->hdr || info->hdr[0] != 0x40) return;  // doar probe request: CSI din UDP-ul altui nod ar face o bucla
    if (next_seq < 10)
        ESP_LOGI(TAG, "CSI #%u len=%u first_word_invalid=%d sig_mode=%d rssi=%d",
                 next_seq, info->len, info->first_word_invalid, info->rx_ctrl.sig_mode, info->rx_ctrl.rssi);
    csi_packet_t packet = {.magic = 0xA55A, .node_id = NODE_ID, .rssi_dbm = info->rx_ctrl.rssi,
                           .timestamp_us = (uint32_t)esp_timer_get_time(), .seq = next_seq++};
    memcpy(packet.csi_iq, info->buf, info->len > CSI_BYTES ? CSI_BYTES : info->len);
    if (info->first_word_invalid) memset(packet.csi_iq, 0, 4);  // octetii 0-3 sunt invalizi: trimitem 0
    if (xRingbufferSend(csi_queue, &packet, sizeof(packet), 0) != pdTRUE && dropped++ % 100 == 0)
        ESP_LOGW(TAG, "coada plina: %u pachete CSI pierdute", dropped);
}

// Goleste coada; fara IP, sendto esueaza si pachetul se pierde
static void udp_sender_task(void *arg) {
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    if (sock < 0) ESP_LOGE(TAG, "UDP socket failed: errno %d", errno);
    setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &(int){1}, sizeof(int));
    struct sockaddr_in dest = {.sin_family = AF_INET, .sin_port = htons(CONFIG_CSI_UDP_PORT),
                               .sin_addr.s_addr = inet_addr(CONFIG_CSI_UDP_HOST)};
    size_t size;
    while (1) {
        csi_packet_t *packet = xRingbufferReceive(csi_queue, &size, portMAX_DELAY);
        if (!packet) continue;  // NULL: sendto ar citi de la adresa 0 (panica vazuta in test)
        sendto(sock, packet, sizeof(*packet), 0, (struct sockaddr *)&dest, sizeof(dest));
        vRingbufferReturnItem(csi_queue, packet);
    }
}

// Emite un probe la fiecare tick (10 ms); la 5 s scrie cate au esuat, daca au esuat
static void probe_sender_task(void *arg) {
    esp_err_t last_err = ESP_OK;
    for (unsigned n = 1, failed = 0;; n++) {
        // true: driverul pune numarul de secventa (ghidul il cere dupa conectare)
        esp_err_t err = esp_wifi_80211_tx(WIFI_IF_STA, probe, sizeof(probe), true);
        if (err != ESP_OK) { failed++; last_err = err; }
        if (n % 500 == 0 && failed) {
            ESP_LOGW(TAG, "probe: %u din 500 esuate in 5 s (%s)", failed, esp_err_to_name(last_err));
            failed = 0;
        }
        vTaskDelay(1);
    }
}

// Conectare la pornire si dupa fiecare deconectare
static void on_wifi_event(void *arg, esp_event_base_t base, int32_t id, void *data) {
    if (base == IP_EVENT)
        ESP_LOGI(TAG, "IP " IPSTR ", UDP catre %s:%d", IP2STR(&((ip_event_got_ip_t *)data)->ip_info.ip), CONFIG_CSI_UDP_HOST, CONFIG_CSI_UDP_PORT);
    else if (id == WIFI_EVENT_STA_START || id == WIFI_EVENT_STA_DISCONNECTED)
        esp_wifi_connect();
}

void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    csi_queue = xRingbufferCreate(16 * 1024, RINGBUF_TYPE_NOSPLIT);
    // Statie Wi-Fi pe reteaua din menuconfig, radio mereu activ
    esp_netif_create_default_wifi_sta();
    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&init));
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, on_wifi_event, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, on_wifi_event, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    wifi_config_t sta = {.sta = {.ssid = CONFIG_CSI_WIFI_SSID, .password = CONFIG_CSI_WIFI_PASSWORD}};
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &sta));
    // Probe la 6 Mbps (OFDM): cadrul are LLTF, deci da CSI la celelalte noduri; implicit 1 Mbps, fara LLTF
    ESP_ERROR_CHECK(esp_wifi_config_80211_tx_rate(WIFI_IF_STA, WIFI_PHY_RATE_6M));
    ESP_ERROR_CHECK(esp_wifi_start());
    ESP_ERROR_CHECK(esp_wifi_set_ps(WIFI_PS_NONE));
    // Promiscuu + CSI: on_csi primeste masuratori din toate cadrele
    wifi_promiscuous_filter_t filter = {.filter_mask = WIFI_PROMIS_FILTER_MASK_ALL};
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_filter(&filter));
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));
    // Doar LLTF (cat trimite pachetul); fara filtru de canal, subpurtatoarele vecine raman independente
    wifi_csi_config_t csi = {.lltf_en = true, .channel_filter_en = false};
    ESP_ERROR_CHECK(esp_wifi_set_csi_config(&csi));
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(on_csi, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_csi(true));
    ESP_ERROR_CHECK(esp_wifi_get_mac(WIFI_IF_STA, probe + 10));  // sursa probe-ului = MAC-ul statiei
    ESP_LOGI(TAG, "Nodul ESP32 #%d initializat (SSID %s)", NODE_ID, CONFIG_CSI_WIFI_SSID);
    xTaskCreatePinnedToCore(udp_sender_task, "udp_sender", 4096, NULL, 10, NULL, 1);
    xTaskCreatePinnedToCore(probe_sender_task, "probe_sender", 2048, NULL, 5, NULL, 0);
}
