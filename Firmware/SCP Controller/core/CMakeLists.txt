# The controller's core: plain C11, no SDK, so the same code runs on the RP2350
# and in the unit tests on the Mac.
add_library(fw_core STATIC
    ata.c
    drive.c
    flashdisk.c
    fw_info.c
    identify.c
    media.c
    nor.c
    sdcard.c
)
target_include_directories(fw_core PUBLIC ${CMAKE_CURRENT_LIST_DIR} ${CMAKE_SOURCE_DIR})
target_link_libraries(fw_core PRIVATE fw_warnings)
