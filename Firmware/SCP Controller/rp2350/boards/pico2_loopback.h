// A Pico 2 as the bus loopback rig: the bus on the board's pins, and a bus
// exerciser on GPIO15-21 driving the controls through seven jumper wires:
//
//   GPIO15 -> GPIO8  RESB      GPIO19 -> GPIO12 A2
//   GPIO16 -> GPIO9  RB        GPIO20 -> GPIO13 A1
//   GPIO17 -> GPIO10 WB        GPIO21 -> GPIO14 A0
//   GPIO18 -> GPIO11 CS
//
// No SD card and no flash: the disk is in RAM.

// pico_cmake_set PICO_PLATFORM=rp2350
// pico_cmake_set_default PICO_FLASH_SIZE_BYTES = (4 * 1024 * 1024)
// pico_cmake_set_default PICO_RP2350_A2_SUPPORTED = 1

#ifndef _BOARDS_PICO2_LOOPBACK_H
#define _BOARDS_PICO2_LOOPBACK_H

#include "boards/pico2.h"

#define FW_TARGET_NAME "Pico 2: bus loopback rig"

#define FW_HAS_BUS      1
#define FW_PIN_D0       0
#define FW_PIN_RESB     8
#define FW_PIN_RB       9
#define FW_PIN_WB       10
#define FW_PIN_CS       11
#define FW_PIN_A2       12
#define FW_PIN_A1       13
#define FW_PIN_A0       14

#define FW_HAS_EXERCISER 1
#define FW_PIN_EXER_BASE 15     // GPIO15-21 drive GPIO8-14, in the same order

#define FW_HAS_SD       0
#define FW_HAS_FLASH    0

#define FW_PIN_LED_SD   25      // the Pico 2's own LED
#define FW_PIN_LED_ACT  22

#endif
