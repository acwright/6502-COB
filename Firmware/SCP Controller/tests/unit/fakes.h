// Models the unit tests run the core against: a virtual clock, a RAM medium
// (the SD card's stand-in) and a NOR flash chip that keeps the chip's rules.
#pragma once

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "ata.h"
#include "drive.h"
#include "flashdisk.h"
#include "media.h"
#include "nor.h"

// A clock the models move on, in microseconds.
typedef struct {
    uint32_t us;
} fake_clock_t;

static inline uint32_t fake_now(void *clock)
{
    return ((fake_clock_t *)clock)->us;
}

// A medium in RAM. `in` and `started` model the SD card's slot; reads and
// writes of a card that isn't in say MEDIUM_GONE.
typedef struct {
    medium_t medium;
    uint32_t count;
    uint8_t *data;
    bool in, started, fail;
    fake_clock_t *clock;
    uint32_t write_us;          // what a sector write costs on the clock
    void (*on_access)(void *);  // called from inside each read and write, to model the bus side acting meanwhile
    void *on_access_ctx;
} ram_medium_t;

static inline bool ram_ready(medium_t *m) { ram_medium_t *r = m->ctx; return r->in && r->started; }
static inline uint32_t ram_sectors(medium_t *m) { return ((ram_medium_t *)m->ctx)->count; }

static inline medium_result_t ram_read(medium_t *m, uint32_t s, uint8_t *buf)
{
    ram_medium_t *r = m->ctx;
    if (r->on_access) r->on_access(r->on_access_ctx);
    if (!r->in) return MEDIUM_GONE;
    if (r->fail || s >= r->count) return MEDIUM_FAILED;
    memcpy(buf, r->data + (size_t)s * 512, 512);
    return MEDIUM_OK;
}

static inline medium_result_t ram_write(medium_t *m, uint32_t s, const uint8_t *buf)
{
    ram_medium_t *r = m->ctx;
    if (r->on_access) r->on_access(r->on_access_ctx);
    if (!r->in) return MEDIUM_GONE;
    if (r->fail || s >= r->count) return MEDIUM_FAILED;
    memcpy(r->data + (size_t)s * 512, buf, 512);
    if (r->clock) r->clock->us += r->write_us;
    return MEDIUM_OK;
}

static inline void ram_init(ram_medium_t *r, uint32_t sectors)
{
    memset(r, 0, sizeof *r);
    r->count = sectors;
    r->data = calloc(sectors ? sectors : 1, 512);
    r->in = r->started = true;
    r->medium = (medium_t){ "ram", 1, ram_ready, ram_sectors, ram_read, ram_write, r };
}

static inline void ram_free(ram_medium_t *r) { free(r->data); }

// A NOR flash chip: programming only clears bits and stays within a page;
// erasing sets a 4 KB sector to $FF. Times are the W25Q128JV's typical ones.
#define NOR_PROGRAM_US 400u
#define NOR_ERASE_US   45000u
typedef struct {
    nor_t nor;
    uint8_t *data;
    uint32_t reads, programs, erases;
    uint32_t violations;        // a program that crossed a page, or tried to set a bit
    bool program_ignores;       // a stuck chip: programs do nothing
    fake_clock_t *clock;
    void (*on_erase)(void *);   // called from inside each erase
    void *on_erase_ctx;
} fake_nor_t;

static inline bool fnor_read(nor_t *n, uint32_t addr, uint8_t *buf, uint32_t len)
{
    fake_nor_t *f = n->ctx;
    if (addr + len > n->size) return false;
    f->reads++;
    memcpy(buf, f->data + addr, len);
    return true;
}

static inline bool fnor_program(nor_t *n, uint32_t addr, const uint8_t *buf, uint32_t len)
{
    fake_nor_t *f = n->ctx;
    if (addr + len > n->size) return false;
    f->programs++;
    if (f->clock) f->clock->us += NOR_PROGRAM_US;
    if ((addr / NOR_PAGE) != ((addr + len - 1) / NOR_PAGE)) f->violations++;
    if (f->program_ignores) return true;
    for (uint32_t i = 0; i < len; i++) {
        if ((f->data[addr + i] & buf[i]) != buf[i]) f->violations++;
        f->data[addr + i] &= buf[i];
    }
    return true;
}

static inline bool fnor_erase(nor_t *n, uint32_t addr)
{
    fake_nor_t *f = n->ctx;
    if (addr % NOR_SECTOR || addr >= n->size) return false;
    f->erases++;
    if (f->on_erase) f->on_erase(f->on_erase_ctx);
    if (f->clock) f->clock->us += NOR_ERASE_US;
    memset(f->data + addr, 0xFF, NOR_SECTOR);
    return true;
}

static inline void fnor_init(fake_nor_t *f, uint32_t size)
{
    memset(f, 0, sizeof *f);
    f->data = malloc(size);
    memset(f->data, 0xFF, size);
    f->nor = (nor_t){ size, fnor_read, fnor_program, fnor_erase, f };
}

static inline void fnor_free(fake_nor_t *f) { free(f->data); }

// The 6502's side: register accesses, with the worker done in between, as the
// two RP2350 cores would between one bus access and the next.
static inline void settle(ata_t *a, drive_t *d)
{
    ata_poll(a);
    while (drive_service(d))
        ata_poll(a);
}
