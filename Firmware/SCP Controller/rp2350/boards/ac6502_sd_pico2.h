// The Storage Card Pro 1.1 and the ACE SD Adapter 1.1: one circuit, one pin map.
//
// A Raspberry Pi Pico 2 module on header pins, with the 6502 bus through a
// 74LVC4245A and a 74LVC541, the SD card on its own 3.3 V regulator, and a W25Q
// flash for the built-in drive. On the ACE SD Adapter the Pico is on the Bottom
// board and the SD card and LEDs on the Top, joined by J7-J10; the pins are the
// same. The Pico SDK reads this file as its board header
// (PICO_BOARD=ac6502_sd_pico2), so it holds preprocessor lines only.
//
// It includes the SDK's own boards/pico2.h, so the SDK knows the module: its
// 4 MB program flash, and the pins that stay on the module (GPIO23 the
// regulator's power-save, GPIO24 VBUS sense, GPIO25 its LED, GPIO29 VSYS sense).

// pico_cmake_set PICO_PLATFORM=rp2350
// pico_cmake_set_default PICO_FLASH_SIZE_BYTES = (4 * 1024 * 1024)
// pico_cmake_set_default PICO_RP2350_A2_SUPPORTED = 1

#ifndef _BOARDS_AC6502_SD_PICO2_H
#define _BOARDS_AC6502_SD_PICO2_H

#include "boards/pico2.h"

// No default UART, I2C or SPI: pico2.h puts the UART on GPIO0 and GPIO1, which
// are D0 and D1 on the 6502 bus and must never be driven by anything but the
// bus program, and its I2C and SPI on bus and SD card pins.
#undef PICO_DEFAULT_UART
#undef PICO_DEFAULT_UART_TX_PIN
#undef PICO_DEFAULT_UART_RX_PIN
#undef PICO_DEFAULT_I2C
#undef PICO_DEFAULT_I2C_SDA_PIN
#undef PICO_DEFAULT_I2C_SCL_PIN
#undef PICO_DEFAULT_SPI
#undef PICO_DEFAULT_SPI_SCK_PIN
#undef PICO_DEFAULT_SPI_TX_PIN
#undef PICO_DEFAULT_SPI_RX_PIN
#undef PICO_DEFAULT_SPI_CSN_PIN

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
#define FW_BUS_INTERNAL_PULLS 0 // R13-R20, 4.7k: D7 up, D0-D6 down

// The SD card on SPI0.
#define FW_HAS_SD       1
#define FW_SD_SPI       spi0
#define FW_PIN_SD_MISO  16      // DAT0
#define FW_PIN_SD_CS    17      // DAT3
#define FW_PIN_SD_SCK   18      // CLK
#define FW_PIN_SD_MOSI  19      // CMD
#define FW_PIN_SD_CD    20      // R4 pulls it up; the socket's switch grounds it with a card in
#define FW_SD_CD_PULLUP 0
#define FW_SD_CD_CARD_IN 0      // the level CD reads with a card in

// The built-in drive, a W25Q flash, on SPI1.
#define FW_HAS_FLASH    1
#define FW_FLASH_SPI    spi1
#define FW_PIN_FLASH_MISO 28    // DO
#define FW_PIN_FLASH_CS   15
#define FW_PIN_FLASH_SCK  26
#define FW_PIN_FLASH_MOSI 27    // DI

// The LEDs, lit high. LED_ACT lights D1 and, on the card, the off-board LED on J1.
#define FW_PIN_LED_SD   21      // D2, green: the SD card is the medium answering
#define FW_PIN_LED_ACT  22      // D1, red: a medium is busy

// The SPI clocks after start-up. The SD card's is half its 25 MHz limit: at 25 MHz
// the card's replies have about 20 ns to come back, and the card alone may take
// 14 ns. A sector costs 0.2 ms more, against the 6502's 3.8 ms to move it at
// 2 MHz. To be tried again at 25 MHz on the first boards made.
#define FW_SD_HZ        12500000
#define FW_FLASH_HZ     25000000

#endif
