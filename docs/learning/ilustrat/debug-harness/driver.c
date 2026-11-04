/* Rulează funcțiile din main.c (incluse nemodificat) pe PC, cu bibliotecile simulate din stub/. */
#include <setjmp.h>
#include "main.c"

extern jmp_buf stub_jmp;

static void __attribute__((noinline)) poison_stack(void) {
    volatile unsigned char junk[4096];
    memset((void *)junk, 0xCD, sizeof(junk));
}

static int8_t pattern_buf[256];
static wifi_csi_info_t make_info(uint16_t len, int rssi) {
    wifi_csi_info_t info;
    memset(&info, 0, sizeof(info));
    for (int i = 0; i < 256; i++) pattern_buf[i] = (int8_t)(((i * 37 + 11) % 200) - 100);
    info.rx_ctrl.rssi = rssi;
    info.rx_ctrl.channel = 6;
    info.buf = pattern_buf;
    info.len = len;
    return info;
}
static void feed_packets(int count) {
    for (int i = 0; i < count; i++) {
        csi_packet_t p;
        memset(&p, 0, sizeof(p));
        p.magic = FRAME_MAGIC; p.node_id = NODE_ID; p.rssi_dbm = -52 + i; p.timestamp_us = 5000000u + 10000u * i; p.seq = (uint16_t)i;
        for (int k = 0; k < CSI_BYTES; k++) p.csi_iq[k] = pattern_buf[k];
        stub_ring_feed(&p, sizeof(p));
    }
}
static void setup(void) {
    csi_queue = xRingbufferCreate(CSI_QUEUE_BYTES, RINGBUF_TYPE_NOSPLIT);
    wifi_events = xEventGroupCreate();
    next_seq = 0;
    stub_log_len = 0;
}

void scenario_on_csi_normal(void) { setup(); wifi_csi_info_t info = make_info(128, -52); poison_stack(); on_csi(NULL, &info); }
void scenario_on_csi_long(void) { setup(); wifi_csi_info_t info = make_info(200, -52); poison_stack(); on_csi(NULL, &info); }
void scenario_on_csi_empty(void) { setup(); wifi_csi_info_t info = make_info(0, -52); poison_stack(); on_csi(NULL, &info); }
void scenario_on_csi_two(void) {
    setup(); wifi_csi_info_t a = make_info(128, -52), b = make_info(128, -47);
    poison_stack(); on_csi(NULL, &a); poison_stack(); on_csi(NULL, &b);
}
void scenario_on_csi_full(void) {
    setup(); wifi_csi_info_t info = make_info(128, -52);
    for (int i = 0; i < 200; i++) { csi_packet_t p; memset(&p, 0, sizeof(p)); if (stub_ring_bytes + 148 > CSI_QUEUE_BYTES) break; stub_ring_feed(&p, sizeof(p)); }
    stub_log_len = 0; poison_stack(); on_csi(NULL, &info);
}
void scenario_probe(void) { setup(); stub_set_exit_after(2); poison_stack(); probe_sender_task(NULL); }
void scenario_udp_offline(void) { setup(); feed_packets(2); stub_log_len = 0; poison_stack(); udp_sender_task(NULL); }
void scenario_udp_online(void) { setup(); feed_packets(2); xEventGroupSetBits(wifi_events, WIFI_CONNECTED_BIT); stub_log_len = 0; poison_stack(); udp_sender_task(NULL); }
void scenario_ev_start(void) { setup(); stub_log_len = 0; poison_stack(); on_wifi_event(NULL, WIFI_EVENT, WIFI_EVENT_STA_START, NULL); }
void scenario_ev_gotip(void) {
    setup(); ip_event_got_ip_t ev; memset(&ev, 0, sizeof(ev)); ev.ip_info.ip.addr = 0x2A01A8C0u; /* 192.168.1.42 */
    stub_log_len = 0; poison_stack(); on_wifi_event(NULL, IP_EVENT, IP_EVENT_STA_GOT_IP, &ev);
}
void scenario_ev_disc(void) { setup(); xEventGroupSetBits(wifi_events, WIFI_CONNECTED_BIT); stub_log_len = 0; poison_stack(); on_wifi_event(NULL, WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL); }
void scenario_init_wifi(void) { stub_log_len = 0; poison_stack(); init_wifi(); }
void scenario_init_csi(void) { stub_log_len = 0; poison_stack(); init_csi(); }
void scenario_boot(void) { stub_log_len = 0; poison_stack(); app_main(); }

struct { const char *name; void (*fn)(void); } SCENARIOS[] = {
    {"on_csi_normal", scenario_on_csi_normal}, {"on_csi_long", scenario_on_csi_long}, {"on_csi_empty", scenario_on_csi_empty},
    {"on_csi_two", scenario_on_csi_two}, {"on_csi_full", scenario_on_csi_full}, {"probe", scenario_probe},
    {"udp_offline", scenario_udp_offline}, {"udp_online", scenario_udp_online}, {"ev_start", scenario_ev_start},
    {"ev_gotip", scenario_ev_gotip}, {"ev_disc", scenario_ev_disc}, {"init_wifi", scenario_init_wifi},
    {"init_csi", scenario_init_csi}, {"boot", scenario_boot}, {0, 0}
};

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "scenariu lipsă\n"); return 2; }
    for (int i = 0; SCENARIOS[i].name; i++) {
        if (strcmp(argv[1], SCENARIOS[i].name) == 0) {
            if (setjmp(stub_jmp) == 0) SCENARIOS[i].fn();
            fwrite(stub_log_buf, 1, stub_log_len, stdout);
            return 0;
        }
    }
    fprintf(stderr, "scenariu necunoscut: %s\n", argv[1]);
    return 2;
}
