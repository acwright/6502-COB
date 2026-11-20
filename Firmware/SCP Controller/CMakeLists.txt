cmake_minimum_required(VERSION 3.21)

# One tree, two platforms. Pick a build with a preset (CMakePresets.json):
#   host, host-asan     macOS: the controller's core and its unit tests
#   board               the Storage Card Pro 1.1 and the ACE SD Adapter 1.1 (a Pico 2 on each)
#   pico2-loopback      a Pico 2 with seven jumper wires: the bus, timed by a bus exerciser
#   pico2-media         a Pico 2 with an SD card breakout and a W25Q flash breakout
#   pico2-breadboard    the boards' firmware on a Pico 2 with the media rig's breakouts
set(FW_PLATFORM host CACHE STRING "host or rp2350")
set_property(CACHE FW_PLATFORM PROPERTY STRINGS host rp2350)
set(FW_BOARD ac6502_sd_pico2 CACHE STRING "The rp2350 target: a header in rp2350/boards")

if(FW_PLATFORM STREQUAL "rp2350")
    set(PICO_PLATFORM rp2350-arm-s)
    set(PICO_BOARD ${FW_BOARD})
    list(APPEND PICO_BOARD_HEADER_DIRS ${CMAKE_CURRENT_LIST_DIR}/rp2350/boards)
    include(cmake/sdk.cmake)
elseif(NOT FW_PLATFORM STREQUAL "host")
    message(FATAL_ERROR "FW_PLATFORM must be host or rp2350, not '${FW_PLATFORM}'")
endif()

# The firmware's name, from product.h: the one file the two copies differ in.
file(STRINGS ${CMAKE_CURRENT_LIST_DIR}/product.h _line REGEX "^#define PRODUCT_FIRMWARE ")
string(REGEX REPLACE "^#define PRODUCT_FIRMWARE +\"([^\"]+)\".*$" "\\1" FW_NAME "${_line}")

project(sd_controller C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
# The SDK's own sources use GNU extensions; the host build is strict C11, which
# keeps core/ free of anything the Mac wouldn't compile.
if(FW_PLATFORM STREQUAL "host")
    set(CMAKE_C_EXTENSIONS OFF)
else()
    set(CMAKE_C_EXTENSIONS ON)
endif()
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Warnings for this firmware's code only; the SDK isn't held to them.
add_library(fw_warnings INTERFACE)
target_compile_options(fw_warnings INTERFACE -Wall -Wextra)
if(FW_PLATFORM STREQUAL "host")
    target_compile_options(fw_warnings INTERFACE -Werror)
    option(FW_SANITIZE "AddressSanitizer and UBSan" OFF)
    if(FW_SANITIZE)
        add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=all)
        add_link_options(-fsanitize=address,undefined)
    endif()
else()
    pico_sdk_init()
endif()

add_subdirectory(core)

if(FW_PLATFORM STREQUAL "host")
    enable_testing()
    add_subdirectory(tests/unit)
    add_subdirectory(tests/bios)
else()
    add_subdirectory(rp2350)
endif()
