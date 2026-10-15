#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/ringbuf.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_timer.h"
#include "driver/uart.h"

#define TAG "CSI_NODE"

#define NODE_ID 3
#define WIFI_CHANNEL 6
#define UART_PORT UART_NUM_0
#define UART_BAUD_RATE 921600
#define FRAME_MAGIC 0xA55A
#define CSI_BYTES 128
#define UART_RX_BUFFER_BYTES 4096
#define CSI_QUEUE_BYTES (16 * 1024)

#define UART_TASK_CORE 1
#define UART_TASK_STACK_BYTES 4096
#define UART_TASK_PRIORITY 10
#define WIFI_TASK_CORE 0
#define WIFI_TASK_STACK_BYTES 2048
#define WIFI_TASK_PRIORITY 5

#define PROBE_BYTES 64
#define PROBE_DEST_OFFSET 4
#define PROBE_SOURCE_OFFSET 10
#define PROBE_BSSID_OFFSET 16
#define MAC_BYTES 6

typedef struct __attribute__((packed)) {
    uint16_t magic;
    uint8_t  node_id;
    int8_t   rssi_dbm;
    uint32_t timestamp_us;
    uint16_t seq;
    int8_t   csi_iq[CSI_BYTES];
} csi_packet_t;

_Static_assert(sizeof(csi_packet_t) == 138, "wire packet must be 138 bytes");

static const uint8_t PROBE_FRAME_CONTROL[] = {0x40, 0x00, 0x00, 0x00};
static const uint8_t BROADCAST_MAC[MAC_BYTES] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
static const uint8_t SOURCE_MAC[MAC_BYTES] = {0x24, 0x0A, 0xC4, 0x00, 0x00, NODE_ID};

static RingbufHandle_t csi_queue = NULL;
static uint16_t next_seq = 0;

static void IRAM_ATTR on_csi(void *ctx, wifi_csi_info_t *info) {
    if (!info || !info->buf || info->len == 0) return;

    BaseType_t woken = pdFALSE;
    csi_packet_t packet;
    memset(&packet, 0, sizeof(packet));
    packet.magic = FRAME_MAGIC;
    packet.node_id = NODE_ID;
    packet.rssi_dbm = info->rx_ctrl.rssi;
    packet.timestamp_us = (uint32_t)esp_timer_get_time();
    packet.seq = next_seq++;

    size_t copy_len = info->len > CSI_BYTES ? CSI_BYTES : info->len;
    memcpy(packet.csi_iq, info->buf, copy_len);

    xRingbufferSendFromISR(csi_queue, &packet, sizeof(packet), &woken);
    if (woken) {
        portYIELD_FROM_ISR();
    }
}

static void uart_sender_task(void *arg) {
    size_t item_size;
    while (1) {
        csi_packet_t *packet = (csi_packet_t *)xRingbufferReceive(csi_queue, &item_size, portMAX_DELAY);
        if (packet != NULL) {
            uart_write_bytes(UART_PORT, (const char *)packet, sizeof(csi_packet_t));
            vRingbufferReturnItem(csi_queue, (void *)packet);
        }
    }
}

static void build_probe_request(uint8_t *out) {
    memset(out, 0, PROBE_BYTES);
    memcpy(out, PROBE_FRAME_CONTROL, sizeof(PROBE_FRAME_CONTROL));
    memcpy(out + PROBE_DEST_OFFSET, BROADCAST_MAC, MAC_BYTES);
    memcpy(out + PROBE_SOURCE_OFFSET, SOURCE_MAC, MAC_BYTES);
    memcpy(out + PROBE_BSSID_OFFSET, BROADCAST_MAC, MAC_BYTES);
}

static void probe_sender_task(void *arg) {
    uint8_t probe[PROBE_BYTES];
    build_probe_request(probe);

    while (1) {
        esp_wifi_80211_tx(WIFI_IF_STA, probe, sizeof(probe), false);
        vTaskDelay(1);
    }
}

static void init_uart(void) {
    uart_config_t uart_config = {
        .baud_rate = UART_BAUD_RATE,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    ESP_ERROR_CHECK(uart_param_config(UART_PORT, &uart_config));
    ESP_ERROR_CHECK(uart_driver_install(UART_PORT, UART_RX_BUFFER_BYTES, 0, 0, NULL, 0));
}

static void init_wifi(void) {
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_start());
    ESP_ERROR_CHECK(esp_wifi_set_channel(WIFI_CHANNEL, WIFI_SECOND_CHAN_NONE));

    wifi_promiscuous_filter_t filter = {
        .filter_mask = WIFI_PROMIS_FILTER_MASK_ALL
    };
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_filter(&filter));
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));
}

static void init_csi(void) {
    wifi_csi_config_t csi_config = {
        .lltf_en = true,
        .htltf_en = true,
        .stbc_htltf2_en = true,
        .ltf_merge_en = true,
        .channel_filter_en = false,
        .manu_scale = false,
        .shift = false,
    };
    ESP_ERROR_CHECK(esp_wifi_set_csi_config(&csi_config));
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(&on_csi, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_csi(true));
}

static void start_tasks(void) {
    xTaskCreatePinnedToCore(uart_sender_task, "uart_sender", UART_TASK_STACK_BYTES, NULL, UART_TASK_PRIORITY, NULL, UART_TASK_CORE);
    xTaskCreatePinnedToCore(probe_sender_task, "probe_sender", WIFI_TASK_STACK_BYTES, NULL, WIFI_TASK_PRIORITY, NULL, WIFI_TASK_CORE);
}

void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    init_uart();
    csi_queue = xRingbufferCreate(CSI_QUEUE_BYTES, RINGBUF_TYPE_NOSPLIT);
    init_wifi();
    init_csi();

    ESP_LOGI(TAG, "Nodul ESP32 #%d initializat cu succes pe Canalul %d!", NODE_ID, WIFI_CHANNEL);

    start_tasks();
}
