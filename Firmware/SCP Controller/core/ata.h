// The eight registers the 6502 sees, and the commands written to them: the
// CompactFlash card's task file in 8-bit, LBA, master-only use, as the BIOS
// drives it. This is the bus side of the controller. It never waits: anything
// slow (the media) is handed to the worker side (drive.h) through a one-job
// mailbox, and status reads BSY until the job comes back.
//
// On the RP2350 the bus side runs on core 1 and the worker on core 0. The
// mailbox's state is atomic; everything else belongs to one side at a time:
// the registers always to the bus side, the sector buffer to the worker only
// between ata_job_begin() and ata_job_end().
#pragma once

#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>

// Registers, by A2-A0.
enum {
    ATA_REG_DATA = 0,
    ATA_REG_ERROR = 1,      // read: error; write: feature
    ATA_REG_COUNT = 2,
    ATA_REG_LBA0 = 3,
    ATA_REG_LBA1 = 4,
    ATA_REG_LBA2 = 5,
    ATA_REG_LBA3 = 6,       // bits 0-3 are LBA 24-27; reads back with $E0 set (LBA mode, master)
    ATA_REG_STATUS = 7,     // read: status; write: command
};

// Status bits.
#define ATA_SR_BSY 0x80
#define ATA_SR_RDY 0x40
#define ATA_SR_DSC 0x10
#define ATA_SR_DRQ 0x08
#define ATA_SR_ERR 0x01

// Error bits.
#define ATA_ER_AMNF 0x01    // no medium answered
#define ATA_ER_ABRT 0x04    // command aborted
#define ATA_ER_IDNF 0x10    // no such sector (a medium under 1 MB)
#define ATA_ER_UNC  0x40    // the medium failed to read or write

// Commands.
#define ATA_CMD_READ       0x20
#define ATA_CMD_READ_NR    0x21
#define ATA_CMD_WRITE      0x30
#define ATA_CMD_WRITE_NR   0x31
#define ATA_CMD_ERASE      0xC0     // CFA Erase Sectors: the sectors read back as zeros
#define ATA_CMD_FLUSH      0xE7
#define ATA_CMD_IDENTIFY   0xEC
#define ATA_CMD_SET_FEAT   0xEF

#define ATA_SECTOR 512

// What the worker is asked to do with one sector.
typedef enum {
    ATA_JOB_READ = 1,       // the sector into the buffer
    ATA_JOB_WRITE,          // the buffer onto the sector
    ATA_JOB_ERASE,          // zeros onto the sector
    ATA_JOB_IDENTIFY,       // the IDENTIFY data into the buffer
} ata_op_t;

enum { ATA_JOB_IDLE, ATA_JOB_POSTED, ATA_JOB_TAKEN, ATA_JOB_DONE };

typedef struct {
    atomic_int state;       // ATA_JOB_IDLE ... ATA_JOB_DONE
    uint8_t op;             // ata_op_t
    bool first;             // the command's first sector: choose the medium now
    uint32_t lba;           // as the 6502 wrote it, before mirroring
    uint8_t error;          // the result: 0, or ATA_ER_* bits
} ata_job_t;

typedef enum { ATA_XFER_NONE, ATA_XFER_READ, ATA_XFER_WRITE, ATA_XFER_ERASE, ATA_XFER_IDENTIFY } ata_xfer_t;

typedef struct {
    // The registers.
    uint8_t error, feature, count, lba[4];

    // The controller's state.
    bool starting;          // since power-on, until ata_set_present()
    bool present;           // a medium can answer; with none, status reads $00, an empty socket
    bool resb;              // RESB is held low
    bool resetting;         // RESB released, waiting for a job in progress to finish
    bool waiting;           // a job is posted or in progress
    bool drq, err;
    ata_xfer_t xfer;
    uint32_t lba_start;     // the command's first sector
    uint32_t total;         // sectors the command moves (1-256)
    uint32_t done;          // sectors finished
    uint16_t index;         // the next byte in the buffer

    uint8_t buffer[ATA_SECTOR];
    ata_job_t job;
} ata_t;

// Power-on: every read answers $80 (BSY) until ata_set_present().
void ata_init(ata_t *a);

// The worker has started, and a medium can answer (true) or none can (false:
// status reads $00, so the BIOS's boot probe finds an empty socket).
void ata_set_present(ata_t *a, bool present);

// What a read of a register returns now, with no side effects: while BSY is
// set, every register reads as the status, $80, as on a CF card. The RP2350's
// bus program serves reads from a copy of these values.
uint8_t ata_peek(const ata_t *a, unsigned reg);

// All eight registers as ata_peek() gives them, in one pass: what the RP2350's
// bus program is given after every access, so it must be quick.
void ata_registers(const ata_t *a, uint8_t regs[8]);

// Whether an access to the data register in the middle of a sector changed
// nothing the 6502 can see but the data register itself: no BSY, DRQ still set.
// Then the RP2350 updates just the data register (a read) or nothing (a write).
static inline bool ata_mid_sector(const ata_t *a)
{
    return a->drq && !a->starting && !a->resb && !a->resetting && !a->waiting;
}

// Registers 0 and 1 (data, error) as one word, low byte first: what the RP2350
// rewrites after a data read in the middle of a sector.
static inline uint16_t ata_data_word(const ata_t *a)
{
    uint8_t data = a->xfer == ATA_XFER_READ || a->xfer == ATA_XFER_IDENTIFY ? a->buffer[a->index] : 0x00;
    return (uint16_t)(data | (a->error << 8));
}

// A read of a register by the 6502: ata_peek()'s value, and its side effects
// (the data register moves on to the next byte).
uint8_t ata_read(ata_t *a, unsigned reg);

// A write of a register by the 6502. Ignored while BSY.
void ata_write(ata_t *a, unsigned reg, uint8_t value);


// RESB's level: true while it is held low. A reset aborts the command and keeps
// BSY until any job in progress is finished, then puts the registers back.
void ata_resb(ata_t *a, bool low);

// Bus side: pick up a finished job. Call it between bus accesses.
void ata_poll(ata_t *a);

// The status register as ata_peek() gives it.
static inline bool ata_busy(const ata_t *a)
{
    return a->starting || a->resb || a->resetting || a->waiting;
}

// Whether this write may leave the controller busy: a command, or the last byte
// of a sector being written. The RP2350 shows BSY the moment it takes such a
// write, before it does the rest, so a status read right behind it (lda after
// sta, four cycles) can't see the old status.
static inline bool ata_write_may_busy(const ata_t *a, unsigned reg)
{
    if (ata_busy(a))
        return false;                   // ignored anyway
    if ((reg & 7) == ATA_REG_STATUS)
        return a->present;
    return (reg & 7) == ATA_REG_DATA && a->drq && a->xfer == ATA_XFER_WRITE && a->index == ATA_SECTOR - 1;
}

// Worker side: the posted job, now taken, or NULL if there is none. The worker
// may use a->buffer until it calls ata_job_end().
ata_job_t *ata_job_begin(ata_t *a);
void ata_job_end(ata_t *a, uint8_t error);
