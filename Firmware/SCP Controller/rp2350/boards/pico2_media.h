// A Pico 2 as the media rig: an Adafruit microSD breakout on the board's SD
// pins, and a W25Q flash breakout on SPI1's pins the Pico 2 brings out. A Pico
// 2's header has no GPIO23-25, so the flash can't use the board's pins. No bus:
// the core is driven over USB.
//
//   SD breakout:    GPIO16 DO, GPIO17 CS, GPIO18 CLK, GPIO19 DI, GPIO20 CD; 5V from VBUS
//   Flash breakout: GPIO28 DO, GPIO15 CS, GPIO26 CLK, GPIO27 DI; 3.3 V from 3V3(OUT)
//
// A Pico 2 with a damaged GPIO26 pad (one that drives high but not low, as the
// first rig's did) can take the flash clock on GPIO14 instead, another of SPI1's
// clock pins: the media rig has no bus. Run "pins" and "adc" on a new Pico 2 first.

// pico_cmake_set PICO_PLATFORM=rp2350
// pico_cmake_set_default PICO_FLASH_SIZE_BYTES = (4 * 1024 * 1024)
// pico_cmake_set_default PICO_RP2350_A2_SUPPORTED = 1

#ifndef _BOARDS_PICO2_MEDIA_H
#define _BOARDS_PICO2_MEDIA_H

#include "boards/pico2.h"

#define FW_TARGET_NAME "Pico 2: SD card and flash rig"

#define FW_HAS_BUS      0
#define FW_HAS_MEDIA_CONSOLE 1  // rp2350/mediarig.c

#define FW_HAS_SD       1
#define FW_SD_SPI       spi0
#define FW_PIN_SD_MISO  16
#define FW_PIN_SD_CS    17
#define FW_PIN_SD_SCK   18
#define FW_PIN_SD_MOSI  19
#define FW_PIN_SD_CD    20
#define FW_SD_CD_PULLUP 1       // the breakout has no pull-up on CD
#define FW_SD_CD_CARD_IN 1      // the Adafruit breakout grounds CD with no card in, so a card reads high

#define FW_HAS_FLASH    1
#define FW_FLASH_SPI    spi1
#define FW_PIN_FLASH_MISO 28
#define FW_PIN_FLASH_CS   15
#define FW_PIN_FLASH_SCK  26
#define FW_PIN_FLASH_MOSI 27

#define FW_PIN_LED_SD   21
#define FW_PIN_LED_ACT  22

// The SPI clocks after start-up. The SD card's is half the board's: through the
// Adafruit breakout's level shifter the card's replies come back too late for
// 25 MHz (writes' data responses misread, 19 November 2026); 18.75 MHz passed,
// and 12.5 MHz leaves a step to spare.
#define FW_SD_HZ        12500000
#define FW_FLASH_HZ     25000000

#endif
