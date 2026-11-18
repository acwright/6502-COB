// The bus side and the worker together, on the SD card's stand-in and the
// built-in drive: the BIOS's own sequence, the choice of medium, mirroring, a
// card pulled mid-command, a reset during an erase, IDENTIFY and the LEDs.
#include "fakes.h"
#include "identify.h"

#include "test.h"

static fake_clock_t clk;
static ata_t a;
static drive_t d;
static ram_medium_t sd;
static fake_nor_t chip;
static flashdisk_t flash;

// A machine with a 16 MB built-in drive and an SD card of `sd_sectors` (0: no
// card in the slot).
static void machine(uint32_t sd_sectors)
{
    clk.us = 1000;
    ata_init(&a);
    ram_init(&sd, sd_sectors ? sd_sectors : 2048);
    sd.in = sd.started = sd_sectors != 0;
    sd.clock = &clk;
    sd.write_us = 3000;
    fnor_init(&chip, 16u << 20);
    chip.clock = &clk;
    flashdisk_init(&flash, &chip.nor);
    drive_init(&d, &a, &sd.medium, &flash.medium, fake_now, &clk, "AC6502 Storage Card Pro", "E66138935F2A1B2C", "0.1.0");
    ata_set_present(&a, drive_choose(&d) != NULL);
}

static void done(void)
{
    ram_free(&sd);
    fnor_free(&chip);
}

static uint8_t status(void)
{
    settle(&a, &d);
    return ata_read(&a, ATA_REG_STATUS);
}

// The BIOS's StSetupLba and command, then its wait (StWaitDrq / StWaitReady).
static void command(uint8_t cmd, uint32_t lba, uint8_t count)
{
    ata_write(&a, ATA_REG_COUNT, count);
    ata_write(&a, ATA_REG_LBA0, (uint8_t)lba);
    ata_write(&a, ATA_REG_LBA1, (uint8_t)(lba >> 8));
    ata_write(&a, ATA_REG_LBA2, (uint8_t)(lba >> 16));
    ata_write(&a, ATA_REG_LBA3, (uint8_t)(0xE0 | (lba >> 24)));
    ata_write(&a, ATA_REG_STATUS, cmd);
}

static bool write_sector(uint32_t lba, const uint8_t *p)
{
    command(ATA_CMD_WRITE, lba, 1);
    if (status() != 0x58)
        return false;
    for (int i = 0; i < 512; i++)
        ata_write(&a, ATA_REG_DATA, p[i]);
    return status() == 0x50;
}

static bool read_sector(uint32_t lba, uint8_t *p)
{
    command(ATA_CMD_READ, lba, 1);
    if (status() != 0x58)
        return false;
    for (int i = 0; i < 512; i++)
        p[i] = ata_read(&a, ATA_REG_DATA);
    return status() == 0x50;
}

static uint8_t buf[512], back[512];

static void pattern(uint8_t *p, int seed)
{
    for (int i = 0; i < 512; i++)
        p[i] = (uint8_t)(i * 13 + seed);
}

TEST(the_bios_sequence_on_the_built_in_drive)
{
    machine(0);
    CHECK_EQ(0x50, status());
    ata_write(&a, ATA_REG_ERROR, 0x01);                 // StInit: Set Features, 8-bit
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_SET_FEAT);
    CHECK_EQ(0x50, status());
    CHECK(read_sector(0, back));                        // a blank chip: an empty directory
    int nonzero = 0;
    for (int i = 0; i < 512; i++)
        nonzero += back[i] != 0;
    CHECK_EQ(0, nonzero);
    pattern(buf, 1);
    CHECK(write_sector(5, buf));
    CHECK(read_sector(5, back));
    CHECK(memcmp(buf, back, 512) == 0);
    CHECK_EQ(1, d.stats.flash.writes);
    CHECK_EQ(0, d.stats.sd.writes);
    done();
}

TEST(the_sd_card_answers_when_its_in)
{
    machine(256u * 2048);
    pattern(buf, 2);
    CHECK(write_sector(77, buf));
    CHECK(memcmp(sd.data + 77 * 512, buf, 512) == 0);
    CHECK_EQ(1, d.stats.sd.writes);
    CHECK_EQ(0, d.stats.flash.writes);
    CHECK(drive_leds(&d, clk.us).sd);
    sd.in = sd.started = false;                         // pulled between commands: the built-in drive answers
    CHECK(!drive_leds(&d, clk.us).sd);
    CHECK(read_sector(77, back));
    int nonzero = 0;
    for (int i = 0; i < 512; i++)
        nonzero += back[i] != 0;
    CHECK_EQ(0, nonzero);
    CHECK(write_sector(77, buf));                       // LOAD from one, SAVE to the other
    CHECK_EQ(1, d.stats.flash.writes);
    sd.in = sd.started = true;
    CHECK(read_sector(77, back));
    CHECK(memcmp(buf, back, 512) == 0);
    CHECK_EQ(1, d.stats.sd.reads);
    done();
}

TEST(disk_16_is_disk_0_on_the_16_mb_chip)
{
    machine(0);
    pattern(buf, 3);
    CHECK(write_sector(0, buf));                        // DISK 0's directory
    CHECK(read_sector(16u * 2048, back));               // DISK 16's
    CHECK(memcmp(buf, back, 512) == 0);
    pattern(buf, 4);
    CHECK(write_sector(20u * 2048 + 9, buf));           // DISK 20 lands on DISK 4
    CHECK(read_sector(4u * 2048 + 9, back));
    CHECK(memcmp(buf, back, 512) == 0);
    done();
}

TEST(a_card_under_1_mb_answers_idnf)
{
    machine(2000);
    command(ATA_CMD_READ, 0, 1);
    CHECK_EQ(0x51, status());
    CHECK_EQ(ATA_ER_IDNF | ATA_ER_ABRT, ata_read(&a, ATA_REG_ERROR));
    done();
}

TEST(a_card_pulled_mid_read)
{
    machine(256u * 2048);
    command(ATA_CMD_READ, 10, 2);
    CHECK_EQ(0x58, status());
    for (int i = 0; i < 512; i++)
        ata_read(&a, ATA_REG_DATA);
    sd.in = sd.started = false;                         // between the two sectors
    CHECK_EQ(0x51, status());
    CHECK_EQ(ATA_ER_ABRT, ata_read(&a, ATA_REG_ERROR));
    CHECK_EQ(0, d.stats.flash.reads);                   // never switched to the built-in drive mid-command
    done();
}

TEST(a_card_swapped_mid_command)
{
    machine(256u * 2048);
    command(ATA_CMD_READ, 10, 2);
    CHECK_EQ(0x58, status());
    for (int i = 0; i < 512; i++)
        ata_read(&a, ATA_REG_DATA);
    sd.medium.generation++;                             // pulled, another card in and started, between the sectors
    CHECK_EQ(0x51, status());
    CHECK_EQ(ATA_ER_ABRT, ata_read(&a, ATA_REG_ERROR));
    command(ATA_CMD_READ, 10, 1);                       // the next command takes the new card
    CHECK_EQ(0x58, status());
    done();
}

TEST(a_card_pulled_and_back_mid_command)
{
    machine(256u * 2048);
    command(ATA_CMD_READ, 10, 2);
    CHECK_EQ(0x58, status());
    for (int i = 0; i < 512; i++)
        ata_read(&a, ATA_REG_DATA);
    sd.started = false;                                 // in the slot again, but not started yet
    CHECK_EQ(0x51, status());
    CHECK_EQ(ATA_ER_ABRT, ata_read(&a, ATA_REG_ERROR));
    done();
}

static void pull(void *unused)
{
    (void)unused;
    sd.in = false;
}

TEST(a_card_pulled_mid_write)
{
    machine(256u * 2048);
    command(ATA_CMD_WRITE, 10, 2);
    CHECK_EQ(0x58, status());
    for (int i = 0; i < 512; i++)
        ata_write(&a, ATA_REG_DATA, 1);
    sd.on_access = pull;                                // gone while the sector is being written
    CHECK_EQ(0x51, status());
    CHECK_EQ(ATA_ER_ABRT, ata_read(&a, ATA_REG_ERROR));
    CHECK_EQ(1, d.stats.errors);
    sd.on_access = NULL;
    CHECK_EQ(0, d.stats.flash.writes);
    done();
}

TEST(a_card_put_in_mid_command_waits_for_the_next)
{
    machine(256u * 2048);
    sd.in = sd.started = false;
    command(ATA_CMD_READ, 10, 2);
    CHECK_EQ(0x58, status());
    sd.in = sd.started = true;
    for (int i = 0; i < 512; i++)
        ata_read(&a, ATA_REG_DATA);
    CHECK_EQ(0x58, status());
    CHECK_EQ(2, d.stats.flash.reads);
    CHECK_EQ(0, d.stats.sd.reads);
    done();
}

TEST(nothing_to_answer_with)
{
    machine(0);
    chip.nor.size = 0;                                  // a dead chip, and no card
    CHECK(drive_choose(&d) == NULL);
    ata_init(&a);
    ata_set_present(&a, drive_choose(&d) != NULL);
    CHECK_EQ(0x00, status());                           // an empty socket
    ata_set_present(&a, true);                          // and if the controller answered anyway
    command(ATA_CMD_READ, 0, 1);
    CHECK_EQ(0x51, status());
    CHECK_EQ(ATA_ER_AMNF, ata_read(&a, ATA_REG_ERROR));
    done();
}

static void reset_pulse(void *unused)
{
    (void)unused;
    ata_resb(&a, true);
    ata_resb(&a, false);
    CHECK_EQ(0x80, ata_read(&a, ATA_REG_STATUS));       // the erase isn't done: still BSY
}

TEST(a_reset_during_an_erase_waits_for_it)
{
    machine(0);
    pattern(buf, 5);
    CHECK(write_sector(3, buf));
    pattern(buf, 6);                                    // needs an erase
    command(ATA_CMD_WRITE, 3, 1);
    CHECK_EQ(0x58, status());
    for (int i = 0; i < 512; i++)
        ata_write(&a, ATA_REG_DATA, buf[i]);
    chip.on_erase = reset_pulse;
    CHECK_EQ(0x50, status());                           // the write finished, then the reset took effect
    chip.on_erase = NULL;
    CHECK_EQ(1, chip.erases);
    CHECK_EQ(0, ata_read(&a, ATA_REG_LBA0));            // registers reset
    CHECK(read_sector(3, back));                        // and the sector was written whole
    CHECK(memcmp(buf, back, 512) == 0);
    done();
}

TEST(identify_describes_the_medium)
{
    machine(0);
    pattern(buf, 7);
    CHECK(write_sector(1, buf));                        // so the busy times aren't zero
    command(ATA_CMD_IDENTIFY, 0, 1);
    CHECK_EQ(0x58, status());
    uint8_t id[512];
    for (int i = 0; i < 512; i++)
        id[i] = ata_read(&a, ATA_REG_DATA);
    CHECK_EQ(0x50, status());
    CHECK_EQ(0x848A, identify_word(id, 0));
    CHECK_EQ(0x0200, identify_word(id, 49));
    CHECK_EQ(32768, identify_word(id, 60) | (identify_word(id, 61) << 16));
    CHECK_EQ(0, identify_word(id, 7));
    CHECK_EQ(32768, identify_word(id, 8));
    CHECK_EQ('A', id[27 * 2 + 1]);                      // "AC6502": first character in the high byte
    CHECK_EQ('C', id[27 * 2]);
    CHECK_EQ(' ', id[46 * 2]);                          // space padded to 40
    CHECK_EQ('0', id[23 * 2 + 1]);                      // firmware "0.1.0"
    CHECK_EQ('.', id[23 * 2]);
    CHECK_EQ('E', id[10 * 2 + 1]);                      // serial
    CHECK_EQ(IDENTIFY_MEDIUM_FLASH, identify_word(id, 134));
    CHECK_EQ(16, identify_word(id, 135));
    uint32_t longest = identify_word(id, 128) | ((uint32_t)identify_word(id, 129) << 16);
    uint32_t flash_write = identify_word(id, 132) | ((uint32_t)identify_word(id, 133) << 16);
    CHECK_EQ(2 * NOR_PROGRAM_US, flash_write);          // two pages programmed, on the model's clock
    CHECK_EQ(flash_write, longest);
    CHECK_EQ(0, identify_word(id, 136));
    done();
}

TEST(identify_on_the_sd_card)
{
    machine(3u * 2048 + 100);
    command(ATA_CMD_IDENTIFY, 0, 1);
    CHECK_EQ(0x58, status());
    uint8_t id[512];
    for (int i = 0; i < 512; i++)
        id[i] = ata_read(&a, ATA_REG_DATA);
    CHECK_EQ(IDENTIFY_MEDIUM_SD, identify_word(id, 134));
    CHECK_EQ(3, identify_word(id, 135));
    CHECK_EQ(3 * 2048, identify_word(id, 60));
    done();
}

TEST(busy_times_are_kept)
{
    machine(256u * 2048);
    pattern(buf, 8);
    CHECK(write_sector(2, buf));
    CHECK_EQ(3000, d.stats.sd.longest_write_us);
    sd.in = false;
    pattern(buf, 9);
    CHECK(write_sector(2, buf));                        // blank space on the chip: in place
    pattern(buf, 10);
    CHECK(write_sector(2, buf));                        // now an erase
    CHECK_EQ(NOR_ERASE_US + 2 * NOR_PROGRAM_US, d.stats.flash.longest_write_us);
    CHECK_EQ(NOR_ERASE_US + 2 * NOR_PROGRAM_US, d.stats.longest_busy_us);
    done();
}

TEST(the_leds)
{
    machine(0);
    drive_leds_t l = drive_leds(&d, clk.us);
    CHECK(!l.sd && !l.act);
    pattern(buf, 11);
    CHECK(write_sector(0, buf));
    uint32_t end = d.last_end_us;
    CHECK(drive_leds(&d, end).act);
    CHECK(drive_leds(&d, end + DRIVE_ACT_HOLD_US - 1).act);
    CHECK(!drive_leds(&d, end + DRIVE_ACT_HOLD_US).act);
    d.last_end_us = 0xFFFFFFF0u;                        // across the clock's wrap
    CHECK(drive_leds(&d, 0x10).act);
    d.last_end_us = 0xFFFF0000u;                        // 70 ms later, past the wrap: off
    CHECK(!drive_leds(&d, 0xFFFF0000u + 70000u).act);
    done();
}

TEST(when_power_on_is_over)
{
    CHECK(drive_boot_settled(false, false, false, 0));          // no card: at once
    CHECK(!drive_boot_settled(true, false, false, 0));          // a card starting: wait
    CHECK(!drive_boot_settled(true, false, false, 1199));
    CHECK(drive_boot_settled(true, false, false, 1200));        // ... up to 1.2 s
    CHECK(drive_boot_settled(true, true, false, 300));          // started
    CHECK(drive_boot_settled(true, false, true, 300));          // failed to
}

int main(void)
{
    RUN(the_bios_sequence_on_the_built_in_drive);
    RUN(the_sd_card_answers_when_its_in);
    RUN(disk_16_is_disk_0_on_the_16_mb_chip);
    RUN(a_card_under_1_mb_answers_idnf);
    RUN(a_card_pulled_mid_read);
    RUN(a_card_pulled_mid_write);
    RUN(a_card_put_in_mid_command_waits_for_the_next);
    RUN(a_card_swapped_mid_command);
    RUN(a_card_pulled_and_back_mid_command);
    RUN(nothing_to_answer_with);
    RUN(a_reset_during_an_erase_waits_for_it);
    RUN(identify_describes_the_medium);
    RUN(identify_on_the_sd_card);
    RUN(busy_times_are_kept);
    RUN(the_leds);
    RUN(when_power_on_is_over);
    return TEST_RESULT();
}
