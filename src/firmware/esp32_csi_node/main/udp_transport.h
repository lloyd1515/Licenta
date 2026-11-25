#pragma once
#include "freertos/FreeRTOS.h"
#include "freertos/ringbuf.h"

// Porneste trimiterea UDP
void udp_transport_start(RingbufHandle_t queue);
