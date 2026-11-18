// What the firmware says about itself: the banner on the USB serial port.
#pragma once

#include <stddef.h>

// Writes the banner into buf, at most size bytes with the terminating NUL, and
// returns the length the whole banner needs, as snprintf does:
//
//   SCP Controller 0.1.0 (source 0123456789ab), Pico 2: SD card and flash rig
//   Copyright (c) 2026 A.C. Wright Design
//
// source_hash is the 64-digit hash the build stamps in; the banner shows its
// first 12 digits, enough to tell builds apart.
int fw_banner(char *buf, size_t size, const char *firmware, const char *version,
              const char *source_hash, const char *target);
