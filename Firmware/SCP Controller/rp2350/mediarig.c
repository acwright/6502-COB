// The media rig's test console: the SD card and the built-in drive's chip on
// their breakouts, with no bus. Commands come over the USB serial port, one a
// line; each answer ends with a line "END".
//
//   info                     the build, the card, the chip, and the medium a command would use
//   sd                       start the card again, step by step
//   flash                    reset the chip and read its ID again
//   clock sd|flash HZ        the SPI clock after start-up (the rig's breakout may need it lower)
//   test sd|flash [DISKS]    write every sector of the medium's first DISKS disks (all the
//                            BIOS reaches, at most 256, if left out), read them back and compare,
//                            then read where every disk above the medium's mirrors to
//   dump sd|flash SECTOR     one sector, as the BIOS would read it
//   watch SECONDS            card detect, the medium chosen and the LEDs, as they change
//   pins                     each SD and flash pin against the pad's pull-up and pull-down
//   adc                      the voltage on GPIO26-28, undriven, pulled and driven
//   flashprobe               the flash chip's ID with its four wires taken every way round
//   flashwires               with the module out and the four wires' far ends joined: each carries
#include "mediarig.h"

#include "pico.h"          // the board header: FW_HAS_MEDIA_CONSOLE

#if FW_HAS_MEDIA_CONSOLE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "hardware/adc.h"
#include "hardware/gpio.h"
#include "pico/stdlib.h"
#include "pico/unique_id.h"

#include "ata.h"
#include "drive.h"
#include "flash.h"
#include "flashdisk.h"
#include "media.h"
#include "product.h"
#include "sd.h"
#include "version.h"

#define BIOS_DISKS 256u     // what the BIOS's LBA reaches: 256 disks of 1 MB

static ata_t ata;
static drive_t drive;
static flashdisk_t fdisk;
static char serial[2 * PICO_UNIQUE_BOARD_ID_SIZE_BYTES + 1];

static uint32_t now_us(void *clock)
{
    (void)clock;
    return time_us_32();
}

static void leds(void)
{
    drive_leds_t l = drive_leds(&drive, time_us_32());
    gpio_put(FW_PIN_LED_SD, l.sd);
    gpio_put(FW_PIN_LED_ACT, l.act);
}

static void idle(void)
{
    sd_poll();
    leds();
}

static const char *state_name(sd_state_t s)
{
    switch (s) {
    case SD_EMPTY: return "no card";
    case SD_STARTING: return "starting";
    case SD_READY: return "ready";
    default: return "FAILED";
    }
}

static medium_t *medium_named(const char *name)
{
    if (name && !strcmp(name, "sd"))
        return sd_medium();
    if (name && !strcmp(name, "flash"))
        return &fdisk.medium;
    printf("  sd or flash?\r\n");
    return NULL;
}

// --- info --------------------------------------------------------------------------

static void print_sd(void)
{
    const sd_info_t *s = sd_info();
    printf("  SD card: card detect %s (now %s); %s", s->card_in ? "in" : "out",
           sd_card_detect_raw() ? "in" : "out", state_name(s->state));
    if (s->state == SD_FAILED)
        printf(" at %s", s->failed_at);
    printf("\r\n");
    if (s->state != SD_READY)
        return;
    const uint8_t *c = s->cid;
    printf("    %s, %lu sectors (%lu MB), N = %lu; started in %lu ms; clock %lu Hz\r\n",
           s->high_capacity ? "SDHC/SDXC" : "SDSC", (unsigned long)s->sectors,
           (unsigned long)(s->sectors / 2048), (unsigned long)media_disks(s->sectors),
           (unsigned long)s->start_ms, (unsigned long)s->hz);
    printf("    CID: maker $%02X, OEM %c%c, product %c%c%c%c%c rev %u.%u, serial %02X%02X%02X%02X, made %u/%u\r\n",
           c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8] >> 4, c[8] & 15, c[9], c[10], c[11], c[12],
           c[14] & 15, 2000 + ((c[13] & 15) << 4 | c[14] >> 4));
    printf("    CSD:");
    for (int i = 0; i < 16; i++)
        printf(" %02X", s->csd[i]);
    printf("\r\n    OCR $%08lX; %lu reads, %lu writes, %lu CRC retries, %lu failed\r\n", (unsigned long)s->ocr,
           (unsigned long)s->reads, (unsigned long)s->writes, (unsigned long)s->crc_retries,
           (unsigned long)s->failures);
}

static void print_flash(void)
{
    const flash_info_t *f = flash_info();
    printf("  Flash: JEDEC ID %02X %02X %02X, status %02X %02X %02X; ", f->jedec[0], f->jedec[1], f->jedec[2],
           f->status[0], f->status[1], f->status[2]);
    if (!fdisk.nor->size) {
        printf("NOT a chip this knows\r\n");
        return;
    }
    printf("%lu MB, N = %lu; clock %lu Hz\r\n", (unsigned long)(fdisk.nor->size >> 20),
           (unsigned long)media_disks(fdisk.nor->size / 512), (unsigned long)f->hz);
    printf("    %lu page programs (longest %lu us), %lu erases (longest %lu us), %lu timeouts, %lu write enables missed\r\n",
           (unsigned long)f->programs, (unsigned long)f->longest_program_us, (unsigned long)f->erases,
           (unsigned long)f->longest_erase_us, (unsigned long)f->timeouts, (unsigned long)f->wel_failures);
    printf("    flash disk: %lu writes: %lu unchanged, %lu in place, %lu erased; %lu failed\r\n",
           (unsigned long)fdisk.stats.writes, (unsigned long)fdisk.stats.unchanged,
           (unsigned long)fdisk.stats.in_place, (unsigned long)fdisk.stats.erases, (unsigned long)fdisk.stats.failed);
}

static void cmd_info(void)
{
    printf("  %s %s, %s\r\n", PRODUCT_FIRMWARE, FW_VERSION, FW_TARGET_NAME);
    print_sd();
    print_flash();
    medium_t *m = drive_choose(&drive);
    drive_leds_t l = drive_leds(&drive, time_us_32());
    printf("  A command now would use: %s. LEDs: SD %s, ACT %s\r\n", m ? m->name : "NOTHING", l.sd ? "on" : "off",
           l.act ? "on" : "off");
}

// --- test ----------------------------------------------------------------------------

// Each sector's own bytes: its number and the run's seed, then xorshift32 from both.
static void pattern(uint8_t *buf, uint32_t sector, uint32_t seed)
{
    uint32_t x = seed ^ (sector * 0x9E3779B9u);
    if (!x)
        x = 1;
    for (int i = 0; i < 128; i++) {
        x ^= x << 13;
        x ^= x >> 17;
        x ^= x << 5;
        memcpy(buf + 4 * i, &x, 4);
    }
    memcpy(buf, &sector, 4);
    memcpy(buf + 4, &seed, 4);
}

// FNV-1a, a word at a time. Not a linear sum: with rotate-and-XOR the seed in
// every sector cancelled out over an even number of sectors, and every run gave
// the same checksum whatever its data.
#define CHECKSUM_START 2166136261u
static uint32_t checksum(uint32_t sum, const uint8_t *buf)
{
    for (int i = 0; i < 512; i += 4) {
        uint32_t w;
        memcpy(&w, buf + i, 4);
        sum = (sum ^ w) * 16777619u;
    }
    return sum;
}

typedef struct {
    uint32_t count, failed, longest_us, over_426, over_852;
    uint64_t total_us;
} times_t;

static void timed(times_t *t, uint32_t us, bool ok)
{
    t->count++;
    t->total_us += us;
    if (!ok)
        t->failed++;
    if (us > t->longest_us)
        t->longest_us = us;
    if (us > 426000)
        t->over_426++;
    if (us > 852000)
        t->over_852++;
}

static void print_times(const char *what, const times_t *t, uint32_t sectors)
{
    double s = (double)t->total_us / 1e6;
    printf("  %s: %lu sectors in %.1f s (%.2f MB/s), %lu failed; longest %lu us, %lu over 426 ms, %lu over 852 ms\r\n",
           what, (unsigned long)t->count, s, s > 0 ? sectors * 512.0 / 1048576.0 / s : 0.0, (unsigned long)t->failed,
           (unsigned long)t->longest_us, (unsigned long)t->over_426, (unsigned long)t->over_852);
}

static void progress(const char *what, uint32_t done, uint32_t of, uint32_t *last)
{
    uint32_t now = time_us_32();
    if (now - *last >= 10000000u) {
        *last = now;
        printf("    %s %lu of %lu\r\n", what, (unsigned long)done, (unsigned long)of);
    }
}

static uint8_t want[512], got[512];

static void cmd_test(const char *which, int disks_asked)
{
    medium_t *m = medium_named(which);
    if (!m)
        return;
    if (!m->ready(m)) {
        printf("  %s: not ready\r\nRESULT FAIL\r\n", m->name);
        return;
    }
    uint32_t n = media_disks(m->sectors(m));
    uint32_t disks = n < BIOS_DISKS ? n : BIOS_DISKS;
    if (disks_asked > 0 && (uint32_t)disks_asked < n)
        disks = (uint32_t)disks_asked;
    uint32_t sectors = disks * MEDIA_DISK_SECTORS;
    uint32_t seed = time_us_32() * 2654435761u ^ 0xA5C6502u;
    printf("  %s: N = %lu; testing disks 0-%lu, %lu sectors, seed %08lX\r\n", m->name, (unsigned long)n,
           (unsigned long)(disks - 1), (unsigned long)sectors, (unsigned long)seed);

    bool is_flash = m == &fdisk.medium;
    flashdisk_stats_t fs0 = fdisk.stats;
    const sd_info_t *si = sd_info();
    uint32_t crc0 = si->crc_retries;
    gpio_put(FW_PIN_LED_ACT, 1);

    // Write.
    times_t wt = { 0 };
    uint32_t sum_written = CHECKSUM_START, last = time_us_32();
    for (uint32_t s = 0; s < sectors; s++) {
        pattern(want, s, seed);
        sum_written = checksum(sum_written, want);
        uint32_t t0 = time_us_32();
        medium_result_t r = m->write(m, s, want);
        timed(&wt, time_us_32() - t0, r == MEDIUM_OK);
        if (r == MEDIUM_GONE || wt.failed > 16) {
            printf("  stopped writing at sector %lu: %s\r\n", (unsigned long)s, r == MEDIUM_GONE ? "the card went" : "too many failures");
            break;
        }
        progress("written", s + 1, sectors, &last);
    }
    print_times("write", &wt, sectors);

    // Read back, and compare.
    times_t rt = { 0 };
    uint32_t sum_read = CHECKSUM_START, wrong = 0;
    last = time_us_32();
    for (uint32_t s = 0; s < sectors && wt.failed <= 16; s++) {
        uint32_t t0 = time_us_32();
        medium_result_t r = m->read(m, s, got);
        timed(&rt, time_us_32() - t0, r == MEDIUM_OK);
        if (r == MEDIUM_GONE)
            break;
        sum_read = checksum(sum_read, got);
        pattern(want, s, seed);
        if (memcmp(want, got, 512)) {
            if (wrong++ < 5) {
                int i = 0;
                while (want[i] == got[i])
                    i++;
                printf("  sector %lu WRONG from byte %d: wanted %02X, got %02X (its first word: %02X%02X%02X%02X)\r\n",
                       (unsigned long)s, i, want[i], got[i], got[3], got[2], got[1], got[0]);
            }
        }
        progress("read", s + 1, sectors, &last);
    }
    print_times("read", &rt, sectors);
    printf("  checksum written %08lX, read %08lX; %lu sectors wrong\r\n", (unsigned long)sum_written,
           (unsigned long)sum_read, (unsigned long)wrong);

    // The disks above the medium's N, where the BIOS's LBA mirrors.
    uint32_t mirror_wrong = 0, mirrored = 0;
    // Only when every disk the medium holds was written.
    for (uint32_t d = n; d < BIOS_DISKS && disks == n; d++) {
        uint32_t lba = d * MEDIA_DISK_SECTORS + (d * 37u) % MEDIA_DISK_SECTORS, sector;
        if (!media_map(m->sectors(m), lba, &sector) || m->read(m, sector, got) != MEDIUM_OK) {
            mirror_wrong++;
            continue;
        }
        pattern(want, sector, seed);
        mirrored++;
        if (memcmp(want, got, 512))
            mirror_wrong++;
    }
    if (n < BIOS_DISKS && disks == n)
        printf("  mirrors: disks %lu-255, one sector each: %lu read, %lu wrong\r\n", (unsigned long)n,
               (unsigned long)mirrored, (unsigned long)mirror_wrong);

    uint32_t unchanged = 0;
    if (is_flash && !wt.failed && !wrong) {
        // The same data again: every sector should be skipped, unchanged.
        uint32_t before = fdisk.stats.unchanged;
        times_t again = { 0 };
        for (uint32_t s = 0; s < sectors; s++) {
            pattern(want, s, seed);
            uint32_t t0 = time_us_32();
            medium_result_t r = m->write(m, s, want);
            timed(&again, time_us_32() - t0, r == MEDIUM_OK);
        }
        unchanged = fdisk.stats.unchanged - before;
        print_times("the same data again", &again, sectors);
        printf("  ... of which skipped, unchanged: %lu\r\n", (unsigned long)unchanged);
    }
    gpio_put(FW_PIN_LED_ACT, 0);

    if (is_flash)
        printf("  flash disk: %lu in place, %lu erased; chip: longest program %lu us, longest erase %lu us, %lu timeouts\r\n",
               (unsigned long)(fdisk.stats.in_place - fs0.in_place), (unsigned long)(fdisk.stats.erases - fs0.erases),
               (unsigned long)flash_info()->longest_program_us, (unsigned long)flash_info()->longest_erase_us,
               (unsigned long)flash_info()->timeouts);
    else
        printf("  SD: %lu CRC retries\r\n", (unsigned long)(si->crc_retries - crc0));

    bool pass = !wt.failed && !rt.failed && wt.count == sectors && rt.count == sectors && !wrong &&
                sum_written == sum_read && !mirror_wrong && (!is_flash || unchanged == sectors);
    printf("RESULT %s\r\n", pass ? "PASS" : "FAIL");
}

// --- dump, watch -------------------------------------------------------------------------

static void cmd_dump(const char *which, uint32_t sector)
{
    medium_t *m = medium_named(which);
    if (!m)
        return;
    medium_result_t r = m->ready(m) ? m->read(m, sector, got) : MEDIUM_FAILED;
    if (r != MEDIUM_OK) {
        printf("  %s: sector %lu couldn't be read\r\n", m->name, (unsigned long)sector);
        return;
    }
    for (int i = 0; i < 512; i += 16) {
        printf("  %03X:", i);
        for (int j = 0; j < 16; j++)
            printf(" %02X", got[i + j]);
        printf("\r\n");
    }
}

static void cmd_watch(uint32_t seconds)
{
    printf("  watching for %lu s: put the card in and take it out\r\n", (unsigned long)seconds);
    uint32_t start = time_us_32();
    int raw = -1, in = -1, state = -1, sd_led = -1;
    medium_t *chosen = (medium_t *)1;
    while (time_us_32() - start < seconds * 1000000u) {
        idle();
        const sd_info_t *s = sd_info();
        medium_t *m = drive_choose(&drive);
        drive_leds_t l = drive_leds(&drive, time_us_32());
        uint32_t ms = (time_us_32() - start) / 1000;
        if (sd_card_detect_raw() != raw) {
            raw = sd_card_detect_raw();
            printf("  %6lu ms  pin: %s\r\n", (unsigned long)ms, raw ? "card" : "no card");
        }
        if (s->card_in != in) {
            in = s->card_in;
            printf("  %6lu ms  card detect (debounced): %s\r\n", (unsigned long)ms, in ? "in" : "out");
        }
        if ((int)s->state != state) {
            state = (int)s->state;
            printf("  %6lu ms  SD: %s", (unsigned long)ms, state_name(s->state));
            if (s->state == SD_READY)
                printf(", started in %lu ms, N = %lu", (unsigned long)s->start_ms,
                       (unsigned long)media_disks(s->sectors));
            if (s->state == SD_FAILED)
                printf(" at %s", s->failed_at);
            printf("\r\n");
        }
        if (m != chosen) {
            chosen = m;
            printf("  %6lu ms  a command would use: %s\r\n", (unsigned long)ms, m ? m->name : "NOTHING");
        }
        if (l.sd != sd_led) {
            sd_led = l.sd;
            printf("  %6lu ms  green LED %s\r\n", (unsigned long)ms, l.sd ? "on" : "off");
        }
    }
}

// Each rig pin as an input, against the pad's pull-up and then its pull-down,
// with every chip select high. One that reads low against the pull-up is held
// low: a short, a wire on the wrong pin, or a chip with no power (its pins clamp
// to its own 0 V). The pull-down is weak on the RP2350 (erratum E9): a pin left
// floating may still read high against it.
static void cmd_pins(void)
{
    static const struct { const char *name; unsigned pin; } pins[] = {
        { "SD DO (MISO)", FW_PIN_SD_MISO }, { "SD CS", FW_PIN_SD_CS },     { "SD CLK", FW_PIN_SD_SCK },
        { "SD DI (MOSI)", FW_PIN_SD_MOSI }, { "SD CD", FW_PIN_SD_CD },     { "flash DO (MISO)", FW_PIN_FLASH_MISO },
        { "flash CS", FW_PIN_FLASH_CS },    { "flash CLK", FW_PIN_FLASH_SCK }, { "flash DI (MOSI)", FW_PIN_FLASH_MOSI },
    };
    gpio_put(FW_PIN_SD_CS, 1);
    gpio_put(FW_PIN_FLASH_CS, 1);
    for (unsigned i = 0; i < sizeof pins / sizeof pins[0]; i++) {
        unsigned p = pins[i].pin;
        bool cs = p == FW_PIN_SD_CS || p == FW_PIN_FLASH_CS;
        if (cs)
            gpio_set_dir(p, GPIO_IN);
        gpio_function_t f = gpio_get_function(p);
        gpio_set_function(p, GPIO_FUNC_SIO);
        gpio_set_dir(p, GPIO_IN);
        gpio_pull_up(p);
        busy_wait_us(200);
        bool up = gpio_get(p);
        gpio_pull_down(p);
        busy_wait_us(200);
        bool down = gpio_get(p);
        gpio_disable_pulls(p);
        // The pad's own driver, a millisecond each way, read back at the pad. Not
        // CD's: a card-detect switch may tie it hard to ground.
        bool drives_low = true, drives_high = true;
        if (p != FW_PIN_SD_CD) {
            gpio_put(p, 0);
            gpio_set_dir(p, GPIO_OUT);
            busy_wait_us(1000);
            drives_low = !gpio_get(p);
            gpio_put(p, 1);
            busy_wait_us(1000);
            drives_high = gpio_get(p);
            gpio_set_dir(p, GPIO_IN);
        }
        printf("  GPIO%-2u %-16s pull-up: %-4s pull-down: %-4s drives low: %-3s high: %-3s %s\r\n", p, pins[i].name,
               up ? "high" : "LOW", down ? "HIGH" : "low", drives_low ? "yes" : "NO", drives_high ? "yes" : "NO",
               !drives_low || !drives_high ? "<- PAD FAULT, or held by something strong"
               : !up && !down ? "<- held low" : up && down ? "(held high, or floating: E9)" : "");
        if (p == FW_PIN_SD_MISO || (p == FW_PIN_SD_CD && FW_SD_CD_PULLUP))
            gpio_pull_up(p);
        else
            gpio_disable_pulls(p);
        gpio_set_function(p, f);
        if (cs) {
            gpio_put(p, 1);
            gpio_set_dir(p, GPIO_OUT);
        }
    }
}

// The four flash wires, with the module out and their far ends joined in one
// breadboard row: each driven low in turn, the other three held up by their
// pads' pull-ups, must follow it, and go back up when it lets go. It proves the
// pads, the firmware's pin set-up and the wires, end to end, with no chip.
static void cmd_flashwires(void)
{
    const unsigned wires[4] = { FW_PIN_FLASH_CS, FW_PIN_FLASH_SCK, FW_PIN_FLASH_MOSI, FW_PIN_FLASH_MISO };
    const char *names[4] = { "CS (GPIO15)", "CLK (GPIO26)", "DI (GPIO27)", "DO (GPIO28)" };
    int bad = 0;
    for (int i = 0; i < 4; i++) {
        gpio_init(wires[i]);
        gpio_pull_up(wires[i]);
    }
    busy_wait_us(500);
    for (int d = 0; d < 4; d++) {
        gpio_put(wires[d], 0);
        gpio_set_dir(wires[d], GPIO_OUT);
        busy_wait_us(200);
        bool own = gpio_get(wires[d]);
        printf("  %-13s driven low (its pad reads %s):", names[d], own ? "HIGH" : "low");
        bad += own;
        for (int o = 0; o < 4; o++) {
            if (o == d)
                continue;
            bool follows = !gpio_get(wires[o]);
            printf("  %s %s", names[o], follows ? "follows" : "DOESN'T");
            bad += !follows;
        }
        gpio_set_dir(wires[d], GPIO_IN);
        busy_wait_us(500);
        for (int o = 0; o < 4; o++)
            if (!gpio_get(wires[o])) {
                printf("  [%s stays low after]", names[o]);
                bad++;
            }
        printf("\r\n");
    }
    for (int i = 0; i < 4; i++)
        gpio_disable_pulls(wires[i]);
    printf("RESULT %s\r\n", bad ? "FAIL" : "PASS");
}

// The voltage on GPIO26-28 (ADC inputs 0-2) as each is left undriven, pulled
// either way, and driven low and high, read by the ADC alongside the digital
// pad. It tells a pin held by something outside (it stays put however it's
// pulled or driven) from one left floating, and measures the fight when a pin
// is driven against it. Each drive lasts a millisecond. The flash pins are left
// undriven inputs afterwards, until "flash" sets them up again.
static void cmd_adc(void)
{
    adc_init();
    const unsigned flash_pins[4] = { FW_PIN_FLASH_CS, FW_PIN_FLASH_SCK, FW_PIN_FLASH_MOSI, FW_PIN_FLASH_MISO };
    for (int i = 0; i < 4; i++) {
        gpio_init(flash_pins[i]);
        gpio_disable_pulls(flash_pins[i]);
    }
    static const char *how[] = { "undriven", "pull-up", "pull-down", "driven low", "driven high" };
    for (unsigned pin = 26; pin <= 28; pin++) {
        printf("  GPIO%u:", pin);
        for (int h = 0; h < 5; h++) {
            gpio_disable_pulls(pin);
            gpio_set_dir(pin, GPIO_IN);
            if (h == 1)
                gpio_pull_up(pin);
            if (h == 2)
                gpio_pull_down(pin);
            if (h >= 3) {
                gpio_put(pin, h == 4);
                gpio_set_dir(pin, GPIO_OUT);
            }
            adc_select_input(pin - 26);
            busy_wait_us(1000);
            uint32_t sum = 0;
            for (int k = 0; k < 16; k++)
                sum += adc_read();
            bool digital = gpio_get(pin);
            gpio_set_dir(pin, GPIO_IN);
            gpio_disable_pulls(pin);
            uint32_t mv = sum * 3300u / 16u / 4095u;
            printf("  %s %lu.%02lu V (%s)", how[h], (unsigned long)(mv / 1000), (unsigned long)(mv % 1000 / 10),
                   digital ? "high" : "low");
        }
        printf("\r\n");
    }
    printf("  the flash pins are left undriven: \"flash\" sets them up again\r\n");
}

static void start_flash(uint32_t hz);

// For a flash chip that doesn't answer: the JEDEC ID asked for slowly, by hand,
// with the four flash wires taken as CS, CLK, DI and DO in each of the 24 ways
// they could be, to find two wires swapped. The pins drive at 2 mA, so a pin
// driven against the chip's DO for a moment does no harm.
static uint8_t probe_bits(unsigned clk, unsigned di, unsigned dout, uint8_t out)
{
    uint8_t in = 0;
    for (int b = 7; b >= 0; b--) {
        gpio_put(di, (out >> b) & 1);
        busy_wait_us(5);
        gpio_put(clk, 1);
        busy_wait_us(2);
        in = (uint8_t)(in << 1 | gpio_get(dout));
        busy_wait_us(3);
        gpio_put(clk, 0);
    }
    return in;
}

static void cmd_flashprobe(void)
{
    const unsigned wires[4] = { FW_PIN_FLASH_CS, FW_PIN_FLASH_SCK, FW_PIN_FLASH_MOSI, FW_PIN_FLASH_MISO };
    const char *names[4] = { "CS", "CLK", "DI", "DO" };
    for (int i = 0; i < 4; i++) {
        gpio_init(wires[i]);
        gpio_set_drive_strength(wires[i], GPIO_DRIVE_STRENGTH_2MA);
        gpio_pull_down(wires[i]);
    }
    int found = 0;
    for (int perm = 0; perm < 24; perm++) {
        // The perm-th ordering of the four wires: role r is wire w[r].
        unsigned w[4], pool[4] = { 0, 1, 2, 3 }, k = (unsigned)perm;
        for (int r = 0, left = 4; r < 4; r++, left--) {
            unsigned f = 1;
            for (int j = 2; j < left; j++)
                f *= (unsigned)j;
            unsigned pick = k / f;
            k %= f;
            w[r] = pool[pick];
            for (int j = (int)pick; j < left - 1; j++)
                pool[j] = pool[j + 1];
        }
        unsigned cs = wires[w[0]], clk = wires[w[1]], di = wires[w[2]], dout = wires[w[3]];
        for (int r = 0; r < 3; r++) {
            gpio_put(wires[w[r]], r == 0);      // CS high, CLK and DI low
            gpio_set_dir(wires[w[r]], GPIO_OUT);
        }
        gpio_set_dir(dout, GPIO_IN);
        busy_wait_us(50);
        gpio_put(cs, 0);
        probe_bits(clk, di, dout, 0xAB);        // release from power-down
        gpio_put(cs, 1);
        busy_wait_us(50);
        gpio_put(cs, 0);
        probe_bits(clk, di, dout, 0x9F);
        uint8_t id[3];
        for (int i = 0; i < 3; i++)
            id[i] = probe_bits(clk, di, dout, 0xFF);
        gpio_put(cs, 1);
        for (int r = 0; r < 4; r++)
            gpio_set_dir(wires[r], GPIO_IN);
        bool answer = !(id[0] == 0xFF && id[1] == 0xFF && id[2] == 0xFF) && !(id[0] == 0 && id[1] == 0 && id[2] == 0);
        if (answer || perm == 0) {
            printf("  %s:", perm == 0 ? "as wired" : "ANSWERS");
            for (int r = 0; r < 4; r++)
                printf(" %s on GPIO%u", names[r], wires[w[r]]);
            printf(": ID %02X %02X %02X\r\n", id[0], id[1], id[2]);
            found += answer;
        }
    }
    if (!found)
        printf("  no arrangement of the four wires answers: look at the chip's power, and each wire's far end\r\n");
    for (int i = 0; i < 4; i++) {
        gpio_disable_pulls(wires[i]);
        gpio_set_drive_strength(wires[i], GPIO_DRIVE_STRENGTH_4MA);
    }
    start_flash(flash_info()->hz);              // the pins back to SPI1
}

// --- The console ----------------------------------------------------------------------------

static void start_flash(uint32_t hz)
{
    flashdisk_init(&fdisk, flash_init(hz));
}

static void dispatch(char *line)
{
    char *argv[4] = { 0 };
    int argc = 0;
    for (char *t = strtok(line, " \t"); t && argc < 4; t = strtok(NULL, " \t"))
        argv[argc++] = t;
    if (!argc)
        return;
    if (!strcmp(argv[0], "info"))
        cmd_info();
    else if (!strcmp(argv[0], "sd")) {
        sd_restart(true);
        print_sd();
    } else if (!strcmp(argv[0], "flash")) {
        start_flash(flash_info()->hz);
        print_flash();
    } else if (!strcmp(argv[0], "clock") && argc > 2) {
        uint32_t hz = (uint32_t)strtoul(argv[2], NULL, 0);
        if (!strcmp(argv[1], "sd"))
            printf("  SD clock %lu Hz\r\n", (unsigned long)sd_set_hz(hz));
        else if (!strcmp(argv[1], "flash"))
            printf("  flash clock %lu Hz\r\n", (unsigned long)flash_set_hz(hz));
    } else if (!strcmp(argv[0], "test"))
        cmd_test(argv[1], argc > 2 ? atoi(argv[2]) : 0);
    else if (!strcmp(argv[0], "dump"))
        cmd_dump(argv[1], argc > 2 ? (uint32_t)strtoul(argv[2], NULL, 0) : 0);
    else if (!strcmp(argv[0], "adc"))
        cmd_adc();
    else if (!strcmp(argv[0], "flashwires")) {
        cmd_flashwires();
        start_flash(flash_info()->hz);
    } else if (!strcmp(argv[0], "flashprobe"))
        cmd_flashprobe();
    else if (!strcmp(argv[0], "pins"))
        cmd_pins();
    else if (!strcmp(argv[0], "watch"))
        cmd_watch(argc > 1 ? (uint32_t)atoi(argv[1]) : 30);
    else
        printf("unknown: %s\r\n", argv[0]);
    printf("END\r\n");
}

void mediarig_main(void (*banner)(void))
{
    pico_get_unique_board_id_string(serial, sizeof serial);
    sd_init(FW_SD_HZ);
    start_flash(FW_FLASH_HZ);
    ata_init(&ata);
    drive_init(&drive, &ata, sd_medium(), &fdisk.medium, now_us, NULL, PRODUCT_MODEL, serial, FW_VERSION);

    char line[80];
    size_t len = 0;
    bool told = false;
    for (;;) {
        bool connected = stdio_usb_connected();
        if (connected && !told)
            banner();
        told = connected;
        int c = getchar_timeout_us(0);
        if (c == '\r' || c == '\n') {
            line[len] = 0;
            dispatch(line);
            len = 0;
        } else if (c >= 0 && len < sizeof line - 1) {
            line[len++] = (char)c;
        }
        idle();
    }
}

#endif
