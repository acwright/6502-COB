// The Storage Card Pro 1.1 and the ACE SD Adapter 1.1: one circuit, one pin map.
//
// An RP2350A with a W25Q128JVS (16 MB) program flash and Raspberry Pi's 12 MHz
// crystal circuit, as on the Pico 2. The Pico SDK reads this file as its board
// header (PICO_BOARD=ac6502_sd), so it holds preprocessor lines only.
//
// Derived from the Pico SDK's boards/pico2.h:
// Copyright (c) 2024 Raspberry Pi (Trading) Ltd.
// SPDX-License-Identifier: BSD-3-Clause

// pico_cmake_set PICO_PLATFORM=rp2350

#ifndef _BOARDS_AC6502_SD_H
#define _BOARDS_AC6502_SD_H

#define PICO_RP2350A 1

// No default UART, I2C, SPI or LED: GPIO0 and GPIO1 are D0 and D1 on the 6502
// bus, and must never be driven by anything but the bus program.

#define PICO_FLASH_SPI_CLKDIV 2
// pico_cmake_set_default PICO_FLASH_SIZE_BYTES = (16 * 1024 * 1024)
#ifndef PICO_FLASH_SIZE_BYTES
#define PICO_FLASH_SIZE_BYTES (16 * 1024 * 1024)
#endif

// pico_cmake_set_default PICO_RP2350_A2_SUPPORTED = 1
#ifndef PICO_RP2350_A2_SUPPORTED
#define PICO_RP2350_A2_SUPPORTED 1
#endif

#define FW_TARGET_NAME "Storage Card Pro 1.1 / ACE SD Adapter 1.1"

// The 6502 bus. D0-D7 come through the 74LVC4245A; the controls through the
// 74LVC541, in this order, with A0-A2 reversed.
#define FW_HAS_BUS      1
#define FW_PIN_D0       0       // D0-D7 on GPIO0-7
#define FW_PIN_RESB     8
#define FW_PIN_RB       9
#define FW_PIN_WB       10
#define FW_PIN_CS       11      // IO4B on the ACE, the window jumper's select on the card
#define FW_PIN_A2       12
#define FW_PIN_A1       13
#define FW_PIN_A0       14

// The SD card on SPI0.
#define FW_HAS_SD       1
#define FW_SD_SPI       spi0
#define FW_PIN_SD_MISO  16      // DAT0
#define FW_PIN_SD_CS    17      // DAT3
#define FW_PIN_SD_SCK   18      // CLK
#define FW_PIN_SD_MOSI  19      // CMD
#define FW_PIN_SD_CD    20      // low with a card in; R4 pulls it up

// The built-in drive, a W25Q flash, on SPI1.
#define FW_HAS_FLASH    1
#define FW_FLASH_SPI    spi1
#define FW_PIN_FLASH_MISO 24    // DO
#define FW_PIN_FLASH_CS   25
#define FW_PIN_FLASH_SCK  26
#define FW_PIN_FLASH_MOSI 27    // DI

// The LEDs, lit high. LED_ACT lights D1 and, on the card, the off-board LED on J1.
#define FW_PIN_LED_SD   21      // D2, green: the SD card is the medium answering
#define FW_PIN_LED_ACT  22      // D1, red: a medium is busy

#endif
