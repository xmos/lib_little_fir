// Copyright 2020-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#if defined(__XS3A__)

.text
.align 16;
.issue_mode dual

/*  
void td_block_fir_compute_8_tap(
    int32_t * output_data,
    int32_t * input_data, 
    int32_t coefs[8],
    unsigned length
);

*/

#define FUNCTION_NAME   td_block_fir_compute_8_tap
#define NSTACKWORDS     2

#define output_data_p      r0
#define input_data_p       r1
#define coefs_p            r2
#define length             r3

#define s r4
#define thirtytwo r5

#define t r11

.cc_top FUNCTION_NAME.function,FUNCTION_NAME
FUNCTION_NAME:
FUNCTION_NAME_asm:
  dualentsp NSTACKWORDS
  std r5, r4, sp[0]
  {vldc coefs_p[0] ; shr length, length, 3}
  {sub length, length, 1; ldc thirtytwo, 32}
  {ldc s, 64 - 4; add input_data_p, input_data_p, thirtytwo} 
  {vclrdr; sub input_data_p, input_data_p, 4}
td_block_fir_compute_8_tap_loop:
  
  {vlmaccr input_data_p[0] ; sub input_data_p, input_data_p, 4 }
  {vlmaccr input_data_p[0] ; sub input_data_p, input_data_p, 4 }
  {vlmaccr input_data_p[0] ; sub input_data_p, input_data_p, 4 }
  {vlmaccr input_data_p[0] ; sub input_data_p, input_data_p, 4 }
  {vlmaccr input_data_p[0] ; sub input_data_p, input_data_p, 4 }
  {vlmaccr input_data_p[0] ; sub input_data_p, input_data_p, 4 }
  {vlmaccr input_data_p[0] ; sub input_data_p, input_data_p, 4 }
  {vlmaccr input_data_p[0] ; add input_data_p, input_data_p, s }

  //{vlsat t[0] ; nop}
  vstr output_data_p[0]
  {vclrdr; add output_data_p, output_data_p, thirtytwo}

  {bt length, td_block_fir_compute_8_tap_loop; sub length, length, 1}

  ldd r5, r4, sp[0]
  { nop                ; retsp NSTACKWORDS           }

.L_func_end_unpack:
.cc_bottom FUNCTION_NAME.function

.global FUNCTION_NAME
.type FUNCTION_NAME,@function
.set FUNCTION_NAME.nstackwords,NSTACKWORDS;     .global FUNCTION_NAME.nstackwords
.set FUNCTION_NAME.maxcores,1;                  .global FUNCTION_NAME.maxcores
.set FUNCTION_NAME.maxtimers,0;                 .global FUNCTION_NAME.maxtimers
.set FUNCTION_NAME.maxchanends,0;               .global FUNCTION_NAME.maxchanends
.size FUNCTION_NAME,.L_func_end_unpack - FUNCTION_NAME

#undef NSTACKWORDS
#undef FUNCTION_NAME

#endif //defined(__XS3A__)
