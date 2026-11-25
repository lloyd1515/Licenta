#pragma once
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "esp_timer.h"
#include "esp_wifi_types.h"
#include "sdkconfig.h"

// Constantele pachetului v1
#define CSI_PACKET_MAGIC 0xA55A
#define CSI_IQ_BYTES 128

// Pachetul UDP de 138 octeti
typedef struct __attribute__((packed)) {
    uint16_t magic; uint8_t node_id; int8_t rssi_dbm; uint32_t timestamp_us; uint16_t seq;
    int8_t csi_iq[CSI_IQ_BYTES];
} csi_packet_t;
// Verifica pozitiile campurilor
_Static_assert(sizeof(csi_packet_t) == 138, "wire packet must be 138 bytes");
_Static_assert(offsetof(csi_packet_t, timestamp_us) == 4, "timestamp_us must start at byte 4");
_Static_assert(offsetof(csi_packet_t, seq) == 8, "seq must start at byte 8");
_Static_assert(offsetof(csi_packet_t, csi_iq) == 10, "csi_iq must start at byte 10");
_Static_assert(CONFIG_CSI_NODE_ID >= 0 && CONFIG_CSI_NODE_ID <= 255, "node_id must fit in one byte");

// Construieste pachetul din CSI
static inline csi_packet_t csi_packet_build(const wifi_csi_info_t *info, uint16_t seq) {
    csi_packet_t packet = {.magic = CSI_PACKET_MAGIC, .node_id = CONFIG_CSI_NODE_ID, .rssi_dbm = info->rx_ctrl.rssi,
                           .timestamp_us = (uint32_t)esp_timer_get_time(), .seq = seq};
    memcpy(packet.csi_iq, info->buf, info->len > CSI_IQ_BYTES ? CSI_IQ_BYTES : info->len);
    if (info->first_word_invalid) memset(packet.csi_iq, 0, 4);
    return packet;
}
