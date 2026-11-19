# Unit tests on the Mac, one executable per concern.
function(fw_unit_test name)
    add_executable(${name} ${name}.c)
    target_link_libraries(${name} PRIVATE fw_core fw_warnings)
    add_test(NAME ${name} COMMAND ${name} ${ARGN})
endfunction()

fw_unit_test(test_info)     # the banner, and product.h's strings
fw_unit_test(test_ata)      # the registers and commands, the worker played by hand
fw_unit_test(test_media)    # mirroring, the JEDEC ID, the built-in drive on a NOR chip
fw_unit_test(test_sdcard)   # the SD card's size from its CSD, and the bus's CRCs
fw_unit_test(test_drive)    # the two sides together: the BIOS's sequence, media, resets, IDENTIFY, LEDs
