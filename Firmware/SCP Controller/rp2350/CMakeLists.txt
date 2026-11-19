# The firmware for one rp2350 target (FW_BOARD).

# The source hash, rewritten when any file that goes into the firmware changes.
set(FW_GENERATED ${CMAKE_CURRENT_BINARY_DIR}/generated)
add_custom_target(fw_source_hash
    COMMAND ${CMAKE_COMMAND} -DROOT=${CMAKE_SOURCE_DIR} -DOUT=${FW_GENERATED}/source_hash.h
            -P ${CMAKE_SOURCE_DIR}/cmake/source_hash.cmake
    BYPRODUCTS ${FW_GENERATED}/source_hash.h
    COMMENT "Hashing the firmware's sources"
    VERBATIM)

add_executable(firmware
    main.c
    bus.c
    controller.c
    exerciser.c
    flash.c
    loopback.c
    mediarig.c
    patterndisk.c
    sd.c
    serve.c
)
pico_generate_pio_header(firmware ${CMAKE_CURRENT_LIST_DIR}/bus.pio)
pico_generate_pio_header(firmware ${CMAKE_CURRENT_LIST_DIR}/exerciser.pio)
add_dependencies(firmware fw_source_hash)
set_target_properties(firmware PROPERTIES OUTPUT_NAME ${FW_NAME})
target_compile_definitions(firmware PRIVATE "PICO_PROGRAM_NAME=\"${FW_NAME}\"")
target_include_directories(firmware PRIVATE ${FW_GENERATED} ${CMAKE_SOURCE_DIR})
target_link_libraries(firmware PRIVATE
    fw_core
    fw_warnings
    pico_stdlib
    pico_multicore
    pico_unique_id
    hardware_adc
    hardware_clocks
    hardware_dma
    hardware_gpio
    hardware_pio
    hardware_spi
)

# The whole program runs from SRAM, so the bus loop never waits on the program flash.
pico_set_binary_type(firmware copy_to_ram)

# USB is the only console: the UART's default pins are D0 and D1 on the bus.
pico_enable_stdio_usb(firmware 1)
pico_enable_stdio_uart(firmware 0)

pico_add_extra_outputs(firmware)
