// The stock BIOS against the controller's core: the boot probe, the BASIC
// storage commands on both media, mirroring, a card pulled between commands,
// and the media's busy times against the BIOS's own timeouts, at 1 and 2 MHz.
//
//   test_bios ROM
//
// It ends with a table of every timing case: the longest the controller kept
// BSY set, the BIOS's limit at that clock, and what the BIOS made of it.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "machine.h"

#include "../unit/test.h"

static uint8_t rom[0x8000];
static const char *rom_name;
static char out[1 << 15];

static machine_t *boot(machine_config_t cfg, double mhz)
{
    cfg.rom = rom;
    cfg.mhz = mhz;
    if (!cfg.boot_us)
        cfg.boot_us = 250000;
    machine_t *m = machine_new(&cfg, NULL);
    // BIOS 1.7 waits about 5 s at its ENTER=BASIC/ESC=MONITOR menu before going on.
    if (!machine_wait(m, 0, "\r\nOK\r\n", 10)) {
        fprintf(stderr, "%s at %g MHz: no prompt after boot:\n%s\n", rom_name, mhz, m->out);
        machine_free(m);
        return NULL;
    }
    return m;
}

// Types a line; true if the prompt came back and `want` (if any) is in the reply.
static bool run(machine_t *m, const char *line, const char *want)
{
    bool ok = machine_command(m, line, out, sizeof out, 10);
    if (ok && want && !strstr(out, want)) {
        fprintf(stderr, "  \"%s\" gave\n%s  (no \"%s\")\n", line, out, want);
        return false;
    }
    if (!ok)
        fprintf(stderr, "  \"%s\": no prompt; gave\n%s\n", line, out);
    return ok;
}

static bool has(const char *want)
{
    return strstr(out, want) != NULL;
}

static const double MHZ[] = { 1, 2 };

// --- The boot probe ----------------------------------------------------------------

TEST(the_probe_finds_the_built_in_drive_with_no_card)
{
    for (int i = 0; i < 2; i++) {
        machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20 }, MHZ[i]);
        CHECK(m != NULL);
        if (!m) continue;
        CHECK(machine_peek(m, 0x030D) & 0x08);              // HW_PRESENT's HW_CF
        CHECK(run(m, "DIR", "DISK 0"));
        CHECK(!has("?"));
        machine_free(m);
    }
}

TEST(the_probe_finds_a_card_in_the_slot)
{
    for (int i = 0; i < 2; i++) {
        machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20, .sd_sectors = 256u * 2048, .sd_start_us = 300000 }, MHZ[i]);
        CHECK(m != NULL);
        if (!m) continue;
        CHECK(machine_peek(m, 0x030D) & 0x08);
        CHECK(run(m, "10 PRINT 1", NULL));
        CHECK(run(m, "SAVE \"ONSD\"", NULL));
        CHECK(m->drive.stats.sd.writes > 0);
        CHECK_EQ(0, m->drive.stats.flash.writes);
        machine_free(m);
    }
}

// The slowest power-on there is: the RP2350's start, then the whole 1.2 s wait
// for a card that never starts. The probe allows 3.0 s at 1 MHz and 1.5 s at 2.
TEST(the_probe_outlasts_the_longest_power_on)
{
    for (int i = 0; i < 2; i++) {
        machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20, .sd_sectors = 256u * 2048,
                                                .sd_start_us = 5000000, .boot_us = 250000 }, MHZ[i]);
        CHECK(m != NULL);
        if (!m) continue;
        CHECK(machine_peek(m, 0x030D) & 0x08);
        CHECK(run(m, "10 PRINT 1", NULL));
        CHECK(run(m, "SAVE \"FALLBACK\"", NULL));            // the card never started: the built-in drive answers
        CHECK(m->drive.stats.flash.writes > 0);
        machine_free(m);
    }
}

// And the other way: a power-on longer than the probe's wait finds no storage,
// so the case above is the probe's real limit and not a harness that never times out.
TEST(a_power_on_longer_than_the_probe_finds_nothing)
{
    machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20, .sd_sectors = 256u * 2048,
                                            .sd_start_us = 5000000, .boot_us = 400000 }, 2);
    CHECK(m != NULL);
    if (!m) return;
    CHECK(!(machine_peek(m, 0x030D) & 0x08));               // 1.6 s against the probe's 1.5 s at 2 MHz
    machine_free(m);
}

TEST(a_card_that_fails_to_start)
{
    machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20, .sd_sectors = 256u * 2048,
                                            .sd_start_us = 400000, .sd_start_fails = true }, 2);
    CHECK(m != NULL);
    if (!m) return;
    CHECK(machine_peek(m, 0x030D) & 0x08);
    CHECK(run(m, "DIR", "DISK 0"));
    machine_free(m);
}

// --- Files -----------------------------------------------------------------------------

static void files_on(machine_t *m)
{
    CHECK(run(m, "10 PRINT \"HELLO\"", NULL));
    CHECK(run(m, "20 FOR I=1 TO 3:PRINT I:NEXT", NULL));
    CHECK(run(m, "SAVE \"PROG\"", NULL));
    CHECK(!has("?SAVE ERROR"));
    CHECK(run(m, "DIR", "PROG"));
    CHECK(run(m, "NEW", NULL));
    CHECK(run(m, "LOAD \"PROG\"", NULL));
    CHECK(!has("?LOAD ERROR"));
    CHECK(run(m, "RUN", "HELLO\r\n 1\r\n 2\r\n 3\r\n"));
    CHECK(run(m, "BSAVE 40960,1000,\"ROM.BIN\"", NULL));
    CHECK(!has("?SAVE ERROR"));
    CHECK(run(m, "BLOAD 8192,\"ROM.BIN\"", NULL));
    CHECK(!has("?LOAD ERROR"));
    int same = 1;
    for (int i = 0; i < 1000; i++)
        same &= machine_peek(m, (uint16_t)(8192 + i)) == machine_peek(m, (uint16_t)(40960 + i));
    CHECK(same);
    CHECK(run(m, "DIR", "ROM     .BIN 1000"));       // DIR pads names to 8.3
    CHECK(run(m, "DEL \"PROG\"", NULL));
    CHECK(!has("?DEL ERROR"));
    CHECK(run(m, "DIR", NULL));
    CHECK(!has("PROG"));
    CHECK(run(m, "LOAD \"PROG\"", "?LOAD ERROR"));
    CHECK(run(m, "FORMAT\rY", "(Y/N) Y"));
    CHECK(run(m, "DIR", NULL));
    CHECK(!has("ROM     .BIN"));
}

TEST(files_on_the_built_in_drive)
{
    for (int i = 0; i < 2; i++) {
        machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20 }, MHZ[i]);
        CHECK(m != NULL);
        if (!m) continue;
        files_on(m);
        CHECK(m->drive.stats.flash.writes > 0);
        CHECK_EQ(0, m->drive.stats.errors);
        machine_free(m);
    }
}

TEST(files_on_the_sd_card)
{
    for (int i = 0; i < 2; i++) {
        machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20, .sd_sectors = 256u * 2048, .sd_start_us = 300000 }, MHZ[i]);
        CHECK(m != NULL);
        if (!m) continue;
        files_on(m);
        CHECK(m->drive.stats.sd.writes > 0);
        CHECK_EQ(0, m->drive.stats.flash.writes);
        CHECK_EQ(0, m->drive.stats.errors);
        machine_free(m);
    }
}

TEST(disk_16_is_disk_0_on_the_16_mb_chip)
{
    machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20 }, 1);
    CHECK(m != NULL);
    if (!m) return;
    CHECK(run(m, "10 PRINT 1", NULL));
    CHECK(run(m, "SAVE \"ZERO\"", NULL));
    CHECK(run(m, "DISK 16", NULL));
    CHECK(run(m, "DIR", "DISK 16\r\nZERO"));
    CHECK(run(m, "DISK 20", NULL));
    CHECK(run(m, "SAVE \"TWENTY\"", NULL));
    CHECK(run(m, "DISK 4", NULL));
    CHECK(run(m, "DIR", "TWENTY"));
    CHECK(run(m, "DISK 255", NULL));                        // 255 mod 16: DISK 15, empty
    CHECK(run(m, "DIR", "DISK 255\r\n\r\n"));
    machine_free(m);
}

TEST(no_mirroring_on_a_256_mb_card)
{
    machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20, .sd_sectors = 256u * 2048, .sd_start_us = 300000 }, 1);
    CHECK(m != NULL);
    if (!m) return;
    CHECK(run(m, "10 PRINT 1", NULL));
    CHECK(run(m, "SAVE \"ZERO\"", NULL));
    CHECK(run(m, "DISK 16", NULL));
    CHECK(run(m, "DIR", "DISK 16\r\n\r\n"));
    machine_free(m);
}

TEST(load_from_one_medium_save_to_the_other)
{
    machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20, .sd_sectors = 256u * 2048, .sd_start_us = 300000 }, 1);
    CHECK(m != NULL);
    if (!m) return;
    CHECK(run(m, "10 PRINT \"FROM SD\"", NULL));
    CHECK(run(m, "SAVE \"MOVE\"", NULL));
    CHECK(run(m, "NEW", NULL));
    CHECK(run(m, "LOAD \"MOVE\"", NULL));
    CHECK(drive_leds(&m->drive, (uint32_t)machine_us(m)).sd);
    m->sd.in = m->sd.started = false;                       // pulled between commands
    CHECK(!drive_leds(&m->drive, (uint32_t)machine_us(m)).sd);
    CHECK(run(m, "DIR", NULL));
    CHECK(!has("MOVE"));                                    // the built-in drive's disks now
    CHECK(run(m, "SAVE \"MOVE\"", NULL));
    CHECK(run(m, "DIR", "MOVE"));
    CHECK(m->drive.stats.flash.writes > 0);
    m->sd.in = m->sd.started = true;                        // and back in
    m->sd.medium.generation++;
    CHECK(run(m, "NEW", NULL));
    CHECK(run(m, "LOAD \"MOVE\"", NULL));
    CHECK(run(m, "RUN", "FROM SD"));
    machine_free(m);
}

// --- Busy times against the BIOS's waits -----------------------------------------------

typedef struct {
    const char *what;
    double mhz;
    uint32_t longest_us;
    double limit_us;
    const char *bios_said;
} timing_row_t;
static timing_row_t rows[32];
static int row_count;

static void row(const char *what, double mhz, uint32_t longest, const char *said)
{
    if (row_count < 32)
        rows[row_count++] = (timing_row_t){ what, mhz, longest, BIOS_WAIT_CYCLES / mhz, said };
}

// A 3.5 KB file fills sectors 1-7, so the directory's 4 KB erase sector is full
// and deleting the file is the worst write there is: an erase and 14 pages.
static void worst_flash_write(const media_timing_t *t, double mhz, bool expect_ok)
{
    machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20, .flash_timing = t }, mhz);
    CHECK(m != NULL);
    if (!m) return;
    CHECK(run(m, "BSAVE 40960,3584,\"BIG\"", NULL));
    CHECK(!has("?SAVE ERROR"));
    size_t from = m->job_count;
    CHECK(run(m, "DEL \"BIG\"", NULL));
    bool failed = has("?DEL ERROR");
    CHECK_EQ(!expect_ok, failed);
    uint32_t longest = machine_longest(m, from, ATA_JOB_WRITE);
    char what[64];
    snprintf(what, sizeof what, "%s: erase + 14 pages", t->name);
    row(strdup(what), mhz, longest, failed ? "?DEL ERROR" : "OK");
    // Either way the controller finishes the write, and the next command works.
    CHECK(run(m, "DIR", "DISK 0"));
    CHECK(!has("?"));
    machine_free(m);
}

static void sd_write(const media_timing_t *t, double mhz, bool expect_ok)
{
    machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20, .sd_sectors = 256u * 2048,
                                            .sd_start_us = 300000, .sd_timing = t }, mhz);
    CHECK(m != NULL);
    if (!m) return;
    CHECK(run(m, "10 PRINT 1", NULL));
    size_t from = m->job_count;
    CHECK(run(m, "SAVE \"SD\"", NULL));
    bool failed = has("?SAVE ERROR");
    CHECK_EQ(!expect_ok, failed);
    char what[64];
    snprintf(what, sizeof what, "%s: one sector", t->name);
    row(strdup(what), mhz, machine_longest(m, from, ATA_JOB_WRITE), failed ? "?SAVE ERROR" : "OK");
    from = m->job_count;
    CHECK(run(m, "DIR", NULL));
    char what2[64];
    snprintf(what2, sizeof what2, "%s: read", t->name);
    row(strdup(what2), mhz, machine_longest(m, from, ATA_JOB_READ), has("?") ? "error" : "OK");
    machine_free(m);
}

TEST(busy_times_against_the_bios_waits)
{
    // K33's predictions: everything fits at 1 MHz; at 2 MHz the flash's worst
    // erase and an SDXC card's worst write run over the BIOS's 0.43 s.
    worst_flash_write(&FLASH_TYPICAL, 1, true);
    worst_flash_write(&FLASH_TYPICAL, 2, true);
    worst_flash_write(&FLASH_WORST, 1, true);
    worst_flash_write(&FLASH_WORST, 2, false);
    sd_write(&SD_TYPICAL, 2, true);
    sd_write(&SD_SDHC_WORST, 1, true);
    sd_write(&SD_SDHC_WORST, 2, true);
    sd_write(&SD_SDXC_WORST, 1, true);
    sd_write(&SD_SDXC_WORST, 2, false);
}

static void table(void)
{
    printf("\n%s: busy times against the BIOS's wait (65536 polls of 13 cycles)\n", rom_name);
    printf("  %-32s %5s %12s %12s  %s\n", "case", "MHz", "longest ms", "limit ms", "BIOS");
    for (int i = 0; i < row_count; i++)
        printf("  %-32s %5g %12.1f %12.1f  %s\n", rows[i].what, rows[i].mhz, rows[i].longest_us / 1000.0,
               rows[i].limit_us / 1000.0, rows[i].bios_said);
    printf("  power-on: the probe allows %.0f ms at 1 MHz and %.0f ms at 2 MHz; the longest power-on is %u ms\n",
           BIOS_PROBE_CYCLES / 1000.0, BIOS_PROBE_CYCLES / 2000.0, 250 + DRIVE_BOOT_SD_WAIT_MS);
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "usage: test_bios ROM\n");
        return 2;
    }
    FILE *f = fopen(argv[1], "rb");
    if (!f || fread(rom, 1, sizeof rom, f) != sizeof rom) {
        perror(argv[1]);
        return 2;
    }
    fclose(f);
    rom_name = strrchr(argv[1], '/') ? strrchr(argv[1], '/') + 1 : argv[1];
    printf("%s\n", rom_name);

    RUN(the_probe_finds_the_built_in_drive_with_no_card);
    RUN(the_probe_finds_a_card_in_the_slot);
    RUN(the_probe_outlasts_the_longest_power_on);
    RUN(a_power_on_longer_than_the_probe_finds_nothing);
    RUN(a_card_that_fails_to_start);
    RUN(files_on_the_built_in_drive);
    RUN(files_on_the_sd_card);
    RUN(disk_16_is_disk_0_on_the_16_mb_chip);
    RUN(no_mirroring_on_a_256_mb_card);
    RUN(load_from_one_medium_save_to_the_other);
    RUN(busy_times_against_the_bios_waits);
    table();
    return TEST_RESULT();
}
