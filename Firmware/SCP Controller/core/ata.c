#include "ata.h"

#include <string.h>

static void registers_reset(ata_t *a)
{
    a->error = 0;
    a->feature = 0;
    a->count = 0;
    a->lba[0] = a->lba[1] = a->lba[2] = 0;
    a->lba[3] = 0xE0;
    a->drq = a->err = false;
    a->xfer = ATA_XFER_NONE;
    a->index = 0;
}

void ata_init(ata_t *a)
{
    memset(a, 0, sizeof *a);
    atomic_init(&a->job.state, ATA_JOB_IDLE);
    registers_reset(a);
    a->starting = true;
}

void ata_set_present(ata_t *a, bool present)
{
    a->starting = false;
    a->present = present;
}

static uint32_t lba28(const ata_t *a)
{
    return ((uint32_t)(a->lba[3] & 0x0F) << 24) | ((uint32_t)a->lba[2] << 16) | ((uint32_t)a->lba[1] << 8) | a->lba[0];
}

static void post(ata_t *a, ata_op_t op, uint32_t lba, bool first)
{
    a->job.op = (uint8_t)op;
    a->job.lba = lba & 0x0FFFFFFF;
    a->job.first = first;
    a->job.error = 0;
    a->waiting = true;
    atomic_store_explicit(&a->job.state, ATA_JOB_POSTED, memory_order_release);
}

static void fail(ata_t *a, uint8_t error)
{
    a->error = error;
    a->err = true;
    a->drq = false;
    a->xfer = ATA_XFER_NONE;
}

static void finish(ata_t *a)
{
    a->drq = false;
    a->xfer = ATA_XFER_NONE;
}

uint8_t ata_peek(const ata_t *a, unsigned reg)
{
    switch (reg & 7) {
    case ATA_REG_DATA:
        return a->drq && (a->xfer == ATA_XFER_READ || a->xfer == ATA_XFER_IDENTIFY) ? a->buffer[a->index] : 0x00;
    case ATA_REG_ERROR: return a->error;
    case ATA_REG_COUNT: return a->count;
    case ATA_REG_LBA0: return a->lba[0];
    case ATA_REG_LBA1: return a->lba[1];
    case ATA_REG_LBA2: return a->lba[2];
    case ATA_REG_LBA3: return a->lba[3];
    default:
        if (ata_busy(a))
            return ATA_SR_BSY;
        if (!a->present)
            return 0x00;
        return (uint8_t)(ATA_SR_RDY | ATA_SR_DSC | (a->drq ? ATA_SR_DRQ : 0) | (a->err ? ATA_SR_ERR : 0));
    }
}

uint8_t ata_read(ata_t *a, unsigned reg)
{
    uint8_t value = ata_peek(a, reg);
    if ((reg & 7) != ATA_REG_DATA || !a->drq || (a->xfer != ATA_XFER_READ && a->xfer != ATA_XFER_IDENTIFY))
        return value;
    if (++a->index < ATA_SECTOR)
        return value;
    a->index = 0;
    a->drq = false;
    a->done++;
    if (a->xfer == ATA_XFER_READ && a->done < a->total)
        post(a, ATA_JOB_READ, a->lba_start + a->done, false);
    else
        finish(a);
    return value;
}

static void command(ata_t *a, uint8_t cmd)
{
    if (!a->present)
        return;
    if (a->xfer != ATA_XFER_NONE) {         // a command in the middle of another one's transfer
        fail(a, ATA_ER_ABRT);
        return;
    }
    a->error = 0;
    a->err = false;
    a->drq = false;
    a->index = 0;
    a->done = 0;
    a->total = a->count ? a->count : 256;
    a->lba_start = lba28(a);

    switch (cmd) {
    case ATA_CMD_READ:
    case ATA_CMD_READ_NR:
        a->xfer = ATA_XFER_READ;
        post(a, ATA_JOB_READ, a->lba_start, true);
        break;
    case ATA_CMD_WRITE:
    case ATA_CMD_WRITE_NR:
        a->xfer = ATA_XFER_WRITE;
        a->drq = true;
        break;
    case ATA_CMD_ERASE:
        a->xfer = ATA_XFER_ERASE;
        post(a, ATA_JOB_ERASE, a->lba_start, true);
        break;
    case ATA_CMD_IDENTIFY:
        a->xfer = ATA_XFER_IDENTIFY;
        a->total = 1;
        post(a, ATA_JOB_IDENTIFY, 0, true);
        break;
    case ATA_CMD_SET_FEAT:      // every feature accepted: the controller is 8-bit only, and caches nothing
    case ATA_CMD_FLUSH:         // every write is on the medium before BSY clears
        break;
    default:
        fail(a, ATA_ER_ABRT);
        break;
    }
}

void ata_write(ata_t *a, unsigned reg, uint8_t value)
{
    if (ata_busy(a))
        return;
    switch (reg & 7) {
    case ATA_REG_DATA:
        if (!a->drq || a->xfer != ATA_XFER_WRITE)
            return;
        a->buffer[a->index] = value;
        if (++a->index < ATA_SECTOR)
            return;
        a->index = 0;
        a->drq = false;
        post(a, ATA_JOB_WRITE, a->lba_start + a->done, a->done == 0);
        return;
    case ATA_REG_ERROR: a->feature = value; return;
    case ATA_REG_COUNT: a->count = value; return;
    case ATA_REG_LBA0: a->lba[0] = value; return;
    case ATA_REG_LBA1: a->lba[1] = value; return;
    case ATA_REG_LBA2: a->lba[2] = value; return;
    case ATA_REG_LBA3: a->lba[3] = (uint8_t)((value & 0x0F) | 0xE0); return;
    default: command(a, value); return;
    }
}

static void completed(ata_t *a, uint8_t error)
{
    if (error) {
        fail(a, error);
        return;
    }
    switch (a->xfer) {
    case ATA_XFER_READ:
    case ATA_XFER_IDENTIFY:
        a->drq = true;
        a->index = 0;
        break;
    case ATA_XFER_WRITE:
        if (++a->done < a->total) {
            a->drq = true;
            a->index = 0;
        } else {
            finish(a);
        }
        break;
    case ATA_XFER_ERASE:
        if (++a->done < a->total)
            post(a, ATA_JOB_ERASE, a->lba_start + a->done, false);
        else
            finish(a);
        break;
    default:
        break;
    }
}

void ata_poll(ata_t *a)
{
    if (a->waiting && atomic_load_explicit(&a->job.state, memory_order_acquire) == ATA_JOB_DONE) {
        uint8_t error = a->job.error;
        a->waiting = false;
        atomic_store_explicit(&a->job.state, ATA_JOB_IDLE, memory_order_relaxed);
        // After a reset the transfer is gone, so a result that comes back now
        // can only set the error register, which is reset with the rest once
        // RESB is released, below.
        completed(a, error);
    }
    if (a->resetting && !a->waiting) {
        registers_reset(a);
        a->resetting = false;
    }
}

void ata_resb(ata_t *a, bool low)
{
    if (low) {
        if (a->resb)
            return;
        a->resb = true;
        a->xfer = ATA_XFER_NONE;
        a->drq = false;
        if (a->waiting) {
            int posted = ATA_JOB_POSTED;
            if (atomic_compare_exchange_strong(&a->job.state, &posted, ATA_JOB_IDLE))
                a->waiting = false;     // the worker hadn't started it; if it had, BSY stays until it's done
        }
    } else if (a->resb) {
        a->resb = false;
        a->resetting = true;
        ata_poll(a);
    }
}

ata_job_t *ata_job_begin(ata_t *a)
{
    int posted = ATA_JOB_POSTED;
    if (!atomic_compare_exchange_strong(&a->job.state, &posted, ATA_JOB_TAKEN))
        return NULL;
    return &a->job;
}

void ata_job_end(ata_t *a, uint8_t error)
{
    a->job.error = error;
    atomic_store_explicit(&a->job.state, ATA_JOB_DONE, memory_order_release);
}
