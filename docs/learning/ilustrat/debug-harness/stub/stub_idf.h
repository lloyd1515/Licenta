/* Definiții minime ESP-IDF, doar pentru a compila main.c pe PC. Structurile Wi-Fi vin din ESP-IDF 5.1 (ținta ESP32). */
#pragma once
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdarg.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define CONFIG_CSI_WIFI_SSID "csi-lab"
#define CONFIG_CSI_WIFI_PASSWORD ""
#define CONFIG_CSI_UDP_HOST "255.255.255.255"
#define CONFIG_CSI_UDP_PORT 5005

typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define IRAM_ATTR

/* FreeRTOS */
typedef int BaseType_t;
typedef unsigned int UBaseType_t;
typedef uint32_t TickType_t;
typedef uint32_t EventBits_t;
typedef void (*TaskFunction_t)(void *);
typedef void *TaskHandle_t;
#define pdFALSE 0
#define pdTRUE 1
#define portMAX_DELAY 0xffffffffu
#define BIT0 (1u << 0)
#define portYIELD_FROM_ISR() stub_yield_from_isr()

typedef struct stub_ring *RingbufHandle_t;
typedef struct stub_events *EventGroupHandle_t;
typedef enum { RINGBUF_TYPE_NOSPLIT = 0, RINGBUF_TYPE_ALLOWSPLIT, RINGBUF_TYPE_BYTEBUF } RingbufferType_t;

RingbufHandle_t xRingbufferCreate(size_t size, RingbufferType_t type);
BaseType_t xRingbufferSendFromISR(RingbufHandle_t rb, const void *item, size_t len, BaseType_t *woken);
void *xRingbufferReceive(RingbufHandle_t rb, size_t *len, TickType_t wait);
void vRingbufferReturnItem(RingbufHandle_t rb, void *item);
EventGroupHandle_t xEventGroupCreate(void);
EventBits_t xEventGroupGetBits(EventGroupHandle_t g);
EventBits_t xEventGroupSetBits(EventGroupHandle_t g, EventBits_t bits);
EventBits_t xEventGroupClearBits(EventGroupHandle_t g, EventBits_t bits);
void vTaskDelay(TickType_t ticks);
BaseType_t xTaskCreatePinnedToCore(TaskFunction_t fn, const char *name, uint32_t stack, void *arg, UBaseType_t prio, TaskHandle_t *h, BaseType_t core);
void stub_yield_from_isr(void);

/* esp_timer, nvs, log */
int64_t esp_timer_get_time(void);
esp_err_t nvs_flash_init(void);
void stub_log(char level, const char *tag, const char *fmt, ...);
#define ESP_LOGE(tag, fmt, ...) stub_log('E', tag, fmt, ##__VA_ARGS__)
#define ESP_LOGW(tag, fmt, ...) stub_log('W', tag, fmt, ##__VA_ARGS__)
#define ESP_LOGI(tag, fmt, ...) stub_log('I', tag, fmt, ##__VA_ARGS__)
void stub_check_failed(const char *expr);
#define ESP_ERROR_CHECK(x) do { esp_err_t err_rc_ = (x); if (err_rc_ != ESP_OK) stub_check_failed(#x); } while (0)

/* esp_event, netif */
typedef const char *esp_event_base_t;
typedef void (*esp_event_handler_t)(void *arg, esp_event_base_t base, int32_t id, void *data);
extern esp_event_base_t WIFI_EVENT;
extern esp_event_base_t IP_EVENT;
#define ESP_EVENT_ANY_ID (-1)
enum { WIFI_EVENT_STA_START = 2, WIFI_EVENT_STA_DISCONNECTED = 5 };
enum { IP_EVENT_STA_GOT_IP = 0 };
typedef struct { uint32_t addr; } esp_ip4_addr_t;
typedef struct { esp_ip4_addr_t ip; esp_ip4_addr_t netmask; esp_ip4_addr_t gw; } esp_netif_ip_info_t;
typedef struct { void *esp_netif; esp_netif_ip_info_t ip_info; bool ip_changed; } ip_event_got_ip_t;
#define IPSTR "%d.%d.%d.%d"
#define IP2STR(a) (int)((a)->addr & 0xff), (int)(((a)->addr >> 8) & 0xff), (int)(((a)->addr >> 16) & 0xff), (int)(((a)->addr >> 24) & 0xff)
esp_err_t esp_netif_init(void);
esp_err_t esp_event_loop_create_default(void);
void *esp_netif_create_default_wifi_sta(void);
esp_err_t esp_event_handler_register(esp_event_base_t base, int32_t id, esp_event_handler_t h, void *arg);

/* esp_wifi (structuri copiate din ESP-IDF 5.1, ținta ESP32) */
typedef struct {
    signed rssi:8; unsigned rate:5; unsigned :1; unsigned sig_mode:2; unsigned :16; unsigned mcs:7; unsigned cwb:1; unsigned :16;
    unsigned smoothing:1; unsigned not_sounding:1; unsigned :1; unsigned aggregation:1; unsigned stbc:2; unsigned fec_coding:1; unsigned sgi:1;
    signed noise_floor:8; unsigned ampdu_cnt:8; unsigned channel:4; unsigned secondary_channel:4; unsigned :8; unsigned timestamp:32;
    unsigned :32; unsigned :31; unsigned ant:1; unsigned sig_len:12; unsigned :12; unsigned rx_state:8;
} wifi_pkt_rx_ctrl_t;
typedef struct {
    wifi_pkt_rx_ctrl_t rx_ctrl; uint8_t mac[6]; uint8_t dmac[6]; bool first_word_invalid; int8_t *buf; uint16_t len;
    uint8_t *hdr; uint8_t *payload; uint16_t payload_len; uint16_t rx_seq;
} wifi_csi_info_t;
typedef struct { bool lltf_en; bool htltf_en; bool stbc_htltf2_en; bool ltf_merge_en; bool channel_filter_en; bool manu_scale; uint8_t shift; bool dump_ack_en; } wifi_csi_config_t;
typedef void (*wifi_csi_cb_t)(void *ctx, wifi_csi_info_t *data);
typedef struct { uint32_t filter_mask; } wifi_promiscuous_filter_t;
typedef struct { struct { uint8_t ssid[32]; uint8_t password[64]; } sta; } wifi_config_t;
typedef struct { int magic; } wifi_init_config_t;
typedef enum { WIFI_MODE_STA = 1 } wifi_mode_t;
typedef enum { WIFI_IF_STA = 0 } wifi_interface_t;
typedef enum { WIFI_STORAGE_RAM = 0 } wifi_storage_t;
typedef enum { WIFI_PS_NONE = 0 } wifi_ps_type_t;
#define WIFI_INIT_CONFIG_DEFAULT() { .magic = 0x1F2F3F4F }
#define WIFI_PROMIS_FILTER_MASK_ALL (0xFFFFFFFF)
esp_err_t esp_wifi_init(const wifi_init_config_t *cfg);
esp_err_t esp_wifi_set_storage(wifi_storage_t s);
esp_err_t esp_wifi_set_mode(wifi_mode_t m);
esp_err_t esp_wifi_set_config(wifi_interface_t i, wifi_config_t *c);
esp_err_t esp_wifi_start(void);
esp_err_t esp_wifi_connect(void);
esp_err_t esp_wifi_set_ps(wifi_ps_type_t t);
esp_err_t esp_wifi_set_promiscuous_filter(const wifi_promiscuous_filter_t *f);
esp_err_t esp_wifi_set_promiscuous(bool en);
esp_err_t esp_wifi_set_csi_config(const wifi_csi_config_t *c);
esp_err_t esp_wifi_set_csi_rx_cb(wifi_csi_cb_t cb, void *ctx);
esp_err_t esp_wifi_set_csi(bool en);
esp_err_t esp_wifi_80211_tx(wifi_interface_t i, const void *buf, int len, bool en_sys_seq);

/* socket-uri: păstrăm structurile POSIX, înlocuim apelurile */
int stub_socket(int d, int t, int p);
int stub_setsockopt(int s, int l, int o, const void *v, socklen_t n);
ssize_t stub_sendto(int s, const void *b, size_t n, int f, const struct sockaddr *a, socklen_t l);
#define socket stub_socket
#define setsockopt stub_setsockopt
#define sendto stub_sendto

/* stare vizibilă din depanator + control scenarii */
extern char stub_log_buf[1 << 16];
extern unsigned stub_log_len;
extern int stub_ring_items, stub_ring_bytes, stub_sock_open;
extern unsigned stub_event_bits;
void stub_end_scenario(const char *why);
void stub_ring_feed(const void *item, size_t len);
void stub_set_exit_after(int receives_or_delays);
