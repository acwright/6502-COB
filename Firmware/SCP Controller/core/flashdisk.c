#include "flashdisk.h"

#include <string.h>

#include "ata.h"

static bool fd_ready(medium_t *m)
{
    flashdisk_t *f = (flashdisk_t *)m;
    return f->nor && f->nor->size >= NOR_SECTOR;
}

static uint32_t fd_sectors(medium_t *m)
{
    flashdisk_t *f = (flashdisk_t *)m;
    return fd_ready(m) ? f->nor->size / ATA_SECTOR : 0;
}

static medium_result_t fd_read(medium_t *m, uint32_t sector, uint8_t *buf)
{
    flashdisk_t *f = (flashdisk_t *)m;
    if (sector >= fd_sectors(m) || !f->nor->read(f->nor, sector * ATA_SECTOR, buf, ATA_SECTOR)) {
        f->stats.failed++;
        return MEDIUM_FAILED;
    }
    for (unsigned i = 0; i < ATA_SECTOR; i++)
        buf[i] = (uint8_t)~buf[i];
    return MEDIUM_OK;
}

static bool blank(const uint8_t *p, uint32_t len)
{
    for (uint32_t i = 0; i < len; i++)
        if (p[i] != 0xFF)
            return false;
    return true;
}

// Programs len bytes of raw (already inverted) data at addr, page by page,
// leaving out pages that are all $FF, which programming wouldn't change.
static bool program(nor_t *n, uint32_t addr, const uint8_t *raw, uint32_t len)
{
    for (uint32_t p = 0; p < len; p += NOR_PAGE)
        if (!blank(raw + p, NOR_PAGE) && !n->program(n, addr + p, raw + p, NOR_PAGE))
            return false;
    return true;
}

static medium_result_t fd_write(medium_t *m, uint32_t sector, const uint8_t *buf)
{
    flashdisk_t *f = (flashdisk_t *)m;
    nor_t *n = f->nor;
    if (sector >= fd_sectors(m))
        goto failed;
    f->stats.writes++;

    uint32_t addr = sector * ATA_SECTOR;
    uint32_t base = addr & ~(NOR_SECTOR - 1);
    uint32_t off = addr - base;
    uint8_t raw[ATA_SECTOR];
    for (unsigned i = 0; i < ATA_SECTOR; i++)
        raw[i] = (uint8_t)~buf[i];

    if (!n->read(n, base, f->scratch, NOR_SECTOR))
        goto failed;
    uint8_t *old = f->scratch + off;
    if (memcmp(old, raw, ATA_SECTOR) == 0) {
        f->stats.unchanged++;
        return MEDIUM_OK;
    }

    bool in_place = true;
    for (unsigned i = 0; i < ATA_SECTOR && in_place; i++)
        in_place = (old[i] & raw[i]) == raw[i];

    if (in_place) {
        f->stats.in_place++;
        // Only the pages that change: programming a byte with its own value is
        // harmless, but costs a page program.
        for (uint32_t p = 0; p < ATA_SECTOR; p += NOR_PAGE)
            if (memcmp(old + p, raw + p, NOR_PAGE) != 0 && !n->program(n, addr + p, raw + p, NOR_PAGE))
                goto failed;
    } else {
        f->stats.erases++;
        memcpy(old, raw, ATA_SECTOR);
        if (!n->erase(n, base) || !program(n, base, f->scratch, NOR_SECTOR))
            goto failed;
    }

    if (!n->read(n, addr, f->scratch, ATA_SECTOR) || memcmp(f->scratch, raw, ATA_SECTOR) != 0)
        goto failed;
    return MEDIUM_OK;

failed:
    f->stats.failed++;
    return MEDIUM_FAILED;
}

void flashdisk_init(flashdisk_t *f, nor_t *nor)
{
    memset(f, 0, sizeof *f);
    f->nor = nor;
    f->medium.name = "flash";
    f->medium.generation = 1;
    f->medium.ready = fd_ready;
    f->medium.sectors = fd_sectors;
    f->medium.read = fd_read;
    f->medium.write = fd_write;
    f->medium.ctx = f;
}
