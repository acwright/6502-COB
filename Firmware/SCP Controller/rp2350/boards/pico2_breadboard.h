// A Pico 2 on a breadboard copy of the board, wired to the ACE's STORAGE
// header through a 74LVC4245A and a 74LVC541 as on the board. The bus, the SD
// card and the LEDs are on the board's pins; the flash is on the media rig's,
// since a Pico 2's header has no GPIO23-25.

// pico_cmake_set PICO_PLATFORM=rp2350
// pico_cmake_set_default PICO_FLASH_SIZE_BYTES = (4 * 1024 * 1024)
// pico_cmake_set_default PICO_RP2350_A2_SUPPORTED = 1

#ifndef _BOARDS_PICO2_BREADBOARD_H
#define _BOARDS_PICO2_BREADBOARD_H

#include "boards/pico2.h"

#define FW_TARGET_NAME "Pico 2: breadboard copy on the ACE"

#define FW_HAS_BUS      1
#define FW_PIN_D0       0
#define FW_PIN_RESB     8
#define FW_PIN_RB       9
#define FW_PIN_WB       10
#define FW_PIN_CS       11
#define FW_PIN_A2       12
#define FW_PIN_A1       13
#define FW_PIN_A0       14

#define FW_HAS_SD       1
#define FW_SD_SPI       spi0
#define FW_PIN_SD_MISO  16
#define FW_PIN_SD_CS    17
#define FW_PIN_SD_SCK   18
#define FW_PIN_SD_MOSI  19
#define FW_PIN_SD_CD    20
#define FW_SD_CD_PULLUP 1

#define FW_HAS_FLASH    1
#define FW_FLASH_SPI    spi1
#define FW_PIN_FLASH_MISO 28
#define FW_PIN_FLASH_CS   15
#define FW_PIN_FLASH_SCK  26
#define FW_PIN_FLASH_MOSI 27

#define FW_PIN_LED_SD   21
#define FW_PIN_LED_ACT  22

#endif
