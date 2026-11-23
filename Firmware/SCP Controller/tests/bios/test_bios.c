// The stock BIOS against the controller's core: the boot probe, the BASIC
// storage commands on both media, mirroring, a card pulled between commands,
// and the media's busy times against the BIOS's own timeouts, at 1 and 2 MHz.
//
//   test_bios ROM [--rig PORT|auto [--bus-mhz N] [--for SECONDS]]
//
// It ends with a table of every timing case: the longest the controller kept
// BSY set, the BIOS's limit at that clock, and what the BIOS made of it.
//
// With --rig, the controller is the core on the media rig's Pico 2 (serve
// mode), on its real SD card and flash: the cases that don't depend on the
// models' timing run there, and the table is the real media's busy times. The
// card must be in the rig's slot; the cases hide it to test the built-in drive.
// On the loopback rig (a RAM disk, no slot) the SD card's cases are left out,
// and each access is a bus cycle through the PIO bus at --bus-mhz timing.
// --for repeats the rig's cases until that long has passed.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "machine.h"

#include "../unit/test.h"

static uint8_t rom[0x8000];
static const char *rom_name;
static char out[1 << 15];
static rig_t *rig;

static void note_busy(const machine_controller_t *c);

static machine_controller_t ctl(machine_t *m)
{
    machine_controller_t c;
    machine_controller(m, &c);
    return c;
}

static machine_t *boot(machine_config_t cfg, double mhz)
{
    cfg.rom = rom;
    cfg.mhz = mhz;
    cfg.rig = rig;
    if (!cfg.boot_us)
        cfg.boot_us = 250000;
    machine_t *m = machine_new(&cfg, NULL);
    // BIOS 1.x waits about 5 s at its ENTER=BASIC/ESC=MONITOR menu before going on.
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
        CHECK(run(m, "DIR", "DISK 0"));                     // whatever the disk holds: on a rig, maybe junk
        CHECK(!has("ERROR"));
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
        CHECK(run(m, "FORMAT\rY", "(Y/N) Y"));
        CHECK(run(m, "10 PRINT 1", NULL));
        CHECK(run(m, "SAVE \"ONSD\"", NULL));
        CHECK(!has("?SAVE ERROR"));
        CHECK(ctl(m).drive.sd.writes > 0);
        CHECK_EQ(0, ctl(m).drive.flash.writes);
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
        CHECK(ctl(m).drive.flash.writes > 0);
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
    CHECK(run(m, "FORMAT\rY", "(Y/N) Y"));                  // the disk may hold anything until then
    CHECK(run(m, "DIR", "DISK 0\r\n\r\n"));
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
        machine_controller_t c = ctl(m);
        CHECK(c.drive.flash.writes > 0);
        CHECK_EQ(0, c.drive.sd.writes);
        CHECK_EQ(0, c.drive.errors);
        note_busy(&c);
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
        machine_controller_t c = ctl(m);
        CHECK(c.drive.sd.writes > 0);
        CHECK_EQ(0, c.drive.flash.writes);
        CHECK_EQ(0, c.drive.errors);
        note_busy(&c);
        machine_free(m);
    }
}

// DISK N is DISK 0 on a chip of N disks: 16 on the board's 16 MB chip, 8 on the media rig's.
TEST(disk_n_is_disk_0_on_the_built_in_drive)
{
    machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20 }, 1);
    CHECK(m != NULL);
    if (!m) return;
    unsigned n = ctl(m).flash_disks;
    CHECK(n == 8 || n == 16);
    if (n < 5) { machine_free(m); return; }
    char line[64], want[64];
    CHECK(run(m, "FORMAT\rY", "(Y/N) Y"));
    CHECK(run(m, "10 PRINT 1", NULL));
    CHECK(run(m, "SAVE \"ZERO\"", NULL));
    snprintf(line, sizeof line, "DISK %u", n);
    CHECK(run(m, line, NULL));
    snprintf(want, sizeof want, "DISK %u\r\nZERO", n);
    CHECK(run(m, "DIR", want));                              // DISK N is DISK 0
    snprintf(line, sizeof line, "DISK %u", n + 4);
    CHECK(run(m, line, NULL));
    CHECK(run(m, "FORMAT\rY", "(Y/N) Y"));
    CHECK(run(m, "SAVE \"FOUR\"", NULL));
    CHECK(run(m, "DISK 4", NULL));
    CHECK(run(m, "DIR", "FOUR"));                            // DISK N+4 is DISK 4
    CHECK(run(m, "DISK 255", NULL));
    CHECK(run(m, "FORMAT\rY", "(Y/N) Y"));
    CHECK(run(m, "SAVE \"TOP\"", NULL));
    snprintf(line, sizeof line, "DISK %u", 255 % n);
    CHECK(run(m, line, NULL));
    CHECK(run(m, "DIR", "TOP"));                             // DISK 255 is DISK 255 mod N
    CHECK(run(m, "DISK 0", NULL));
    CHECK(run(m, "DIR", "ZERO"));
    CHECK(!has("TOP") && !has("FOUR"));
    machine_free(m);
}

TEST(no_mirroring_on_a_256_mb_card)
{
    machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20, .sd_sectors = 256u * 2048, .sd_start_us = 300000 }, 1);
    CHECK(m != NULL);
    if (!m) return;
    CHECK(ctl(m).sd_disks >= 256);
    CHECK(run(m, "DISK 16", NULL));
    CHECK(run(m, "FORMAT\rY", "(Y/N) Y"));
    CHECK(run(m, "DISK 0", NULL));
    CHECK(run(m, "FORMAT\rY", "(Y/N) Y"));
    CHECK(run(m, "10 PRINT 1", NULL));
    CHECK(run(m, "SAVE \"ZERO\"", NULL));
    CHECK(run(m, "DISK 16", NULL));
    CHECK(run(m, "DIR", "DISK 16\r\n\r\n"));               // its own disk, empty: no ZERO
    machine_free(m);
}

TEST(load_from_one_medium_save_to_the_other)
{
    machine_t *m = boot((machine_config_t){ .flash_bytes = 16u << 20, .sd_sectors = 256u * 2048, .sd_start_us = 300000 }, 1);
    CHECK(m != NULL);
    if (!m) return;
    machine_set_card(m, false);                             // the built-in drive's disk 0 emptied first
    CHECK(run(m, "FORMAT\rY", "(Y/N) Y"));
    machine_set_card(m, true);
    CHECK(run(m, "FORMAT\rY", "(Y/N) Y"));
    CHECK(run(m, "10 PRINT \"FROM SD\"", NULL));
    CHECK(run(m, "SAVE \"MOVE\"", NULL));
    CHECK(run(m, "NEW", NULL));
    CHECK(run(m, "LOAD \"MOVE\"", NULL));
    CHECK(ctl(m).sd_led);
    machine_set_card(m, false);                             // pulled between commands
    CHECK(!ctl(m).sd_led);
    CHECK(run(m, "DIR", NULL));
    CHECK(!has("MOVE"));                                    // the built-in drive's disks now
    CHECK(run(m, "SAVE \"MOVE\"", NULL));
    CHECK(run(m, "DIR", "MOVE"));
    CHECK(ctl(m).drive.flash.writes > 0);
    machine_set_card(m, true);                              // and back in
    CHECK(run(m, "NEW", NULL));
    CHECK(run(m, "LOAD \"MOVE\"", NULL));
    CHECK(run(m, "RUN", "FROM SD"));
    machine_controller_t c = ctl(m);
    CHECK_EQ(0, c.drive.errors);
    note_busy(&c);
    machine_free(m);
}

// The longest busy times seen on a rig, over every case: the real media's.
static drive_medium_stats_t rig_sd, rig_flash;
static uint32_t rig_longest_busy;

static void note_busy(const machine_controller_t *c)
{
    if (c->drive.sd.longest_read_us > rig_sd.longest_read_us) rig_sd.longest_read_us = c->drive.sd.longest_read_us;
    if (c->drive.sd.longest_write_us > rig_sd.longest_write_us) rig_sd.longest_write_us = c->drive.sd.longest_write_us;
    if (c->drive.flash.longest_read_us > rig_flash.longest_read_us) rig_flash.longest_read_us = c->drive.flash.longest_read_us;
    if (c->drive.flash.longest_write_us > rig_flash.longest_write_us) rig_flash.longest_write_us = c->drive.flash.longest_write_us;
    rig_sd.reads += c->drive.sd.reads;
    rig_sd.writes += c->drive.sd.writes;
    rig_flash.reads += c->drive.flash.reads;
    rig_flash.writes += c->drive.flash.writes;
    if (c->drive.longest_busy_us > rig_longest_busy) rig_longest_busy = c->drive.longest_busy_us;
}

static void rig_table(bool has_sd)
{
    double w1 = BIOS_WAIT_CYCLES / 1.0 / 1000.0, w2 = BIOS_WAIT_CYCLES / 2.0 / 1000.0;
    if (has_sd)
        printf("\n%s on the media rig: the real media's longest busy times, against the BIOS's wait\n", rom_name);
    else
        printf("\n%s on the loopback rig: its RAM disk's busy times (1 ms a read, 5 ms a write), through the bus\n",
               rom_name);
    printf("  %-26s %8s %8s %12s %12s\n", "medium", "reads", "writes", "longest ms", "1 / 2 MHz");
    printf("  %-26s %8u %8u %12.1f %5.0f / %.0f ms\n", "SD card: a read", rig_sd.reads, rig_sd.writes,
           rig_sd.longest_read_us / 1000.0, w1, w2);
    printf("  %-26s %8s %8s %12.1f %5.0f / %.0f ms\n", "SD card: a write", "", "", rig_sd.longest_write_us / 1000.0, w1, w2);
    printf("  %-26s %8u %8u %12.1f %5.0f / %.0f ms\n", "built-in drive: a read", rig_flash.reads, rig_flash.writes,
           rig_flash.longest_read_us / 1000.0, w1, w2);
    printf("  %-26s %8s %8s %12.1f %5.0f / %.0f ms\n", "built-in drive: a write", "", "",
           rig_flash.longest_write_us / 1000.0, w1, w2);
    printf("  round trips on the link: %llu\n", (unsigned long long)rig_round_trips(rig));
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
    double bus_mhz = 1, run_for = 0;
    const char *port = NULL;
    bool use_rig = false;
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "--rig") && i + 1 < argc) {
            use_rig = true;
            port = strcmp(argv[++i], "auto") ? argv[i] : NULL;
        } else if (!strcmp(argv[i], "--bus-mhz") && i + 1 < argc) {
            bus_mhz = atof(argv[++i]);
        } else if (!strcmp(argv[i], "--for") && i + 1 < argc) {
            run_for = atof(argv[++i]);
        } else {
            fprintf(stderr, "usage: test_bios ROM [--rig PORT|auto [--bus-mhz N] [--for SECONDS]]\n");
            return 2;
        }
    }
    if (use_rig) {
        rig = rig_open(port, bus_mhz);
        if (!rig)
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

    if (rig) {
        // The cases that hold on real media; the others set the models' timing.
        uint32_t w[SERVE_STAT_COUNT];
        rig_stats(rig, w);
        bool has_sd = w[SERVE_STAT_HAS_SD] != 0;
        time_t start = time(NULL);
        unsigned rounds = 0;
        uint32_t late = 0;
        do {
            RUN(the_probe_finds_the_built_in_drive_with_no_card);
            RUN(files_on_the_built_in_drive);
            RUN(disk_n_is_disk_0_on_the_built_in_drive);
            if (has_sd) {
                RUN(the_probe_finds_a_card_in_the_slot);
                RUN(files_on_the_sd_card);
                RUN(no_mirroring_on_a_256_mb_card);
                RUN(load_from_one_medium_save_to_the_other);
            }
            rig_stats(rig, w);
            late = w[SERVE_STAT_LATE];
            rounds++;
            if (run_for > 0)
                printf("  round %u: %.0f s, %d checks failed so far\n", rounds, difftime(time(NULL), start),
                       test_failures);
        } while (difftime(time(NULL), start) < run_for);
        rig_table(has_sd);
        printf("  %u rounds in %.0f s%s", rounds, difftime(time(NULL), start), has_sd ? "\n" : "");
        if (!has_sd)
            printf("; the bus at %g MHz timing, %u cycles played late\n", bus_mhz, late);
        rig_close(rig);
        return TEST_RESULT();
    }
    RUN(the_probe_finds_the_built_in_drive_with_no_card);
    RUN(the_probe_finds_a_card_in_the_slot);
    RUN(the_probe_outlasts_the_longest_power_on);
    RUN(a_power_on_longer_than_the_probe_finds_nothing);
    RUN(a_card_that_fails_to_start);
    RUN(files_on_the_built_in_drive);
    RUN(files_on_the_sd_card);
    RUN(disk_n_is_disk_0_on_the_built_in_drive);
    RUN(no_mirroring_on_a_256_mb_card);
    RUN(load_from_one_medium_save_to_the_other);
    RUN(busy_times_against_the_bios_waits);
    table();
    return TEST_RESULT();
}
