// Copyright 2024-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#pragma once

#include <stdint.h>

// This is fixed due to the VPU
#define TD_BLOCK_FIR_LENGTH 8

void td_block_fir_compute_8_tap(
    int32_t * output_data,
    int32_t * input_data, 
    int32_t coefs[8],
    unsigned length
);


