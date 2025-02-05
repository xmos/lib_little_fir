// Copyright 2024-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "td_block_fir.h"


#include "test_0.h"

void td_block_fir_compute_8_tap_ref(
    int32_t * output_data,
    int32_t * input_data, 
    int32_t coefs[8],
    unsigned output_length
){
    for(int i=0;i<output_length;i++){
        int64_t sum = 0;
        for(int j=0;j<8;j++){
            sum += ((int64_t)input_data[i+j] * coefs[j])>>30;
        }
        output_data[i] = sum;
    }

}

#define OUTPUT_LENGTH (2<<9)

int main(void){

while(1){
    int32_t input_data[OUTPUT_LENGTH+8];
    for(int i=0;i<OUTPUT_LENGTH+8;i++){
        input_data[i] = rand()>>4;
    }

    int32_t output_data[OUTPUT_LENGTH];
    memset(output_data, 0, sizeof(output_data));  
    int32_t output_data_ref[OUTPUT_LENGTH];
    memset(output_data_ref, 0, sizeof(output_data_ref));  


    td_block_fir_compute_8_tap_ref(output_data_ref, input_data, coefs_test_0, OUTPUT_LENGTH);
    td_block_fir_compute_8_tap(output_data, input_data, coefs_test_0, OUTPUT_LENGTH);
    
    for(int i=0;i<OUTPUT_LENGTH;i++){
        int delta = output_data_ref[i] - output_data[i];
        delta = delta *delta;
        if(delta > 64)
            printf("Error\n");
    }
    printf("passed\n");
}
    exit(0);
}