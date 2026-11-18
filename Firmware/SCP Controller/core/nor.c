#include "nor.h"

uint32_t nor_size_from_jedec(const uint8_t id[3])
{
    if (id[0] != 0xEF)                      // Winbond
        return 0;
    if (id[1] != 0x40 && id[1] != 0x70)     // W25Q...JV: -IQ/-JQ and -IM/-JM
        return 0;
    if (id[2] >= 0x14 && id[2] <= 0x19)     // W25Q80 (1 MB) to W25Q256 (32 MB): 2 to the power of the byte
        return 1u << id[2];
    if (id[2] == 0x20)                      // W25Q512 (64 MB)
        return 1u << 26;
    if (id[2] == 0x21)                      // W25Q01 (128 MB)
        return 1u << 27;
    return 0;
}

bool nor_needs_4byte(uint32_t size)
{
    return size > (16u << 20);
}
