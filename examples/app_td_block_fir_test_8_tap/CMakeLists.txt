cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)
project(app_test)

set(APP_HW_TARGET XK-EVK-XU316)
set(APP_DEPENDENT_MODULES
    "lib_little_fir"
)
set(APP_PCA_ENABLE OFF)
set(EXAMPLE_BUILD_FLAGS ${EXTRA_BUILD_FLAGS} -fcomment-asm
                                             -Wall
                                             -O3
                                             -report
                                             -lquadflash
                                             -mcmodel=large
                                             -g
                                             -fxscope)

set(APP_COMPILER_FLAGS ${EXAMPLE_BUILD_FLAGS})

file(GLOB C_SRC CONFIGURE_DEPENDS RELATIVE ${CMAKE_CURRENT_LIST_DIR} src/*.c)

set(APP_C_SRCS
    "${C_SRC};${DSP_MAIN}")


set(APP_INCLUDES api src)
set(XMOS_SANDBOX_DIR ${CMAKE_CURRENT_LIST_DIR}/../../..)

XMOS_REGISTER_APP()
