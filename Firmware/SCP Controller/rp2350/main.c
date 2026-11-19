// The controller's start-up. So far: the LEDs and the USB serial port's banner.
// The bus pins are left as they come out of reset, undriven, so the board's
// pull resistors answer every read with $80 (BSY).
#include <stdio.h>

#include "hardware/gpio.h"
#include "pico/binary_info.h"
#include "pico/stdlib.h"

#include "fw_info.h"
#include "loopback.h"
#include "mediarig.h"
#include "product.h"
#include "source_hash.h"
#include "version.h"

// The build's source hash, where Tools/firmware/twins.py finds it in the .uf2.
const char fw_source_marker[] = "AC6502-SRC:" FW_SOURCE_HASH;

// The program's name comes from PICO_PROGRAM_NAME (rp2350/CMakeLists.txt): the
// SDK declares one of its own, which would come first.
bi_decl(bi_program_description(PRODUCT_NAME ": an SD card and a built-in drive, answering as CompactFlash"));
bi_decl(bi_program_version_string(FW_VERSION));
bi_decl(bi_program_url(PRODUCT_REPO_URL));
bi_decl(bi_program_build_attribute(FW_TARGET_NAME));

static void leds_init(void)
{
    gpio_init(FW_PIN_LED_SD);
    gpio_set_dir(FW_PIN_LED_SD, GPIO_OUT);
    gpio_init(FW_PIN_LED_ACT);
    gpio_set_dir(FW_PIN_LED_ACT, GPIO_OUT);
    // On the Storage Card Pro, LED_ACT lights D1 and the off-board LED on J1:
    // about 7 mA together, over the default 4 mA.
    gpio_set_drive_strength(FW_PIN_LED_ACT, GPIO_DRIVE_STRENGTH_8MA);
}

static void banner(void)
{
    char buf[200];
    fw_banner(buf, sizeof buf, PRODUCT_FIRMWARE, FW_VERSION,
              fw_source_marker + sizeof "AC6502-SRC:" - 1, FW_TARGET_NAME);
    fputs(buf, stdout);
}

int main(void)
{
    leds_init();
    stdio_init_all();

    // Lamp test: both LEDs for a quarter of a second.
    gpio_put(FW_PIN_LED_SD, 1);
    gpio_put(FW_PIN_LED_ACT, 1);
    sleep_ms(250);
    gpio_put(FW_PIN_LED_SD, 0);
    gpio_put(FW_PIN_LED_ACT, 0);

#if FW_HAS_EXERCISER
    loopback_main(banner);
#endif
#if FW_HAS_MEDIA_CONSOLE
    mediarig_main(banner);
#endif
    bool told = false;
    for (;;) {
        bool connected = stdio_usb_connected();
        if (connected && !told)
            banner();
        told = connected;
        sleep_ms(50);
    }
}
