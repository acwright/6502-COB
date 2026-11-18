// Mirroring, the JEDEC ID, and the built-in drive's storage on a NOR chip.
#include "fakes.h"

#include "test.h"

static uint32_t map(uint32_t sectors, uint32_t lba)
{
    uint32_t s = 0xFFFFFFFF;
    CHECK(media_map(sectors, lba, &s));
    return s;
}

TEST(mirroring_on_a_16_mb_chip)
{
    const uint32_t sectors = 16u * 2048;
    CHECK_EQ(16, media_disks(sectors));
    CHECK_EQ(5, map(sectors, 5));                       // below the end: sector n is sector n
    CHECK_EQ(sectors - 1, map(sectors, sectors - 1));
    CHECK_EQ(0, map(sectors, 16 * 2048));               // DISK 16 is DISK 0
    CHECK_EQ(4 * 2048 + 33, map(sectors, 20 * 2048 + 33));   // DISK 20 is DISK 4
    CHECK_EQ(15 * 2048 + 2047, map(sectors, 255 * 2048 + 2047));
}

TEST(mirroring_by_a_count_that_isnt_a_power_of_two)
{
    const uint32_t sectors = 3u * 2048 + 1000;          // three whole disks, and a part-disk left unused
    CHECK_EQ(3, media_disks(sectors));
    CHECK_EQ(6143, map(sectors, 6143));
    CHECK_EQ(0, map(sectors, 6144));                    // the part-disk is never reached
    CHECK_EQ(856, map(sectors, 7000));
    CHECK_EQ(2 * 2048, map(sectors, 5 * 2048));         // DISK 5 is DISK 2
}

TEST(no_mirroring_from_256_mb)
{
    const uint32_t sectors = 256u * 2048;
    CHECK_EQ(256, media_disks(sectors));
    CHECK_EQ(255 * 2048 + 7, map(sectors, 255 * 2048 + 7));
    const uint32_t big = 62521344;                      // a 32 GB card
    CHECK_EQ(0x0FFFFFF, map(big, 0x0FFFFFF));
    CHECK_EQ(0x0FFFFFFF % (media_disks(big) * 2048), map(big, 0x0FFFFFFF));
}

TEST(a_medium_under_1_mb_holds_no_disk)
{
    uint32_t s = 77;
    CHECK_EQ(0, media_disks(2047));
    CHECK(!media_map(2047, 0, &s));
    CHECK(!media_map(0, 0, &s));
    CHECK_EQ(77, s);
}

TEST(jedec_sizes)
{
    const struct { uint8_t id[3]; uint32_t size; } cases[] = {
        { { 0xEF, 0x40, 0x14 }, 1u << 20 },
        { { 0xEF, 0x40, 0x17 }, 8u << 20 },     // W25Q64: the media rig's breakout
        { { 0xEF, 0x40, 0x18 }, 16u << 20 },    // W25Q128JVFIQ: the BOM's part
        { { 0xEF, 0x70, 0x18 }, 16u << 20 },    // W25Q128JV-IM
        { { 0xEF, 0x40, 0x19 }, 32u << 20 },
        { { 0xEF, 0x40, 0x20 }, 64u << 20 },
        { { 0xEF, 0x40, 0x21 }, 128u << 20 },   // W25Q01JVSFIQ
        { { 0xEF, 0x40, 0x1A }, 0 },
        { { 0xEF, 0x40, 0x22 }, 0 },
        { { 0xEF, 0x60, 0x18 }, 0 },            // W25Q128FW: a 1.8 V part
        { { 0xC2, 0x20, 0x18 }, 0 },            // not Winbond
        { { 0xFF, 0xFF, 0xFF }, 0 },            // no chip
        { { 0x00, 0x00, 0x00 }, 0 },
    };
    for (unsigned i = 0; i < sizeof cases / sizeof cases[0]; i++)
        CHECK_EQ(cases[i].size, nor_size_from_jedec(cases[i].id));
    CHECK(!nor_needs_4byte(16u << 20));
    CHECK(nor_needs_4byte(32u << 20));
    CHECK(nor_needs_4byte(128u << 20));
}

static fake_nor_t chip;
static flashdisk_t disk;
static uint8_t buf[512], back[512];

static void fresh(uint32_t size)
{
    fnor_init(&chip, size);
    flashdisk_init(&disk, &chip.nor);
}

static void pattern(uint8_t *p, int seed)
{
    for (int i = 0; i < 512; i++)
        p[i] = (uint8_t)(i * 7 + seed);
}

static bool all(const uint8_t *p, uint8_t v, size_t n)
{
    for (size_t i = 0; i < n; i++)
        if (p[i] != v)
            return false;
    return true;
}

TEST(a_blank_chip_reads_as_zeros)
{
    fresh(1u << 20);
    medium_t *m = &disk.medium;
    CHECK(m->ready(m));
    CHECK_EQ(2048, m->sectors(m));
    memset(back, 0xAA, 512);
    CHECK_EQ(MEDIUM_OK, m->read(m, 0, back));
    CHECK(all(back, 0, 512));
    CHECK_EQ(MEDIUM_OK, m->read(m, 2047, back));
    CHECK(all(back, 0, 512));
    CHECK_EQ(MEDIUM_FAILED, m->read(m, 2048, back));
    fnor_free(&chip);
}

TEST(stored_inverted_and_written_in_place_on_blank_space)
{
    fresh(1u << 20);
    medium_t *m = &disk.medium;
    pattern(buf, 1);
    CHECK_EQ(MEDIUM_OK, m->write(m, 9, buf));
    CHECK_EQ(MEDIUM_OK, m->read(m, 9, back));
    CHECK(memcmp(buf, back, 512) == 0);
    CHECK_EQ((uint8_t)~buf[0], chip.data[9 * 512]);
    CHECK_EQ((uint8_t)~buf[511], chip.data[9 * 512 + 511]);
    CHECK_EQ(0, chip.erases);
    CHECK_EQ(2, chip.programs);
    CHECK_EQ(1, disk.stats.in_place);
    CHECK_EQ(0, chip.violations);
    fnor_free(&chip);
}

TEST(a_write_that_changes_nothing_writes_nothing)
{
    fresh(1u << 20);
    medium_t *m = &disk.medium;
    memset(buf, 0, 512);                                // zeros onto a blank chip: already there
    CHECK_EQ(MEDIUM_OK, m->write(m, 3, buf));
    pattern(buf, 2);
    CHECK_EQ(MEDIUM_OK, m->write(m, 4, buf));
    uint32_t programs = chip.programs;
    CHECK_EQ(MEDIUM_OK, m->write(m, 4, buf));           // the same data again
    CHECK_EQ(programs, chip.programs);
    CHECK_EQ(0, chip.erases);
    CHECK_EQ(2, disk.stats.unchanged);
    fnor_free(&chip);
}

TEST(an_overwrite_erases_and_keeps_its_neighbours)
{
    fresh(1u << 20);
    medium_t *m = &disk.medium;
    for (int s = 8; s < 16; s++) {                      // one 4 KB erase sector, all eight 512-byte sectors
        pattern(buf, s);
        CHECK_EQ(MEDIUM_OK, m->write(m, (uint32_t)s, buf));
    }
    CHECK_EQ(0, chip.erases);
    pattern(buf, 99);                                   // sets bits the old data cleared: needs an erase
    CHECK_EQ(MEDIUM_OK, m->write(m, 11, buf));
    CHECK_EQ(1, chip.erases);
    CHECK_EQ(1, disk.stats.erases);
    for (int s = 8; s < 16; s++) {
        pattern(buf, s == 11 ? 99 : s);
        CHECK_EQ(MEDIUM_OK, m->read(m, (uint32_t)s, back));
        CHECK(memcmp(buf, back, 512) == 0);
    }
    CHECK_EQ(0, chip.violations);
    fnor_free(&chip);
}

TEST(after_an_erase_blank_pages_are_left_alone)
{
    fresh(1u << 20);
    medium_t *m = &disk.medium;
    pattern(buf, 5);
    CHECK_EQ(MEDIUM_OK, m->write(m, 0, buf));
    pattern(buf, 6);
    uint32_t programs = chip.programs;
    CHECK_EQ(MEDIUM_OK, m->write(m, 0, buf));           // the rest of the 4 KB sector is blank
    CHECK_EQ(1, chip.erases);
    CHECK_EQ(programs + 2, chip.programs);              // two pages, not sixteen
    fnor_free(&chip);
}

TEST(a_write_the_chip_doesnt_keep_fails)
{
    fresh(1u << 20);
    medium_t *m = &disk.medium;
    chip.program_ignores = true;
    pattern(buf, 3);
    CHECK_EQ(MEDIUM_FAILED, m->write(m, 2, buf));
    CHECK_EQ(1, disk.stats.failed);
    CHECK_EQ(MEDIUM_FAILED, m->write(m, 2048, buf));    // past the end
    fnor_free(&chip);
}

TEST(no_chip_no_drive)
{
    fresh(1u << 20);
    chip.nor.size = 0;                                  // the JEDEC ID didn't answer
    CHECK(!disk.medium.ready(&disk.medium));
    CHECK_EQ(0, disk.medium.sectors(&disk.medium));
    fnor_free(&chip);
}

int main(void)
{
    RUN(mirroring_on_a_16_mb_chip);
    RUN(mirroring_by_a_count_that_isnt_a_power_of_two);
    RUN(no_mirroring_from_256_mb);
    RUN(a_medium_under_1_mb_holds_no_disk);
    RUN(jedec_sizes);
    RUN(a_blank_chip_reads_as_zeros);
    RUN(stored_inverted_and_written_in_place_on_blank_space);
    RUN(a_write_that_changes_nothing_writes_nothing);
    RUN(an_overwrite_erases_and_keeps_its_neighbours);
    RUN(after_an_erase_blank_pages_are_left_alone);
    RUN(a_write_the_chip_doesnt_keep_fails);
    RUN(no_chip_no_drive);
    return TEST_RESULT();
}
