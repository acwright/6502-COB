// The controller as the boards run it (the board build, and the breadboard copy):
// the bus on PIO0 and core 1 (bus.c), and the worker on core 0: the SD card, the
// built-in drive, the drive's jobs, power-on and the LEDs. USB is the diagnostic
// port: a banner when a terminal connects, and a report on any key.
#include "controller.h"

#include "pico.h"           // the board header

#if FW_HAS_BUS && !FW_HAS_EXERCISER

#include <stdio.h>

#include "hardware/gpio.h"
#include "pico/stdlib.h"
#include "pico/unique_id.h"

#include "ata.h"
#include "bus.h"
#include "drive.h"
#include "flash.h"
#include "flashdisk.h"
#include "media.h"
#include "product.h"
#include "sd.h"
#include "version.h"

#define LAMP_TEST_MS 250

static ata_t ata;
static drive_t drive;
static flashdisk_t fdisk;
static char serial[2 * PICO_UNIQUE_BOARD_ID_SIZE_BYTES + 1];
static uint32_t settle_ms;                  // from main() to answering
static bool settled, present;

static uint32_t now_us(void *clock)
{
    (void)clock;
    return time_us_32();
}

static void report(void)
{
    const sd_info_t *s = sd_info();
    medium_t *m = drive_choose(&drive);
    const drive_stats_t *d = &drive.stats;
    printf("Answering since %lu ms after start: %s\r\n", (unsigned long)settle_ms,
           !settled ? "not yet" : present ? "a medium is ready" : "no medium");
    printf("Medium now: %s", m ? m->name : "none");
    if (m)
        printf(", N = %lu", (unsigned long)media_disks(m->sectors(m)));
    printf("\r\nSD card: %s", s->state == SD_READY ? "ready" : s->state == SD_STARTING ? "starting"
                               : s->state == SD_FAILED ? "failed" : "none");
    if (s->state == SD_READY)
        printf(", %lu sectors, N = %lu", (unsigned long)s->sectors, (unsigned long)media_disks(s->sectors));
    printf("\r\nBuilt-in drive: %lu MB, N = %lu\r\n", (unsigned long)(fdisk.nor->size >> 20),
           (unsigned long)media_disks(fdisk.medium.sectors(&fdisk.medium)));
    printf("Jobs: SD %lu reads, %lu writes; built-in %lu reads, %lu writes; %lu errors\r\n",
           (unsigned long)d->sd.reads, (unsigned long)d->sd.writes, (unsigned long)d->flash.reads,
           (unsigned long)d->flash.writes, (unsigned long)d->errors);
    printf("Longest busy: %lu us (SD write %lu, built-in write %lu)\r\n", (unsigned long)d->longest_busy_us,
           (unsigned long)d->sd.longest_write_us, (unsigned long)d->flash.longest_write_us);
    bus_stats_t b = bus_stats();
    printf("Bus: %lu reads, %lu writes, %lu resets; longest handling %lu ns\r\n", (unsigned long)b.reads,
           (unsigned long)b.writes, (unsigned long)b.resets, (unsigned long)b.longest_ns);
}

void controller_main(void (*banner)(void))
{
    uint32_t start = to_ms_since_boot(get_absolute_time());
    bus_start(&ata);                        // from here every read answers $80 (BSY) until bus_set_present()
    stdio_init_all();
    pico_get_unique_board_id_string(serial, sizeof serial);
    sd_init(FW_SD_HZ);
    flashdisk_init(&fdisk, flash_init(FW_FLASH_HZ));
    drive_init(&drive, &ata, sd_medium(), &fdisk.medium, now_us, NULL, PRODUCT_MODEL, serial, FW_VERSION);

    bool told = false;
    for (;;) {
        uint32_t ms = to_ms_since_boot(get_absolute_time()) - start;
        sd_poll();
        if (!settled) {
            const sd_info_t *s = sd_info();
            if (drive_boot_settled(s->card_in, s->state == SD_READY, s->state == SD_FAILED, ms)) {
                present = drive_choose(&drive) != NULL;
                bus_set_present(present);
                settle_ms = ms;
                settled = true;
            }
        } else {
            drive_service(&drive);
        }

        // The lamp test (main.c lit both LEDs) ends here, without holding anything up.
        if (ms >= LAMP_TEST_MS) {
            drive_leds_t l = drive_leds(&drive, time_us_32());
            gpio_put(FW_PIN_LED_SD, l.sd);
            gpio_put(FW_PIN_LED_ACT, l.act);
        }

        bool connected = stdio_usb_connected();
        if (connected && !told)
            banner();
        told = connected;
        if (getchar_timeout_us(0) >= 0)
            report();
    }
}

#endif
