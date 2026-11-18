#include "fw_info.h"

#include <stdio.h>

int fw_banner(char *buf, size_t size, const char *firmware, const char *version,
              const char *source_hash, const char *target)
{
    return snprintf(buf, size, "%s %s (source %.12s), %s\r\nCopyright (c) 2026 A.C. Wright Design\r\n",
                    firmware, version, source_hash, target);
}
