// The loopback rig's test console. The controller runs as on the board (the bus
// on PIO0 and core 1, the worker on core 0) on a pattern disk, and the exerciser
// plays a 6502's side of the bus into it through the jumper wires. Commands come
// over the USB serial port, one a line; each answer ends with a line "END".
//
//   info                     the build, and the counts so far (core 1's handling times)
//   sweep MHZ [RUNS]         when D0-D7 are ready after RB falls, by delay: RUNS of 128
//                            samples at each delay (16; 7813 makes a million)
//   bsy MHZ                  BSY and DRQ in time for the tightest status reads
//   soak MHZ SECONDS         sectors written and read back in the BIOS's own loop timing
//   spacing MHZ CYCLES       the same for 10 s, data reads CYCLES apart (the BIOS's are 15)
// and, for finding faults on the rig:
//   wires                    each jumper wire, both ways
//   pads                     each control pad: GPIO15-21 driven, GPIO8-14 against their pulls
//   selfdrive PIN            one of GPIO8-14 driven by itself (only with its wire out)
//   peek MHZ                 known values into the registers, and every register read back
//   raw MHZ DELAY            the sampler's first samples, and the stream's first words
//   bench                    what core 1's register updates cost, in cycles
#include "loopback.h"

#include "pico.h"          // the board header: FW_HAS_EXERCISER

#if FW_HAS_EXERCISER

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "hardware/gpio.h"
#include "pico/stdlib.h"
#include "pico/unique_id.h"

#include "ata.h"
#include "bus.h"
#include "drive.h"
#include "exerciser.h"
#include "patterndisk.h"
#include "product.h"
#include "version.h"

static ata_t ata;
static drive_t drive;
static patterndisk_t disk;
static uint32_t small_words[1024];
static uint32_t loop_words[24 * 1024];
static uint8_t samples[1024];
static char serial[2 * PICO_UNIQUE_BOARD_ID_SIZE_BYTES + 1];

static uint32_t now_us(void *clock)
{
    (void)clock;
    return time_us_32();
}

static void idle(void)
{
    drive_service(&drive);
    drive_leds_t l = drive_leds(&drive, time_us_32());
    gpio_put(FW_PIN_LED_SD, l.sd);
    gpio_put(FW_PIN_LED_ACT, l.act);
}

static void others(stream_t *s, int n)
{
    for (int i = 0; i < n; i++)
        stream_cycle(s, CYCLE_READ, 0, -1, false);
}

// --- Registers, as a 6502 program would touch them ------------------------------

static bool late;

static void reg_write(unsigned reg, uint8_t v, double mhz)
{
    stream_t s;
    stream_init(&s, small_words, 1024, mhz);
    others(&s, 3);
    stream_cycle(&s, CYCLE_OUR_WRITE, reg, -1, false);
    others(&s, 1);
    exerciser_drive_data(v);
    late |= !exerciser_play(&s, NULL, idle);
    exerciser_release_data();
}

static uint8_t reg_read(unsigned reg, double mhz)
{
    stream_t s;
    stream_init(&s, small_words, 1024, mhz);
    others(&s, 3);
    stream_cycle(&s, CYCLE_OUR_READ, reg, stream_latch_ns(&s), false);
    others(&s, 1);
    late |= !exerciser_play(&s, samples, idle);
    return samples[0];
}

// Polls status until (status & mask) == want, or ms pass. Returns the last status, or -1.
static int wait_status(uint8_t mask, uint8_t want, double mhz, uint32_t ms)
{
    uint32_t start = time_us_32();
    uint8_t st;
    do {
        st = reg_read(ATA_REG_STATUS, mhz);
        if ((st & mask) == want)
            return st;
    } while (time_us_32() - start < ms * 1000u);
    return -1;
}

static void setup(uint32_t lba, uint8_t count, double mhz)
{
    reg_write(ATA_REG_COUNT, count, mhz);
    reg_write(ATA_REG_LBA0, (uint8_t)lba, mhz);
    reg_write(ATA_REG_LBA1, (uint8_t)(lba >> 8), mhz);
    reg_write(ATA_REG_LBA2, (uint8_t)(lba >> 16), mhz);
    reg_write(ATA_REG_LBA3, (uint8_t)(0xE0 | (lba >> 24)), mhz);
}

// --- The BIOS's data loops -------------------------------------------------------

// StReadSector's loop, 15 cycles a byte: lda ST_DATA (4, the read last),
// sta (CF_BUF_PTR),y (6, the write last), iny (2), bne (3). `per_byte` below 15
// keeps the read and fills the rest with reads.
static void read_loop(stream_t *s, double mhz, int per_byte)
{
    stream_init(s, loop_words, sizeof loop_words / 4, mhz);
    for (int i = 0; i < 512; i++) {
        others(s, 3);
        stream_cycle(s, CYCLE_OUR_READ, ATA_REG_DATA, stream_latch_ns(s), false);
        if (per_byte >= 15) {
            others(s, 5);
            stream_cycle(s, CYCLE_WRITE, 0, -1, false);
            others(s, 5);
        } else {
            others(s, per_byte - 4);
        }
    }
}

// StWriteSector's loop, 14 cycles a byte: lda (CF_BUF_PTR),y (5), sta ST_DATA (4,
// the write last), iny (2), bne (3). Each write is followed by a marker, so the
// CPU puts the next byte on D0-D7.
static void write_loop(stream_t *s, double mhz)
{
    stream_init(s, loop_words, sizeof loop_words / 4, mhz);
    for (int i = 0; i < 512; i++) {
        others(s, 8);
        stream_cycle(s, CYCLE_OUR_WRITE, ATA_REG_DATA, -1, true);
        others(s, 5);
    }
}

static const uint8_t *write_data;
static uint8_t tail_status;

static void next_byte(uint32_t index, uint8_t value)
{
    if (index + 1 < 512)
        exerciser_drive_data(write_data[index + 1]);
    else if (index + 1 == 512)
        exerciser_release_data();
    else
        tail_status = value;            // the status read after the loop, if there is one
}

// For a stream with one write then one status read: sample 0 is the write's
// marker (let go of D0-D7), sample 1 the status.
static uint8_t first_status_value;
static void first_status(uint32_t index, uint8_t value)
{
    if (index == 0)
        exerciser_release_data();
    else if (index == 1)
        first_status_value = value;
}

static bool write_sector(uint32_t lba, const uint8_t *data, double mhz, char *why)
{
    setup(lba, 1, mhz);
    reg_write(ATA_REG_STATUS, ATA_CMD_WRITE, mhz);
    int st = wait_status(ATA_SR_BSY | ATA_SR_DRQ, ATA_SR_DRQ, mhz, 100);
    if (st < 0) {
        sprintf(why, "write %lu: no DRQ", (unsigned long)lba);
        return false;
    }
    stream_t s;
    write_loop(&s, mhz);
    write_data = data;
    exerciser_drive_data(data[0]);
    late |= !exerciser_play_live(&s, next_byte, idle);
    exerciser_release_data();
    st = wait_status(ATA_SR_BSY, 0, mhz, 1000);
    if (st != 0x50) {
        sprintf(why, "write %lu: status $%02X after the data", (unsigned long)lba, st & 0xFF);
        return false;
    }
    return true;
}

static bool read_sector(uint32_t lba, uint8_t *out, double mhz, int per_byte, char *why)
{
    setup(lba, 1, mhz);
    reg_write(ATA_REG_STATUS, ATA_CMD_READ, mhz);
    int st = wait_status(ATA_SR_BSY | ATA_SR_DRQ, ATA_SR_DRQ, mhz, 100);
    if (st < 0) {
        sprintf(why, "read %lu: no DRQ", (unsigned long)lba);
        return false;
    }
    stream_t s;
    read_loop(&s, mhz, per_byte);
    late |= !exerciser_play(&s, out, idle);
    st = wait_status(0xFF, 0x50, mhz, 100);
    if (st != 0x50) {
        sprintf(why, "read %lu: status $%02X after the data", (unsigned long)lba, st & 0xFF);
        return false;
    }
    return true;
}

static uint8_t expected_byte(uint32_t sector, unsigned i)
{
    for (unsigned k = 0; k < PATTERNDISK_SLOTS; k++)
        if (disk.slot[k].used && disk.slot[k].sector == sector)
            return disk.slot[k].data[i];
    return patterndisk_byte(sector, i);
}

static uint32_t rng = 0x12345678;
static uint32_t random32(void)
{
    rng ^= rng << 13;
    rng ^= rng >> 17;
    rng ^= rng << 5;
    return rng;
}

// --- Commands ----------------------------------------------------------------------

static void cmd_info(void)
{
    bus_stats_t b = bus_stats();
    printf("%s %s, %s\r\n", PRODUCT_FIRMWARE, FW_VERSION, FW_TARGET_NAME);
    printf("bus: %lu reads, %lu writes, %lu resets; core 1's longest access to copy current: %lu ns (read %lu, write %lu)\r\n",
           (unsigned long)b.reads, (unsigned long)b.writes, (unsigned long)b.resets, (unsigned long)b.longest_ns,
           (unsigned long)b.longest_read_ns, (unsigned long)b.longest_write_ns);
    static const char *bands[8] = { "<0.25", "<0.5", "<1", "<2", "<4", "<8", "<16", ">=16" };
    printf("  longest sections, in core 1 cycles: the access %lu, the checks and ata_poll %lu, publish %lu\r\n",
           (unsigned long)b.section_cycles[0], (unsigned long)b.section_cycles[1], (unsigned long)b.section_cycles[2]);
    printf("  handled in (us):");
    for (int i = 0; i < 8; i++)
        printf(" %s: %lu", bands[i], (unsigned long)b.histogram[i]);
    printf("\r\n");
    printf("drive: %lu jobs' errors, longest busy %lu us\r\n", (unsigned long)drive.stats.errors,
           (unsigned long)drive.stats.longest_busy_us);
}

static void cmd_sweep(double mhz, uint32_t runs)
{
    reg_write(ATA_REG_LBA0, 0x55, mhz);
    reg_write(ATA_REG_LBA1, 0xAA, mhz);
    stream_t s;
    stream_init(&s, loop_words, sizeof loop_words / 4, mhz);
    for (int i = 0; i < 64; i++) {
        others(&s, 1);
        stream_cycle(&s, CYCLE_OUR_READ, ATA_REG_LBA0, -1, false);
        others(&s, 1);
        stream_cycle(&s, CYCLE_OUR_READ, ATA_REG_LBA1, -1, false);
    }
    printf("sweep at %g MHz: LBA0 = $55 and LBA1 = $AA read alternately; the sampler reads D0-D7\r\n", mhz);
    printf("delay + 3 clocks after it sees RB fall (%.2f ns a clock)\r\n", s.ns_per_clock);
    for (uint32_t d = 0; d <= 16; d++) {
        uint32_t right = 0, total = 0, wrong_value = 0x100;
        for (uint32_t rep = 0; rep < runs; rep++) {
            size_t n = exerciser_sample_play(&s, d, samples, 128, idle);
            for (size_t i = 0; i < n; i++) {
                uint8_t want = (i & 1) ? 0xAA : 0x55;
                total++;
                if (samples[i] == want)
                    right++;
                else if (wrong_value == 0x100)
                    wrong_value = samples[i];
            }
        }
        printf("  %2lu clocks (%5.1f ns): %7lu of %7lu right", (unsigned long)(d + 3), (d + 3) * s.ns_per_clock,
               (unsigned long)right, (unsigned long)total);
        if (wrong_value != 0x100)
            printf(", e.g. $%02lX", (unsigned long)wrong_value);
        printf("\r\n");
    }
}

static void cmd_bsy(double mhz)
{
    char why[96];
    static uint8_t data[512], out[520];       // 512 bytes and the status after them
    disk.read_us = disk.write_us = 2000;    // long enough that BSY is plain to see
    late = false;
    printf("bsy at %g MHz: the status read 4 cycles after (the tightest a 6502 can), with a 2 ms medium\r\n", mhz);

    // 1. A command, then lda ST_STATUS: the read is 4 cycles after the write.
    setup(9, 1, mhz);
    stream_t s;
    stream_init(&s, small_words, 1024, mhz);
    others(&s, 3);
    stream_cycle(&s, CYCLE_OUR_WRITE, ATA_REG_STATUS, -1, true);
    others(&s, 3);
    stream_cycle(&s, CYCLE_OUR_READ, ATA_REG_STATUS, stream_latch_ns(&s), false);
    others(&s, 1);
    // Live: the marker after the write lets go of D0-D7 before the status read.
    static uint8_t command_only[1];
    write_data = command_only;
    tail_status = 0;
    exerciser_drive_data(ATA_CMD_READ);
    late |= !exerciser_play_live(&s, first_status, idle);
    exerciser_release_data();
    printf("  Read Sectors, then status: $%02X (want $80)\r\n", first_status_value);

    // Finish that read, its last byte then status 4 cycles later: DRQ must be gone.
    int st = wait_status(ATA_SR_BSY | ATA_SR_DRQ, ATA_SR_DRQ, mhz, 100);
    read_loop(&s, mhz, 15);
    others(&s, 3);
    stream_cycle(&s, CYCLE_OUR_READ, ATA_REG_STATUS, stream_latch_ns(&s), false);
    late |= !exerciser_play(&s, out, idle);
    int wrong = 0;
    for (int i = 0; i < 512; i++)
        wrong += out[i] != expected_byte(9, (unsigned)i);
    printf("  DRQ $%02X; 512 bytes, %d wrong; status after the last: $%02X (want $50)\r\n", st & 0xFF, wrong, out[512]);

    // 2. Write Sectors: after the 512th byte, status 4 cycles later must be BSY.
    for (int i = 0; i < 512; i++)
        data[i] = (uint8_t)(random32() >> 7);
    setup(10, 1, mhz);
    reg_write(ATA_REG_STATUS, ATA_CMD_WRITE, mhz);
    st = wait_status(ATA_SR_BSY | ATA_SR_DRQ, ATA_SR_DRQ, mhz, 100);
    write_loop(&s, mhz);
    others(&s, 3);
    stream_cycle(&s, CYCLE_OUR_READ, ATA_REG_STATUS, stream_latch_ns(&s), false);
    write_data = data;
    exerciser_drive_data(data[0]);
    late |= !exerciser_play_live(&s, next_byte, idle);
    exerciser_release_data();
    printf("  Write Sectors: DRQ $%02X; status after the 512th byte: $%02X (want $80)\r\n", st & 0xFF, tail_status);
    st = wait_status(ATA_SR_BSY, 0, mhz, 1000);
    bool back = read_sector(10, out, mhz, 15, why) && memcmp(out, data, 512) == 0;
    printf("  then $%02X, and the sector reads back %s\r\n", st & 0xFF, back ? "the same" : "DIFFERENT");
    printf("  streams on time: %s\r\n", late ? "NO" : "yes");
    disk.read_us = disk.write_us = 0;
}

static void cmd_soak(double mhz, uint32_t seconds, int per_byte)
{
    static uint8_t data[512], out[512];
    char why[96] = "";
    uint32_t sectors = 0, bytes = 0, errors = 0, failures = 0;
    late = false;
    uint64_t start = time_us_64(), next_report = start + 10000000u;
    printf("soak at %g MHz for %lu s, data reads %d cycles apart\r\n", mhz, (unsigned long)seconds, per_byte);
    while (time_us_64() - start < (uint64_t)seconds * 1000000u) {
        uint32_t lba = random32() & 0x7FFFF;            // the BIOS's 256 disks
        for (int i = 0; i < 512; i++)
            data[i] = (uint8_t)(random32() >> 11);
        if (!write_sector(lba, data, mhz, why) || !read_sector(lba, out, mhz, per_byte, why)) {
            if (failures++ < 5)
                printf("  FAIL %s\r\n", why);
            continue;
        }
        for (int i = 0; i < 512; i++)
            errors += out[i] != data[i];
        uint32_t other = (random32() & 0x7FFFF) | 0x80000u;   // never written: the pattern
        if (!read_sector(other, out, mhz, per_byte, why)) {
            if (failures++ < 5)
                printf("  FAIL %s\r\n", why);
            continue;
        }
        uint32_t sector;
        media_map(disk.sectors, other, &sector);
        for (int i = 0; i < 512; i++)
            errors += out[i] != expected_byte(sector, (unsigned)i);
        sectors += 3;
        bytes += 3 * 512;
        if (time_us_64() >= next_report) {
            next_report += 10000000u;
            printf("  %3llu s: %lu sectors, %lu bytes, %lu wrong, %lu failed commands%s\r\n",
                   (unsigned long long)((time_us_64() - start) / 1000000u), (unsigned long)sectors, (unsigned long)bytes,
                   (unsigned long)errors, (unsigned long)failures, late ? ", a stream ran LATE" : "");
        }
    }
    bus_stats_t b = bus_stats();
    printf("soak done: %lu sectors, %lu bytes, %lu wrong, %lu failed commands, streams %s; core 1's longest %lu ns\r\n",
           (unsigned long)sectors, (unsigned long)bytes, (unsigned long)errors, (unsigned long)failures,
           late ? "LATE" : "on time", (unsigned long)b.longest_ns);
    printf("%s\r\n", errors || failures || late ? "RESULT FAIL" : "RESULT PASS");
}

// Every register, read one at a time, and the core's own view of it.
static void cmd_peek(double mhz)
{
    static const uint8_t values[6] = { 0x11, 0x22, 0x33, 0x44, 0x55, 0x66 };
    reg_write(ATA_REG_ERROR, 0x01, mhz);                // the feature register: reads as error
    for (unsigned r = 2; r <= 5; r++)
        reg_write(r, values[r], mhz);
    for (int pass = 0; pass < 2; pass++)
        for (unsigned r = 0; r < 8; r++)
            printf("  reg %u: bus $%02X, core $%02X\r\n", r, reg_read(r, mhz), ata_peek(&ata, r));
}

// Each wire on its own: the exerciser's seven pins set one at a time, and what
// GPIO8-14 read.
static void cmd_wires(void)
{
    static const char *names[7] = { "RESB", "RB", "WB", "CS", "A2", "A1", "A0" };
    int bad = 0;
    for (int pass = 0; pass < 2; pass++) {
        for (unsigned b = 0; b < 7; b++) {
            uint32_t pins = pass ? (1u << b) : (0x7Fu & ~(1u << b));
            uint32_t got = exerciser_wires(pins);
            if (got != pins) {
                bad++;
                printf("  GPIO%u -> GPIO%u (%s): set %s, read %s; GPIO8-14 read $%02lX for $%02lX\r\n",
                       15 + b, 8 + b, names[b], (pins >> b) & 1 ? "high" : "low", (got >> b) & 1 ? "high" : "low",
                       (unsigned long)got, (unsigned long)pins);
            }
        }
    }
    // The exerciser's own pads, read back: do GPIO15-21 go where they're set?
    for (uint32_t pins = 0; pins <= 0x7F; pins += 0x7F) {
        exerciser_wires(pins);
        printf("  GPIO15-21 set $%02lX: read $%02lX at their own pads, $%02lX at GPIO8-14\r\n", (unsigned long)pins,
               (unsigned long)((gpio_get_all() >> 15) & 0x7Fu), (unsigned long)((gpio_get_all() >> 8) & 0x7Fu));
    }
    exerciser_wires(0x0F);                               // idle: RESB, RB, WB, CS high
    printf("  %s\r\n", bad ? "wiring FAULTS above" : "all seven wires good");
}

// Each control pad on its own. GPIO15-21: driven high, then low, read back at the
// pad. GPIO8-14: the pad's pull-up, then its pull-down, read back; a pad that
// follows neither is being driven from outside (its jumper wire, if fitted).
static void cmd_pads(void)
{
    int bad = 0;
    for (unsigned b = 0; b < 7; b++) {
        uint32_t pin = 15 + b;
        exerciser_wires(0x0Fu | (1u << b));
        bool high = gpio_get(pin);
        exerciser_wires(0x0Fu & ~(1u << b));
        bool low = !gpio_get(pin);
        printf("  GPIO%lu driven: high reads %s, low reads %s%s\r\n", (unsigned long)pin, high ? "high" : "LOW",
               low ? "low" : "HIGH", high && low ? "" : "  <- FAULT");
        bad += !(high && low);
    }
    exerciser_wires(0x0F);
    for (unsigned pin = FW_PIN_RESB; pin <= FW_PIN_A0; pin++) {
        gpio_pull_up(pin);
        busy_wait_us(50);
        bool up = gpio_get(pin);
        gpio_pull_down(pin);
        busy_wait_us(50);
        bool down = !gpio_get(pin);
        gpio_disable_pulls(pin);
        const char *verdict = up && down ? "follows its pulls (nothing connected)"
                            : up && !down ? "held high (by its wire, or floating high: RP2350-E9)"
                            : !up && down ? "held low by its wire" : "FAULT: reads the opposite of both pulls";
        printf("  GPIO%u: pull-up reads %s, pull-down reads %s: %s\r\n", pin, up ? "high" : "low", down ? "low" : "high",
               verdict);
    }
    printf("  %s\r\n", bad ? "driven pads FAULTY above" : "every driven pad goes high and low");
}

// Drives one pad from the chip itself, high then low, and reads it back: proves
// the pad's driver and input both work. Only for a pin with nothing connected,
// or the drive would fight whatever is.
static void cmd_selfdrive(unsigned pin)
{
    if (pin < FW_PIN_RESB || pin > FW_PIN_A0) {
        printf("  selfdrive is for GPIO8-14\r\n");
        return;
    }
    gpio_set_dir(pin, GPIO_OUT);
    gpio_put(pin, 1);
    busy_wait_us(20);
    bool high = gpio_get(pin);
    gpio_put(pin, 0);
    busy_wait_us(20);
    bool low = !gpio_get(pin);
    gpio_set_dir(pin, GPIO_IN);
    gpio_pull_down(pin);                // left pulled down, so it doesn't float up again
    busy_wait_us(50);
    bool after = gpio_get(pin);
    printf("  GPIO%u driven by itself: high reads %s, low reads %s; then an input with its pull-down: reads %s\r\n", pin,
           high ? "high" : "LOW", low ? "low" : "HIGH", after ? "high" : "low");
    printf("  %s\r\n", high && low ? "the pad drives and reads both ways" : "the pad is FAULTY");
}

// The sampler's first samples of the sweep's stream, at one delay.
static void cmd_raw(double mhz, uint32_t delay)
{
    reg_write(ATA_REG_LBA0, 0x55, mhz);
    reg_write(ATA_REG_LBA1, 0xAA, mhz);
    stream_t s;
    stream_init(&s, loop_words, sizeof loop_words / 4, mhz);
    for (int i = 0; i < 8; i++) {
        others(&s, 1);
        stream_cycle(&s, CYCLE_OUR_READ, ATA_REG_LBA0, -1, false);
        others(&s, 1);
        stream_cycle(&s, CYCLE_OUR_READ, ATA_REG_LBA1, -1, false);
    }
    size_t n = exerciser_sample_play(&s, delay, samples, 64, idle);
    printf("  %u samples at delay %lu:", (unsigned)n, (unsigned long)delay);
    for (size_t i = 0; i < n; i++)
        printf(" %02X", samples[i]);
    printf("\r\n  stream: %u words:", (unsigned)s.count);
    for (size_t i = 0; i < s.count && i < 24; i++)
        printf(" %08lX", (unsigned long)s.words[i]);
    printf("\r\n");
}

static void dispatch(char *line)
{
    char *argv[4] = { 0 };
    int argc = 0;
    for (char *t = strtok(line, " \t"); t && argc < 4; t = strtok(NULL, " \t"))
        argv[argc++] = t;
    if (!argc)
        return;
    double mhz = argc > 1 ? atof(argv[1]) : 1;
    if (mhz < 0.5 || mhz > 4)
        mhz = 1;
    if (!strcmp(argv[0], "info"))
        cmd_info();
    else if (!strcmp(argv[0], "sweep"))
        cmd_sweep(mhz, argc > 2 && atoi(argv[2]) > 0 ? (uint32_t)atoi(argv[2]) : 16);
    else if (!strcmp(argv[0], "bsy"))
        cmd_bsy(mhz);
    else if (!strcmp(argv[0], "soak"))
        cmd_soak(mhz, argc > 2 ? (uint32_t)atoi(argv[2]) : 10, 15);
    else if (!strcmp(argv[0], "selfdrive"))
        cmd_selfdrive(argc > 1 ? (unsigned)atoi(argv[1]) : 0);
    else if (!strcmp(argv[0], "pads"))
        cmd_pads();
    else if (!strcmp(argv[0], "bench")) {
        uint32_t c[3];
        bus_bench(c);
        printf("  per round, in cycles: ata_registers %lu.%03lu, 4 FIFO-word writes %lu.%03lu, 4 RAM writes %lu.%03lu\r\n",
               (unsigned long)(c[0] / 1000), (unsigned long)(c[0] % 1000), (unsigned long)(c[1] / 1000),
               (unsigned long)(c[1] % 1000), (unsigned long)(c[2] / 1000), (unsigned long)(c[2] % 1000));
    } else if (!strcmp(argv[0], "wires"))
        cmd_wires();
    else if (!strcmp(argv[0], "peek"))
        cmd_peek(mhz);
    else if (!strcmp(argv[0], "raw"))
        cmd_raw(mhz, argc > 2 ? (uint32_t)atoi(argv[2]) : 10);
    else if (!strcmp(argv[0], "spacing"))
        cmd_soak(mhz, 10, argc > 2 ? atoi(argv[2]) : 15);
    else
        printf("unknown: %s\r\n", argv[0]);
    printf("END\r\n");
}

void loopback_main(void (*banner)(void))
{
    pico_get_unique_board_id_string(serial, sizeof serial);
    patterndisk_init(&disk, 16u * 2048u);
    ata_init(&ata);
    drive_init(&drive, &ata, NULL, &disk.medium, now_us, NULL, PRODUCT_MODEL, serial, FW_VERSION);
    exerciser_init();           // RESB and the strobes high before the bus looks at them
    bus_start(&ata);
    bus_set_present(true);

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
