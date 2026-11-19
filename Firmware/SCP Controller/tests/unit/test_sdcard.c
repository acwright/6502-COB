// The SD card's arithmetic: its size from the CSD, and the bus's CRC7 and CRC16.
#include "sdcard.h"

#include "test.h"

// Sets bits hi..lo of a 128-bit register, bit 127 the top bit of byte 0.
static void set_bits(uint8_t r[16], unsigned hi, unsigned lo, uint32_t v)
{
    for (unsigned i = lo; i <= hi; i++) {
        uint8_t mask = (uint8_t)(1u << (i % 8));
        if ((v >> (i - lo)) & 1)
            r[15 - i / 8] |= mask;
        else
            r[15 - i / 8] &= (uint8_t)~mask;
    }
}

// A CSD with every bit set but the ones given, so a field read a bit off shows.
static void csd_v1(uint8_t r[16], uint32_t c_size, uint32_t mult, uint32_t bl_len)
{
    memset(r, 0xFF, 16);
    set_bits(r, 127, 126, 0);
    set_bits(r, 83, 80, bl_len);
    set_bits(r, 73, 62, c_size);
    set_bits(r, 49, 47, mult);
}

static void csd_v2(uint8_t r[16], uint32_t c_size)
{
    memset(r, 0xFF, 16);
    set_bits(r, 127, 126, 1);
    set_bits(r, 69, 48, c_size);
}

TEST(sdhc_size)
{
    uint8_t r[16];
    csd_v2(r, 30386);                       // the 16 GB SDHC card on the media rig, by macOS's count
    CHECK_EQ(2, sd_csd_version(r));
    CHECK_EQ(31116288, sd_csd_sectors(r));
    csd_v2(r, 0);
    CHECK_EQ(1024, sd_csd_sectors(r));      // 512 KB
    memset(r, 0, 16);
    set_bits(r, 127, 126, 1);
    set_bits(r, 69, 48, 30386);             // the same with every other bit clear
    CHECK_EQ(31116288, sd_csd_sectors(r));
}

TEST(sdxc_size_at_the_top)
{
    uint8_t r[16];
    csd_v2(r, 0x3FFFFE);                    // 2 TB less 512 KB: just fits
    CHECK_EQ(0xFFFFFC00u, sd_csd_sectors(r));
    csd_v2(r, 0x3FFFFF);                    // 2 TB: 2^32 sectors, read as the most there can be
    CHECK_EQ(0xFFFFFFFFu, sd_csd_sectors(r));
}

TEST(sdsc_size)
{
    uint8_t r[16];
    csd_v1(r, 4095, 7, 10);                 // 2 GB in 1024-byte blocks
    CHECK_EQ(1, sd_csd_version(r));
    CHECK_EQ(4194304, sd_csd_sectors(r));
    csd_v1(r, 4095, 7, 11);                 // 4 GB in 2048-byte blocks
    CHECK_EQ(8388608, sd_csd_sectors(r));
    csd_v1(r, 3999, 5, 9);                  // (4000) x 128 blocks of 512
    CHECK_EQ(512000, sd_csd_sectors(r));
    csd_v1(r, 0, 0, 9);
    CHECK_EQ(4, sd_csd_sectors(r));
    memset(r, 0, 16);
    set_bits(r, 83, 80, 9);
    set_bits(r, 73, 62, 3999);
    set_bits(r, 49, 47, 5);
    CHECK_EQ(512000, sd_csd_sectors(r));    // the same with every other bit clear
}

TEST(csds_this_doesnt_know)
{
    uint8_t r[16];
    csd_v1(r, 4095, 7, 8);                  // 256-byte blocks: not an SD card's
    CHECK_EQ(0, sd_csd_sectors(r));
    csd_v1(r, 4095, 7, 12);
    CHECK_EQ(0, sd_csd_sectors(r));
    csd_v2(r, 100);
    set_bits(r, 127, 126, 2);               // SDUC
    CHECK_EQ(3, sd_csd_version(r));
    CHECK_EQ(0, sd_csd_sectors(r));
    set_bits(r, 127, 126, 3);               // reserved
    CHECK_EQ(0, sd_csd_version(r));
    CHECK_EQ(0, sd_csd_sectors(r));
}

static uint8_t frame_crc(uint8_t cmd, uint32_t arg)
{
    uint8_t f[5] = { (uint8_t)(0x40 | cmd), (uint8_t)(arg >> 24), (uint8_t)(arg >> 16), (uint8_t)(arg >> 8),
                     (uint8_t)arg };
    return (uint8_t)(sd_crc7(f, 5) << 1 | 1);
}

TEST(command_crcs)
{
    // The frames every SPI-mode driver sends, with their well-known last bytes.
    CHECK_EQ(0x95, frame_crc(0, 0));
    CHECK_EQ(0x87, frame_crc(8, 0x1AA));
    CHECK_EQ(0x55, frame_crc(17, 0));
    CHECK_EQ(0x65, frame_crc(55, 0));
    CHECK_EQ(0x77, frame_crc(41, 0x40000000));
    CHECK_EQ(0xFD, frame_crc(58, 0));
}

TEST(data_crcs)
{
    uint8_t block[512];
    memset(block, 0xFF, sizeof block);
    CHECK_EQ(0x7FA1, sd_crc16(block, 512));     // the specification's example
    CHECK_EQ(0, sd_crc16(block, 0));
    uint8_t ascii[9] = { '1', '2', '3', '4', '5', '6', '7', '8', '9' };
    CHECK_EQ(0x31C3, sd_crc16(ascii, 9));       // CRC-16/XMODEM's check value
}

int main(void)
{
    RUN(sdhc_size);
    RUN(sdxc_size_at_the_top);
    RUN(sdsc_size);
    RUN(csds_this_doesnt_know);
    RUN(command_crcs);
    RUN(data_crcs);
    return TEST_RESULT();
}
