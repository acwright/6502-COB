// The loopback rig's test console (pico2-loopback builds only).
#pragma once

// Runs the console for ever. `banner` prints the firmware's banner.
void loopback_main(void (*banner)(void));
