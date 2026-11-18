#include "media.h"

uint32_t media_disks(uint32_t sectors)
{
    return sectors / MEDIA_DISK_SECTORS;
}

bool media_map(uint32_t sectors, uint32_t lba, uint32_t *sector)
{
    uint32_t span = media_disks(sectors) * MEDIA_DISK_SECTORS;
    if (span == 0)
        return false;
    *sector = lba % span;
    return true;
}
