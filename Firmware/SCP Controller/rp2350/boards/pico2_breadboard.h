// The boards' firmware on a bare Pico 2 with the media rig's breakouts: the
// boards' own header (ac6502_sd_pico2.h), but for card detect, which the
// Adafruit microSD breakout gives the other way up. The wiring is the media
// rig's (pico2_media.h), on the same pins as the boards. Nothing is on the bus
// pins, so the bus program runs but nothing reads it.
//
// It was first the build for a breadboard copy of the board on the ACE's
// STORAGE header, which was dropped (19 November 2026) for want of the board's
// level shifters.

// pico_cmake_set PICO_PLATFORM=rp2350
// pico_cmake_set_default PICO_FLASH_SIZE_BYTES = (4 * 1024 * 1024)
// pico_cmake_set_default PICO_RP2350_A2_SUPPORTED = 1

#ifndef _BOARDS_PICO2_BREADBOARD_H
#define _BOARDS_PICO2_BREADBOARD_H

#include "ac6502_sd_pico2.h"

#undef FW_TARGET_NAME
#define FW_TARGET_NAME "Pico 2: the boards' firmware on the media rig"

#undef FW_SD_CD_PULLUP
#define FW_SD_CD_PULLUP 1       // the breakout has no pull-up on CD
#undef FW_SD_CD_CARD_IN
#define FW_SD_CD_CARD_IN 1      // the Adafruit breakout grounds CD with no card in, so a card reads high

#endif
