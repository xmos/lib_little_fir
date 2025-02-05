# lib_little_fir

To build the app:
 - goto /examples/app_td_block_fir_test_8_tap
 - goto the src dir
 - make sure numpy and scipy are installed: pip install numpy/scipy if need be, scipy is only for the example
 - ./gen.sh -this builds an example FIR 
 - got back down to the base of the example, cd ..
 - either
    - xmake && xsim ./bin/app_test.xe
    or
    - cmake -B build && xmake && xsim ./bin/app_test.xe


Note, xmake alone will warn about stuff like:

/Applications/XMOS_XTC_15.3.0/build/xcommon/module_xcommon/build/../build/Makefile.common1:738: warning: overriding commands for target `bin/'
/Applications/XMOS_XTC_15.3.0/build/xcommon/module_xcommon/build/../build/Makefile.common1:731: warning: ignoring old commands for target `bin/'

but it seems to be fine!