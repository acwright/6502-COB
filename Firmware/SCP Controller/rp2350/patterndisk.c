#include "patterndisk.h"

#include <string.h>

#include "pico/time.h"

static bool pd_ready(medium_t *m)
{
    (void)m;
    return true;
}

static uint32_t pd_sectors(medium_t *m)
{
    return ((patterndisk_t *)m)->sectors;
}

static medium_result_t pd_read(medium_t *m, uint32_t sector, uint8_t *buf)
{
    patterndisk_t *d = (patterndisk_t *)m;
    busy_wait_us(d->read_us);
    for (unsigned s = 0; s < PATTERNDISK_SLOTS; s++) {
        if (d->slot[s].used && d->slot[s].sector == sector) {
            memcpy(buf, d->slot[s].data, 512);
            return MEDIUM_OK;
        }
    }
    for (unsigned i = 0; i < 512; i++)
        buf[i] = patterndisk_byte(sector, i);
    return MEDIUM_OK;
}

static medium_result_t pd_write(medium_t *m, uint32_t sector, const uint8_t *buf)
{
    patterndisk_t *d = (patterndisk_t *)m;
    busy_wait_us(d->write_us);
    unsigned s;
    for (s = 0; s < PATTERNDISK_SLOTS; s++)
        if (d->slot[s].used && d->slot[s].sector == sector)
            break;
    if (s == PATTERNDISK_SLOTS) {
        s = d->next;
        d->next = (d->next + 1) % PATTERNDISK_SLOTS;
    }
    d->slot[s].used = 1;
    d->slot[s].sector = sector;
    memcpy(d->slot[s].data, buf, 512);
    return MEDIUM_OK;
}

void patterndisk_init(patterndisk_t *d, uint32_t sectors)
{
    memset(d, 0, sizeof *d);
    d->sectors = sectors;
    d->medium = (medium_t){ "pattern", 1, pd_ready, pd_sectors, pd_read, pd_write, d };
}
