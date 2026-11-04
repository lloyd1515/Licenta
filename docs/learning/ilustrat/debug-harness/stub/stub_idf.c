/* Implementări simulate ale bibliotecilor. Fișierul se compilează fără -g: depanatorul trece peste el dintr-un singur pas. */
#include "stub_idf.h"
#include <setjmp.h>
#undef socket
#undef setsockopt
#undef sendto

char stub_log_buf[1 << 16];
unsigned stub_log_len;
int stub_ring_items, stub_ring_bytes, stub_sock_open;
unsigned stub_event_bits;
jmp_buf stub_jmp;
esp_event_base_t WIFI_EVENT = "WIFI_EVENT";
esp_event_base_t IP_EVENT = "IP_EVENT";

#define RING_CAPACITY 16384
#define RING_HEADER 8
#define RING_SLOTS 256
#define ITEM_MAX 256
struct stub_ring { size_t cap; };
struct stub_events { int unused; };
static struct stub_ring ring_obj;
static struct stub_events events_obj;
static unsigned char items[RING_SLOTS][ITEM_MAX];
static size_t item_len[RING_SLOTS];
static int head, tail, pending_return = -1;
static int delays, exit_after;
static int64_t clock_us = 5000000;

static void add(const char *kind, const char *fmt, va_list ap) {
    int n = snprintf(stub_log_buf + stub_log_len, sizeof(stub_log_buf) - stub_log_len, "%s|", kind);
    n += vsnprintf(stub_log_buf + stub_log_len + n, sizeof(stub_log_buf) - stub_log_len - n, fmt, ap);
    stub_log_len += n;
    stub_log_buf[stub_log_len++] = '\n';
}
static void call(const char *fmt, ...) { va_list ap; va_start(ap, fmt); add("C", fmt, ap); va_end(ap); }
void stub_log(char level, const char *tag, const char *fmt, ...) {
    char text[256], line[300]; va_list ap;
    va_start(ap, fmt); vsnprintf(text, sizeof(text), fmt, ap); va_end(ap);
    snprintf(line, sizeof(line), "%c (%s) %s", level, tag, text);
    int n = snprintf(stub_log_buf + stub_log_len, sizeof(stub_log_buf) - stub_log_len, "L|%s\n", line);
    stub_log_len += n;
}
void stub_check_failed(const char *expr) { call("ESP_ERROR_CHECK a eșuat: %s", expr); }

void stub_end_scenario(const char *why) {
    call("sfârșitul scenariului: %s", why);
    longjmp(stub_jmp, 1);
}
void stub_set_exit_after(int n) { exit_after = n; delays = 0; }

RingbufHandle_t xRingbufferCreate(size_t size, RingbufferType_t type) {
    ring_obj.cap = size; head = tail = 0; stub_ring_items = stub_ring_bytes = 0;
    call("xRingbufferCreate(%zu, NOSPLIT) → coadă goală, capacitate %zu B", size, size);
    (void)type; return &ring_obj;
}
static int cost(size_t len) { return (int)(((len + 3) & ~(size_t)3) + RING_HEADER); }
BaseType_t xRingbufferSendFromISR(RingbufHandle_t rb, const void *item, size_t len, BaseType_t *woken) {
    (void)rb;
    if (len > ITEM_MAX || stub_ring_bytes + cost(len) > RING_CAPACITY || stub_ring_items >= RING_SLOTS) {
        call("xRingbufferSendFromISR(%zu B) → pdFALSE: coada este plină, pachetul se pierde", len);
        return pdFALSE;
    }
    memcpy(items[tail % RING_SLOTS], item, len); item_len[tail % RING_SLOTS] = len; tail++;
    stub_ring_items++; stub_ring_bytes += cost(len);
    call("xRingbufferSendFromISR(%zu B) → pdTRUE; pachete în coadă: %d, %d B ocupați din %d", len, stub_ring_items, stub_ring_bytes, RING_CAPACITY);
    if (woken) {
        *woken = (stub_ring_items == 1) ? pdTRUE : pdFALSE; /* simulare: task-ul UDP era blocat pe coada goală */
        if (*woken) call("(simulare) task-ul UDP aștepta pe coada goală, deci *woken = pdTRUE");
    }
    return pdTRUE;
}
void stub_ring_feed(const void *item, size_t len) {
    memcpy(items[tail % RING_SLOTS], item, len); item_len[tail % RING_SLOTS] = len; tail++;
    stub_ring_items++; stub_ring_bytes += cost(len);
}
void *xRingbufferReceive(RingbufHandle_t rb, size_t *len, TickType_t wait) {
    (void)rb; (void)wait;
    if (stub_ring_items == 0) { call("xRingbufferReceive(portMAX_DELAY) → coada este goală: task-ul UDP se blochează aici"); stub_end_scenario("task blocat pe coadă goală"); }
    pending_return = head % RING_SLOTS; head++; stub_ring_items--;
    *len = item_len[pending_return];
    call("xRingbufferReceive → scoate un pachet de %zu B (mai rămân %d)", *len, stub_ring_items);
    return items[pending_return];
}
void vRingbufferReturnItem(RingbufHandle_t rb, void *item) {
    (void)rb; (void)item;
    stub_ring_bytes -= cost(item_len[pending_return]);
    call("vRingbufferReturnItem → locul se eliberează (%d B ocupați)", stub_ring_bytes);
}

EventGroupHandle_t xEventGroupCreate(void) { stub_event_bits = 0; call("xEventGroupCreate() → toți biții sunt 0"); return &events_obj; }
EventBits_t xEventGroupGetBits(EventGroupHandle_t g) { (void)g; return stub_event_bits; }
EventBits_t xEventGroupSetBits(EventGroupHandle_t g, EventBits_t b) { (void)g; stub_event_bits |= b; call("xEventGroupSetBits(0x%x) → biți = 0x%x", b, stub_event_bits); return stub_event_bits; }
EventBits_t xEventGroupClearBits(EventGroupHandle_t g, EventBits_t b) { (void)g; stub_event_bits &= ~b; call("xEventGroupClearBits(0x%x) → biți = 0x%x", b, stub_event_bits); return stub_event_bits; }

void vTaskDelay(TickType_t t) {
    call("vTaskDelay(%u) → task-ul doarme %u tick = %u ms", t, t, t * 10);
    if (exit_after && ++delays >= exit_after) stub_end_scenario("sfârșitul demonstrației (bucla ar continua la nesfârșit)");
}
BaseType_t xTaskCreatePinnedToCore(TaskFunction_t fn, const char *name, uint32_t stack, void *arg, UBaseType_t prio, TaskHandle_t *h, BaseType_t core) {
    (void)fn; (void)arg; (void)h;
    call("xTaskCreatePinnedToCore(\"%s\", stivă %u B, prioritate %u, nucleul %d) → task creat", name, stack, prio, core);
    return pdTRUE;
}
void stub_yield_from_isr(void) { call("portYIELD_FROM_ISR() → schimbare imediată către task-ul cu prioritate mai mare"); }

int64_t esp_timer_get_time(void) { int64_t v = clock_us; clock_us += 10000; return v; }
esp_err_t nvs_flash_init(void) { call("nvs_flash_init() → ESP_OK (memoria de setări este gata)"); return ESP_OK; }
esp_err_t esp_netif_init(void) { call("esp_netif_init() → ESP_OK"); return ESP_OK; }
esp_err_t esp_event_loop_create_default(void) { call("esp_event_loop_create_default() → ESP_OK"); return ESP_OK; }
void *esp_netif_create_default_wifi_sta(void) { call("esp_netif_create_default_wifi_sta() → interfața de rețea a stației"); return NULL; }
esp_err_t esp_event_handler_register(esp_event_base_t b, int32_t id, esp_event_handler_t h, void *a) {
    (void)h; (void)a;
    call("esp_event_handler_register(%s, %s) → ESP_OK", b, id == ESP_EVENT_ANY_ID ? "ESP_EVENT_ANY_ID" : "IP_EVENT_STA_GOT_IP");
    return ESP_OK;
}
esp_err_t esp_wifi_init(const wifi_init_config_t *c) { (void)c; call("esp_wifi_init() → ESP_OK"); return ESP_OK; }
esp_err_t esp_wifi_set_storage(wifi_storage_t s) { (void)s; call("esp_wifi_set_storage(WIFI_STORAGE_RAM) → ESP_OK"); return ESP_OK; }
esp_err_t esp_wifi_set_mode(wifi_mode_t m) { (void)m; call("esp_wifi_set_mode(WIFI_MODE_STA) → ESP_OK"); return ESP_OK; }
esp_err_t esp_wifi_set_config(wifi_interface_t i, wifi_config_t *c) { (void)i; call("esp_wifi_set_config(ssid=\"%s\", parola=\"%s\") → ESP_OK", (char *)c->sta.ssid, (char *)c->sta.password); return ESP_OK; }
esp_err_t esp_wifi_start(void) { call("esp_wifi_start() → ESP_OK; biblioteca va emite WIFI_EVENT_STA_START"); return ESP_OK; }
esp_err_t esp_wifi_connect(void) { call("esp_wifi_connect() → ESP_OK; începe conectarea la router"); return ESP_OK; }
esp_err_t esp_wifi_set_ps(wifi_ps_type_t t) { (void)t; call("esp_wifi_set_ps(WIFI_PS_NONE) → ESP_OK; radioul nu mai doarme"); return ESP_OK; }
esp_err_t esp_wifi_set_promiscuous_filter(const wifi_promiscuous_filter_t *f) { call("esp_wifi_set_promiscuous_filter(mască = 0x%08X) → ESP_OK", f->filter_mask); return ESP_OK; }
esp_err_t esp_wifi_set_promiscuous(bool en) { call("esp_wifi_set_promiscuous(%s) → ESP_OK", en ? "true" : "false"); return ESP_OK; }
esp_err_t esp_wifi_set_csi_config(const wifi_csi_config_t *c) {
    call("esp_wifi_set_csi_config(lltf=%d, htltf=%d, stbc_htltf2=%d, ltf_merge=%d, channel_filter=%d, manu_scale=%d, shift=%d) → ESP_OK",
         c->lltf_en, c->htltf_en, c->stbc_htltf2_en, c->ltf_merge_en, c->channel_filter_en, c->manu_scale, c->shift);
    return ESP_OK;
}
esp_err_t esp_wifi_set_csi_rx_cb(wifi_csi_cb_t cb, void *ctx) { (void)cb; (void)ctx; call("esp_wifi_set_csi_rx_cb(on_csi) → ESP_OK; biblioteca știe ce funcție să apeleze"); return ESP_OK; }
esp_err_t esp_wifi_set_csi(bool en) { call("esp_wifi_set_csi(%s) → ESP_OK; măsurătorile CSI pornesc", en ? "true" : "false"); return ESP_OK; }
esp_err_t esp_wifi_80211_tx(wifi_interface_t i, const void *buf, int len, bool seq) {
    const unsigned char *b = buf; (void)i; (void)seq;
    call("esp_wifi_80211_tx(%d B) → cadru trimis în aer: tip 0x%02x, destinație %02x:%02x:%02x:%02x:%02x:%02x, sursă %02x:%02x:%02x:%02x:%02x:%02x",
         len, b[0], b[4], b[5], b[6], b[7], b[8], b[9], b[10], b[11], b[12], b[13], b[14], b[15]);
    return ESP_OK;
}

int stub_socket(int d, int t, int p) { (void)d; (void)t; (void)p; stub_sock_open = 1; call("socket(AF_INET, SOCK_DGRAM) → descriptor 3"); return 3; }
int stub_setsockopt(int s, int l, int o, const void *v, socklen_t n) { (void)s; (void)l; (void)o; (void)v; (void)n; call("setsockopt(SO_BROADCAST = 1) → 0"); return 0; }
ssize_t stub_sendto(int s, const void *b, size_t n, int f, const struct sockaddr *a, socklen_t l) {
    const struct sockaddr_in *in = (const struct sockaddr_in *)a; (void)b; (void)f; (void)l;
    call("sendto(socket %d, %zu B → %s:%d) → datagramă UDP trimisă", s, n, inet_ntoa(in->sin_addr), ntohs(in->sin_port));
    return (ssize_t)n;
}
