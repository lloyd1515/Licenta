#pragma once
#include "freertos/FreeRTOS.h"
#include "freertos/ringbuf.h"

// Porneste promiscuu si CSI
void csi_capture_start(RingbufHandle_t queue);
