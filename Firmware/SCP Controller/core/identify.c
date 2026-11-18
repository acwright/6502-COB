#include "identify.h"

#include <string.h>

static void word(uint8_t *buf, unsigned w, uint16_t v)
{
    buf[2 * w] = (uint8_t)v;
    buf[2 * w + 1] = (uint8_t)(v >> 8);
}

static void dword(uint8_t *buf, unsigned w, uint32_t v)       // low word first
{
    word(buf, w, (uint16_t)v);
    word(buf, w + 1, (uint16_t)(v >> 16));
}

// A string over `words` words, space padded, two characters a word with the
// first in the high byte.
static void text(uint8_t *buf, unsigned w, unsigned words, const char *s)
{
    size_t len = s ? strlen(s) : 0;
    for (unsigned i = 0; i < words * 2; i++) {
        char c = i < len ? s[i] : ' ';
        buf[2 * w + (i ^ 1)] = (uint8_t)c;
    }
}

void identify_build(uint8_t buf[512], const identify_t *id)
{
    memset(buf, 0, 512);
    const uint16_t heads = 16, spt = 63;
    uint32_t cylinders = id->sectors / (heads * spt);
    if (cylinders > 16383)
        cylinders = 16383;
    uint32_t chs = cylinders * heads * spt;

    word(buf, 0, 0x848A);
    word(buf, 1, (uint16_t)cylinders);
    word(buf, 3, heads);
    word(buf, 6, spt);
    word(buf, 7, (uint16_t)(id->sectors >> 16));
    word(buf, 8, (uint16_t)id->sectors);
    text(buf, 10, 10, id->serial);
    text(buf, 23, 4, id->firmware);
    text(buf, 27, 20, id->model);
    word(buf, 47, 0x8001);
    word(buf, 49, 0x0200);
    word(buf, 51, 0x0200);
    word(buf, 53, 0x0001);
    word(buf, 54, (uint16_t)cylinders);
    word(buf, 55, heads);
    word(buf, 56, spt);
    dword(buf, 57, chs);
    dword(buf, 60, id->sectors);

    dword(buf, 128, id->longest_busy_us);
    dword(buf, 130, id->longest_sd_write_us);
    dword(buf, 132, id->longest_flash_write_us);
    word(buf, 134, id->medium);
    word(buf, 135, id->disks);
    dword(buf, 136, id->errors);
}
