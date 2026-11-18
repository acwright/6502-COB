// The registers and commands, with the worker played by hand.
#include "ata.h"

#include "test.h"

static ata_t a;

// Every write that leaves the controller busy must have been foretold by
// ata_write_may_busy(), or the RP2350 would show the old status for a moment.
static int busy_not_foretold;
static int fast_path_wrong;      // the RP2350's fast path disagreed with the full registers
static void checked_write(ata_t *x, unsigned reg, uint8_t value)
{
    bool foretold = ata_write_may_busy(x, reg);
    bool was = ata_busy(x);
    uint8_t before[8], after[8];
    ata_registers(x, before);
    ata_write(x, reg, value);
    busy_not_foretold += !was && ata_busy(x) && !foretold;
    // The fast path: a data write mid-sector changes nothing the 6502 can read.
    if ((reg & 7) == ATA_REG_DATA && ata_mid_sector(x)) {
        ata_registers(x, after);
        fast_path_wrong += memcmp(before, after, 8) != 0;
    }
}
#define ata_write checked_write

// ata_registers() must agree with ata_peek() everywhere: checked at every read.
static int registers_disagree;
static uint8_t checked_read(ata_t *x, unsigned reg)
{
    uint8_t all[8], before[8];
    ata_registers(x, all);
    for (unsigned r = 0; r < 8; r++)
        registers_disagree += all[r] != ata_peek(x, r);
    memcpy(before, all, 8);
    uint8_t v = ata_read(x, reg);
    // The RP2350's fast path: mid-sector, only the data word may have changed.
    if ((reg & 7) == ATA_REG_DATA && ata_mid_sector(x)) {
        ata_registers(x, all);
        fast_path_wrong += ata_data_word(x) != (all[0] | (all[1] << 8));
        for (unsigned r = 1; r < 8; r++)
            fast_path_wrong += all[r] != before[r];
    }
    return v;
}
#define ata_read checked_read

static void ready(void)
{
    ata_init(&a);
    ata_set_present(&a, true);
}

// The worker: take the posted job, fill the buffer with a pattern from its LBA, end it.
static ata_job_t *take(void)
{
    return ata_job_begin(&a);
}

static void end(uint8_t error)
{
    ata_job_end(&a, error);
    ata_poll(&a);
}

static void fill(uint32_t lba)
{
    for (int i = 0; i < 512; i++)
        a.buffer[i] = (uint8_t)(i + lba);
}

static void set_lba(uint32_t lba, uint8_t count)
{
    ata_write(&a, ATA_REG_COUNT, count);
    ata_write(&a, ATA_REG_LBA0, (uint8_t)lba);
    ata_write(&a, ATA_REG_LBA1, (uint8_t)(lba >> 8));
    ata_write(&a, ATA_REG_LBA2, (uint8_t)(lba >> 16));
    ata_write(&a, ATA_REG_LBA3, (uint8_t)(0xE0 | (lba >> 24)));
}

TEST(power_on_answers_busy_then_ready_or_empty)
{
    ata_init(&a);
    CHECK_EQ(0x80, ata_read(&a, ATA_REG_STATUS));
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_SET_FEAT);    // ignored while BSY
    CHECK(take() == NULL);
    ata_set_present(&a, true);
    CHECK_EQ(0x50, ata_read(&a, ATA_REG_STATUS));
    ata_set_present(&a, false);
    CHECK_EQ(0x00, ata_read(&a, ATA_REG_STATUS));       // an empty socket: the BIOS's probe gives up
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_READ);
    CHECK(take() == NULL);
}

TEST(registers_read_back)
{
    ready();
    CHECK_EQ(0xE0, ata_read(&a, ATA_REG_LBA3));
    set_lba(0x0ABCDEF, 7);
    CHECK_EQ(7, ata_read(&a, ATA_REG_COUNT));
    CHECK_EQ(0xEF, ata_read(&a, ATA_REG_LBA0));
    CHECK_EQ(0xCD, ata_read(&a, ATA_REG_LBA1));
    CHECK_EQ(0xAB, ata_read(&a, ATA_REG_LBA2));
    CHECK_EQ(0xE0, ata_read(&a, ATA_REG_LBA3));
    ata_write(&a, ATA_REG_LBA3, 0x05);                  // LBA mode and master, whatever is written
    CHECK_EQ(0xE5, ata_read(&a, ATA_REG_LBA3));
    ata_write(&a, ATA_REG_ERROR, 0x01);                 // the feature register, not the error register
    CHECK_EQ(0x00, ata_read(&a, ATA_REG_ERROR));
    CHECK_EQ(0x00, ata_read(&a, ATA_REG_DATA));         // no transfer: data reads $00
}

TEST(every_register_reads_as_status_while_busy)
{
    ready();
    set_lba(0x0123456, 1);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_READ);
    for (unsigned r = 0; r < 8; r++)
        CHECK_EQ(0x80, ata_read(&a, r));
    take();
    for (unsigned r = 0; r < 8; r++)
        CHECK_EQ(0x80, ata_read(&a, r));
    end(0);
    CHECK_EQ(0x56, ata_read(&a, ATA_REG_LBA0));         // and the registers again once BSY clears
    CHECK_EQ(0xE0, ata_read(&a, ATA_REG_LBA3));
    CHECK_EQ(0x58, ata_read(&a, ATA_REG_STATUS));
}

TEST(set_features_and_unknown_commands)
{
    ready();
    ata_write(&a, ATA_REG_ERROR, 0x01);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_SET_FEAT);
    CHECK_EQ(0x50, ata_read(&a, ATA_REG_STATUS));
    CHECK(take() == NULL);
    ata_write(&a, ATA_REG_STATUS, 0x91);
    CHECK_EQ(0x51, ata_read(&a, ATA_REG_STATUS));
    CHECK_EQ(ATA_ER_ABRT, ata_read(&a, ATA_REG_ERROR));
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_FLUSH);       // a good command clears the error
    CHECK_EQ(0x50, ata_read(&a, ATA_REG_STATUS));
    CHECK_EQ(0x00, ata_read(&a, ATA_REG_ERROR));
}

TEST(read_one_sector)
{
    ready();
    set_lba(0x123456, 1);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_READ);
    CHECK_EQ(0x80, ata_read(&a, ATA_REG_STATUS));       // BSY at once, before the next status read
    ata_job_t *j = take();
    CHECK(j != NULL);
    if (!j) return;
    CHECK_EQ(ATA_JOB_READ, j->op);
    CHECK_EQ(0x123456, j->lba);
    CHECK(j->first);
    CHECK_EQ(0x80, ata_read(&a, ATA_REG_STATUS));
    fill(j->lba);
    end(0);
    CHECK_EQ(0x58, ata_read(&a, ATA_REG_STATUS));
    CHECK_EQ(0x56, ata_peek(&a, ATA_REG_DATA));          // peek doesn't move on
    CHECK_EQ(0x56, ata_peek(&a, ATA_REG_DATA));
    int wrong = 0;
    for (int i = 0; i < 512; i++)
        wrong += ata_read(&a, ATA_REG_DATA) != (uint8_t)(i + 0x56);
    CHECK_EQ(0, wrong);
    CHECK_EQ(0x50, ata_read(&a, ATA_REG_STATUS));       // DRQ clear after the 512th byte
    CHECK_EQ(0x00, ata_read(&a, ATA_REG_DATA));
    CHECK(take() == NULL);
}

TEST(read_several_sectors_and_a_count_of_zero)
{
    ready();
    set_lba(100, 3);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_READ_NR);
    for (uint32_t s = 0; s < 3; s++) {
        ata_job_t *j = take();
        CHECK(j != NULL);
        if (!j) return;
        CHECK_EQ(100 + s, j->lba);
        CHECK_EQ(s == 0, j->first);
        fill(j->lba);
        end(0);
        CHECK_EQ(0x58, ata_read(&a, ATA_REG_STATUS));
        for (int i = 0; i < 512; i++)
            ata_read(&a, ATA_REG_DATA);
    }
    CHECK_EQ(0x50, ata_read(&a, ATA_REG_STATUS));
    CHECK(take() == NULL);

    set_lba(0, 0);                                      // 0 means 256
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_READ);
    int jobs = 0;
    for (ata_job_t *j; (j = take()) != NULL; jobs++) {
        end(0);
        for (int i = 0; i < 512; i++)
            ata_read(&a, ATA_REG_DATA);
    }
    CHECK_EQ(256, jobs);
    CHECK_EQ(0x50, ata_read(&a, ATA_REG_STATUS));
}

TEST(write_sectors)
{
    ready();
    set_lba(7, 2);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_WRITE);
    CHECK_EQ(0x58, ata_read(&a, ATA_REG_STATUS));       // DRQ at once: nothing to fetch
    CHECK(take() == NULL);
    for (int s = 0; s < 2; s++) {
        for (int i = 0; i < 511; i++)
            ata_write(&a, ATA_REG_DATA, (uint8_t)(i ^ s));
        CHECK(take() == NULL);
        ata_write(&a, ATA_REG_DATA, 0xEE);
        CHECK_EQ(0x80, ata_read(&a, ATA_REG_STATUS));
        ata_job_t *j = take();
        CHECK(j != NULL);
        if (!j) return;
        CHECK_EQ(ATA_JOB_WRITE, j->op);
        CHECK_EQ(7 + s, j->lba);
        CHECK_EQ(s == 0, j->first);
        CHECK_EQ(0 ^ s, a.buffer[0]);
        CHECK_EQ(0xEE, a.buffer[511]);
        end(0);
        CHECK_EQ(s == 0 ? 0x58 : 0x50, ata_read(&a, ATA_REG_STATUS));
    }
    ata_write(&a, ATA_REG_DATA, 0x12);                  // no transfer: ignored
    CHECK(take() == NULL);
}

TEST(writes_ignored_while_busy)
{
    ready();
    set_lba(1, 1);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_READ);
    ata_write(&a, ATA_REG_LBA0, 0x99);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_WRITE);
    ata_job_t *j = take();
    CHECK(j && j->op == ATA_JOB_READ);
    end(0);
    CHECK_EQ(0x58, ata_read(&a, ATA_REG_STATUS));
    CHECK_EQ(1, ata_read(&a, ATA_REG_LBA0));
}

TEST(a_failed_job_ends_the_command)
{
    ready();
    set_lba(1, 2);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_READ);
    take();
    end(ATA_ER_UNC);
    CHECK_EQ(0x51, ata_read(&a, ATA_REG_STATUS));
    CHECK_EQ(ATA_ER_UNC, ata_read(&a, ATA_REG_ERROR));
    CHECK_EQ(0x00, ata_read(&a, ATA_REG_DATA));
    CHECK(take() == NULL);
}

TEST(a_command_mid_transfer_aborts)
{
    ready();
    set_lba(1, 1);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_WRITE);
    ata_write(&a, ATA_REG_DATA, 1);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_READ);
    CHECK_EQ(0x51, ata_read(&a, ATA_REG_STATUS));
    CHECK_EQ(ATA_ER_ABRT, ata_read(&a, ATA_REG_ERROR));
    CHECK(take() == NULL);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_READ);        // and the next command runs
    CHECK(take() != NULL);
}

TEST(erase_sectors)
{
    ready();
    set_lba(40, 2);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_ERASE);
    for (uint32_t s = 0; s < 2; s++) {
        CHECK_EQ(0x80, ata_read(&a, ATA_REG_STATUS));
        ata_job_t *j = take();
        CHECK(j && j->op == ATA_JOB_ERASE && j->lba == 40 + s);
        end(0);
    }
    CHECK_EQ(0x50, ata_read(&a, ATA_REG_STATUS));
}

TEST(identify_is_one_sector)
{
    ready();
    set_lba(9, 5);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_IDENTIFY);
    ata_job_t *j = take();
    CHECK(j && j->op == ATA_JOB_IDENTIFY && j->first);
    fill(0);
    end(0);
    for (int i = 0; i < 512; i++)
        ata_read(&a, ATA_REG_DATA);
    CHECK_EQ(0x50, ata_read(&a, ATA_REG_STATUS));
    CHECK(take() == NULL);
}

TEST(reset_before_the_worker_starts)
{
    ready();
    set_lba(3, 1);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_READ);
    ata_resb(&a, true);
    CHECK_EQ(0x80, ata_read(&a, ATA_REG_STATUS));
    CHECK(take() == NULL);                              // the posted job was withdrawn
    ata_resb(&a, false);
    CHECK_EQ(0x50, ata_read(&a, ATA_REG_STATUS));
    CHECK_EQ(0, ata_read(&a, ATA_REG_LBA0));
    CHECK_EQ(0, ata_read(&a, ATA_REG_COUNT));
    CHECK_EQ(0xE0, ata_read(&a, ATA_REG_LBA3));
}

TEST(reset_while_the_worker_is_busy)
{
    ready();
    set_lba(3, 1);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_WRITE);
    for (int i = 0; i < 512; i++)
        ata_write(&a, ATA_REG_DATA, 0x55);
    ata_job_t *j = take();                              // the worker is writing the sector
    CHECK(j != NULL);
    ata_resb(&a, true);
    ata_resb(&a, false);
    ata_poll(&a);
    CHECK_EQ(0x80, ata_read(&a, ATA_REG_STATUS));       // BSY until the write is done
    ata_write(&a, ATA_REG_LBA0, 9);                     // and writes still ignored
    end(0);
    CHECK_EQ(0x50, ata_read(&a, ATA_REG_STATUS));       // result forgotten, registers reset
    CHECK_EQ(0, ata_read(&a, ATA_REG_LBA0));
    CHECK_EQ(0, ata_read(&a, ATA_REG_ERROR));
}

TEST(a_failed_job_after_a_reset_leaves_no_error)
{
    ready();
    set_lba(3, 1);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_READ);
    take();
    ata_resb(&a, true);
    end(ATA_ER_UNC);                                    // fails while RESB is still low
    CHECK_EQ(0x80, ata_read(&a, ATA_REG_STATUS));
    ata_resb(&a, false);
    CHECK_EQ(0x50, ata_read(&a, ATA_REG_STATUS));
    CHECK_EQ(0, ata_read(&a, ATA_REG_ERROR));

    set_lba(3, 1);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_READ);
    take();
    ata_resb(&a, true);
    ata_resb(&a, false);
    end(ATA_ER_UNC);                                    // fails after RESB is released
    CHECK_EQ(0x50, ata_read(&a, ATA_REG_STATUS));
    CHECK_EQ(0, ata_read(&a, ATA_REG_ERROR));
    CHECK_EQ(0x00, ata_read(&a, ATA_REG_DATA));
}

TEST(reset_held_low)
{
    ready();
    ata_resb(&a, true);
    ata_write(&a, ATA_REG_STATUS, ATA_CMD_READ);
    CHECK(take() == NULL);
    CHECK_EQ(0x80, ata_read(&a, ATA_REG_STATUS));
    ata_resb(&a, true);                                 // still low: no change
    CHECK_EQ(0x80, ata_read(&a, ATA_REG_STATUS));
    ata_resb(&a, false);
    CHECK_EQ(0x50, ata_read(&a, ATA_REG_STATUS));
}

int main(void)
{
    RUN(power_on_answers_busy_then_ready_or_empty);
    RUN(registers_read_back);
    RUN(every_register_reads_as_status_while_busy);
    RUN(set_features_and_unknown_commands);
    RUN(read_one_sector);
    RUN(read_several_sectors_and_a_count_of_zero);
    RUN(write_sectors);
    RUN(writes_ignored_while_busy);
    RUN(a_failed_job_ends_the_command);
    RUN(a_command_mid_transfer_aborts);
    RUN(erase_sectors);
    RUN(identify_is_one_sector);
    RUN(reset_before_the_worker_starts);
    RUN(reset_while_the_worker_is_busy);
    RUN(a_failed_job_after_a_reset_leaves_no_error);
    RUN(reset_held_low);
    CHECK_EQ(0, registers_disagree);
    CHECK_EQ(0, busy_not_foretold);
    CHECK_EQ(0, fast_path_wrong);
    return TEST_RESULT();
}
