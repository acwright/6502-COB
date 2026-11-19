#include "flash.h"

#include "pico.h"           // the board header

#if FW_HAS_FLASH

#include <string.h>

#include "hardware/gpio.h"
#include "hardware/spi.h"
#include "pico/time.h"

#define SPI FW_FLASH_SPI
#define PROGRAM_US  10000u      // a page program: the W25Q...JV's maximum is 3 ms
#define ERASE_US    1000000u    // a 4 KB erase: its maximum is 400 ms

static flash_info_t info;
static nor_t nor;
static bool four_byte;

static inline void select(void) { gpio_put(FW_PIN_FLASH_CS, 0); }
// CS stays high at least 50 ns between commands after a write-type one (tSHSL2):
// without the wait it's high for a few nanoseconds at 150 MHz, and the chip
// misses the next command. 30 cycles is 200 ns.
static inline void deselect(void)
{
    gpio_put(FW_PIN_FLASH_CS, 1);
    busy_wait_at_least_cycles(30);
}

static void simple(uint8_t op)
{
    select();
    spi_write_blocking(SPI, &op, 1);
    deselect();
}

static uint8_t status(uint8_t op)
{
    uint8_t out[2] = { op, 0xFF }, in[2];
    select();
    spi_write_read_blocking(SPI, out, in, 2);
    deselect();
    return in[1];
}

// The opcode and the address, in 3 or 4 bytes.
static void header(uint8_t op3, uint8_t op4, uint32_t addr)
{
    uint8_t h[5];
    size_t n = 0;
    h[n++] = four_byte ? op4 : op3;
    if (four_byte)
        h[n++] = (uint8_t)(addr >> 24);
    h[n++] = (uint8_t)(addr >> 16);
    h[n++] = (uint8_t)(addr >> 8);
    h[n++] = (uint8_t)addr;
    spi_write_blocking(SPI, h, n);
}

// Waits for BUSY (status 1, bit 0) to clear. Returns the time it took, or 0 on a timeout.
static uint32_t wait_done(uint32_t limit_us)
{
    uint32_t start = time_us_32();
    for (;;) {
        uint32_t t = time_us_32() - start;
        if (!(status(0x05) & 0x01))
            return t ? t : 1;
        if (t > limit_us) {
            info.timeouts++;
            return 0;
        }
    }
}

static bool f_read(nor_t *n, uint32_t addr, uint8_t *buf, uint32_t len)
{
    (void)n;
    select();
    header(0x03, 0x13, addr);
    spi_read_blocking(SPI, 0xFF, buf, len);
    deselect();
    return true;
}

// Write Enable, then a check that the chip took it (WEL, status 1 bit 1).
static bool write_enable(void)
{
    simple(0x06);
    if (status(0x05) & 0x02)
        return true;
    info.wel_failures++;
    return false;
}

static bool f_program(nor_t *n, uint32_t addr, const uint8_t *buf, uint32_t len)
{
    (void)n;
    if (!write_enable())
        return false;
    select();
    header(0x02, 0x12, addr);
    spi_write_blocking(SPI, buf, len);
    deselect();
    uint32_t us = wait_done(PROGRAM_US);
    info.programs++;
    if (us > info.longest_program_us)
        info.longest_program_us = us;
    return us != 0;
}

static bool f_erase(nor_t *n, uint32_t addr)
{
    (void)n;
    if (!write_enable())
        return false;
    select();
    header(0x20, 0x21, addr);
    deselect();
    uint32_t us = wait_done(ERASE_US);
    info.erases++;
    if (us > info.longest_erase_us)
        info.longest_erase_us = us;
    return us != 0;
}

nor_t *flash_init(uint32_t hz)
{
    memset(&info, 0, sizeof info);
    gpio_init(FW_PIN_FLASH_CS);
    gpio_put(FW_PIN_FLASH_CS, 1);
    gpio_set_dir(FW_PIN_FLASH_CS, GPIO_OUT);
    info.hz = spi_init(SPI, hz);
    spi_set_format(SPI, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_MSB_FIRST);
    gpio_set_function(FW_PIN_FLASH_SCK, GPIO_FUNC_SPI);
    gpio_set_function(FW_PIN_FLASH_MOSI, GPIO_FUNC_SPI);
    gpio_set_function(FW_PIN_FLASH_MISO, GPIO_FUNC_SPI);

    simple(0xAB);                           // release from power-down, if it was
    busy_wait_us(5);
    simple(0x66);                           // enable reset, then reset
    simple(0x99);
    busy_wait_us(50);                       // tRST: 30 us

    uint8_t out[4] = { 0x9F, 0xFF, 0xFF, 0xFF }, in[4];
    select();
    spi_write_read_blocking(SPI, out, in, 4);
    deselect();
    memcpy(info.jedec, in + 1, 3);
    info.status[0] = status(0x05);
    info.status[1] = status(0x35);
    info.status[2] = status(0x15);

    nor = (nor_t){ .size = nor_size_from_jedec(info.jedec), .read = f_read, .program = f_program,
                   .erase = f_erase };
    four_byte = nor_needs_4byte(nor.size);
    if (nor.size) {
        // Lift any write protection, in the volatile bits only, so nothing wears:
        // the block-protect bits (status 1, bits 2-6), then the per-block locks if WPS is set.
        if (info.status[0] & 0x7C) {
            simple(0x50);                   // volatile status register write enable
            uint8_t w[2] = { 0x01, (uint8_t)(info.status[0] & ~0x7C) };
            select();
            spi_write_blocking(SPI, w, 2);
            deselect();
            wait_done(PROGRAM_US);
        }
        if (info.status[2] & 0x04) {
            simple(0x06);
            simple(0x98);                   // global block unlock
        }
    }
    return &nor;
}

uint32_t flash_set_hz(uint32_t hz)
{
    info.hz = spi_set_baudrate(SPI, hz);
    return info.hz;
}

const flash_info_t *flash_info(void) { return &info; }

#endif
