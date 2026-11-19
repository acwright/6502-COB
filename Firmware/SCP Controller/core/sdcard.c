#include "sdcard.h"

// Bits hi..lo of the 128-bit register, bit 127 being the top bit of byte 0.
static uint32_t bits(const uint8_t r[16], unsigned hi, unsigned lo)
{
    uint32_t v = 0;
    for (unsigned i = hi + 1; i-- > lo;)
        v = (v << 1) | ((r[15 - i / 8] >> (i % 8)) & 1u);
    return v;
}

unsigned sd_csd_version(const uint8_t csd[16])
{
    unsigned s = bits(csd, 127, 126);
    return s < 3 ? s + 1 : 0;
}

uint32_t sd_csd_sectors(const uint8_t csd[16])
{
    uint64_t sectors;
    switch (sd_csd_version(csd)) {
    case 1: {
        uint32_t c_size = bits(csd, 73, 62);
        uint32_t mult = bits(csd, 49, 47);
        uint32_t bl_len = bits(csd, 83, 80);
        if (bl_len < 9 || bl_len > 11)          // 512, 1024 or 2048 bytes
            return 0;
        uint64_t bytes = (uint64_t)(c_size + 1) << (mult + 2 + bl_len);
        sectors = bytes >> 9;
        break;
    }
    case 2:
        sectors = (uint64_t)(bits(csd, 69, 48) + 1) * 1024u;
        break;
    default:
        return 0;
    }
    return sectors > 0xFFFFFFFFu ? 0xFFFFFFFFu : (uint32_t)sectors;
}

uint8_t sd_crc7(const uint8_t *p, size_t len)
{
    uint8_t crc = 0;
    for (size_t i = 0; i < len; i++) {
        uint8_t d = p[i];
        for (int b = 0; b < 8; b++) {
            crc <<= 1;
            if ((d ^ crc) & 0x80)
                crc ^= 0x09;
            d <<= 1;
        }
    }
    return crc & 0x7F;
}

uint16_t sd_crc16(const uint8_t *p, size_t len)
{
    uint16_t crc = 0;
    for (size_t i = 0; i < len; i++) {
        crc = (uint16_t)((uint8_t)(crc >> 8) | (crc << 8));
        crc ^= p[i];
        crc ^= (uint8_t)(crc & 0xFF) >> 4;
        crc ^= (uint16_t)(crc << 12);
        crc ^= (uint16_t)((crc & 0xFF) << 5);
    }
    return crc;
}
