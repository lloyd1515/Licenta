#include "udp_transport.h"
#include "csi_log.h"
#include "csi_packet.h"
#include "esp_log.h"
#include "lwip/sockets.h"
#include "freertos/task.h"

// Parametrii task-ului UDP
#define UDP_TASK_STACK 4096
#define UDP_TASK_PRIORITY 10
#define UDP_TASK_CORE 1

// Task: coada catre UDP
static void udp_sender_task(void *arg) {
    RingbufHandle_t queue = arg;
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    if (sock < 0) ESP_LOGE(CSI_LOG_TAG, "UDP socket failed: errno %d", errno);
    setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &(int){1}, sizeof(int));
    struct sockaddr_in dest = {.sin_family = AF_INET, .sin_port = htons(CONFIG_CSI_UDP_PORT),
                               .sin_addr.s_addr = inet_addr(CONFIG_CSI_UDP_HOST)};
    size_t size;
    while (1) {
        csi_packet_t *packet = xRingbufferReceive(queue, &size, portMAX_DELAY);
        if (!packet) continue;
        sendto(sock, packet, sizeof(*packet), 0, (struct sockaddr *)&dest, sizeof(dest));
        vRingbufferReturnItem(queue, packet);
    }
}

// Creeaza task-ul UDP
void udp_transport_start(RingbufHandle_t queue) {
    xTaskCreatePinnedToCore(udp_sender_task, "udp_sender", UDP_TASK_STACK, queue, UDP_TASK_PRIORITY, NULL,
                            UDP_TASK_CORE);
}
