#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/ringbuf.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_timer.h"
#include "lwip/sockets.h"

#define TAG "CSI_NODE"

#define NODE_ID 3
#define FRAME_MAGIC 0xA55A
#define CSI_BYTES 128
#define CSI_QUEUE_BYTES (16 * 1024)
#define WIFI_CONNECTED_BIT BIT0

#define UDP_TASK_CORE 1
#define UDP_TASK_STACK_BYTES 4096
#define UDP_TASK_PRIORITY 10
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
static EventGroupHandle_t wifi_events = NULL;
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

static int open_udp_socket(struct sockaddr_in *dest) {
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    if (sock < 0) {
        ESP_LOGE(TAG, "UDP socket failed: errno %d", errno);
        return -1;
    }
    int broadcast = 1;
    setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast));
    memset(dest, 0, sizeof(*dest));
    dest->sin_family = AF_INET;
    dest->sin_port = htons(CONFIG_CSI_UDP_PORT);
    dest->sin_addr.s_addr = inet_addr(CONFIG_CSI_UDP_HOST);
    return sock;
}

static void udp_sender_task(void *arg) {
    struct sockaddr_in dest;
    int sock = -1;
    size_t item_size;
    while (1) {
        csi_packet_t *packet = (csi_packet_t *)xRingbufferReceive(csi_queue, &item_size, portMAX_DELAY);
        if (packet == NULL) continue;
        bool connected = xEventGroupGetBits(wifi_events) & WIFI_CONNECTED_BIT;
        if (connected && sock < 0) {
            sock = open_udp_socket(&dest);
        }
        if (connected && sock >= 0) {
            sendto(sock, packet, sizeof(csi_packet_t), 0, (struct sockaddr *)&dest, sizeof(dest));
        }
        vRingbufferReturnItem(csi_queue, (void *)packet);
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

static void on_wifi_event(void *arg, esp_event_base_t base, int32_t id, void *data) {
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        xEventGroupClearBits(wifi_events, WIFI_CONNECTED_BIT);
        ESP_LOGW(TAG, "Wi-Fi deconectat, reconectare...");
        esp_wifi_connect();
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t *event = (ip_event_got_ip_t *)data;
        ESP_LOGI(TAG, "IP " IPSTR ", trimitere UDP catre %s:%d", IP2STR(&event->ip_info.ip), CONFIG_CSI_UDP_HOST, CONFIG_CSI_UDP_PORT);
        xEventGroupSetBits(wifi_events, WIFI_CONNECTED_BIT);
    }
}

static void init_wifi(void) {
    wifi_events = xEventGroupCreate();
    esp_netif_create_default_wifi_sta();
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &on_wifi_event, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &on_wifi_event, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));

    wifi_config_t wifi_config = {
        .sta = {
            .ssid = CONFIG_CSI_WIFI_SSID,
            .password = CONFIG_CSI_WIFI_PASSWORD,
        },
    };
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());
    ESP_ERROR_CHECK(esp_wifi_set_ps(WIFI_PS_NONE));

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
    xTaskCreatePinnedToCore(udp_sender_task, "udp_sender", UDP_TASK_STACK_BYTES, NULL, UDP_TASK_PRIORITY, NULL, UDP_TASK_CORE);
    xTaskCreatePinnedToCore(probe_sender_task, "probe_sender", WIFI_TASK_STACK_BYTES, NULL, WIFI_TASK_PRIORITY, NULL, WIFI_TASK_CORE);
}

void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    csi_queue = xRingbufferCreate(CSI_QUEUE_BYTES, RINGBUF_TYPE_NOSPLIT);
    init_wifi();
    init_csi();

    ESP_LOGI(TAG, "Nodul ESP32 #%d initializat cu succes (SSID %s)!", NODE_ID, CONFIG_CSI_WIFI_SSID);

    start_tasks();
}
