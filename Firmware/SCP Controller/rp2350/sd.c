// The SD card in SPI mode, by the SD Physical Layer Simplified Specification:
// CMD0, CMD8, ACMD41 until ready, CMD58 (the OCR: block or byte addresses),
// CMD59 (CRC on), CMD9 and CMD10 (CSD and CID), CMD16 on an SDSC card; then
// CMD17 and CMD24 for one sector at a time, as the BIOS asks for them.
#include "sd.h"

#include "pico.h"           // the board header

#if FW_HAS_SD

#include <stdio.h>
#include <string.h>

#include "hardware/gpio.h"
#include "hardware/spi.h"
#include "pico/time.h"

#include "sdcard.h"

#define SPI FW_SD_SPI
#define START_HZ    400000u     // the specification's limit until the card is started
#define POWER_MS    10u         // a card just put in is powered only now: let its supply settle
#define CMD0_MS     1000u       // and keep asking it to go idle this long: on the rig a card just
                                // put in took up to about 300 ms to answer
#define CMD0_GAP_MS 5u          // ... this far apart
#define ACMD41_MS   1000u       // the specification's limit for a card to start
#define TOKEN_MS    200u        // for a read's data token (the specification: 100 ms)
#define WRITE_MS    1000u       // for a write's busy time (SDXC's limit: 500 ms)
#define READY_MS    500u        // for the card to be idle before a command

enum { STEP_POWER, STEP_CMD0, STEP_CMD8, STEP_ACMD41, STEP_FINISH };

static sd_info_t info;
static medium_t medium;
static uint32_t run_hz;
static bool verbose;
static int step;
static unsigned tries;
static bool v2;
static uint32_t step_ms, deadline_ms, started_ms, wake_deadline_ms;
static bool last_raw;
static uint32_t raw_since_ms;

static uint32_t now_ms(void)
{
    return to_ms_since_boot(get_absolute_time());
}

static void say(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
#include <stdarg.h>
static void say(const char *fmt, ...)
{
    if (!verbose)
        return;
    va_list ap;
    va_start(ap, fmt);
    printf("  sd: ");
    vprintf(fmt, ap);
    printf("\r\n");
    va_end(ap);
}

// --- The wire ---------------------------------------------------------------

static inline void select(void) { gpio_put(FW_PIN_SD_CS, 0); }

static uint8_t xfer(uint8_t out)
{
    uint8_t in;
    spi_write_read_blocking(SPI, &out, &in, 1);
    return in;
}

static void deselect(void)
{
    gpio_put(FW_PIN_SD_CS, 1);
    xfer(0xFF);             // eight clocks, so the card lets go of DO
}

static bool wait_ready(uint32_t ms)
{
    uint32_t start = now_ms();
    do {
        if (xfer(0xFF) == 0xFF)
            return true;
    } while (now_ms() - start < ms);
    return false;
}

// Sends a command, with its CRC7, and returns R1: $FF if none came.
static uint8_t command(uint8_t cmd, uint32_t arg)
{
    if (cmd != 0)
        wait_ready(READY_MS);
    uint8_t f[6] = { (uint8_t)(0x40 | cmd), (uint8_t)(arg >> 24), (uint8_t)(arg >> 16),
                     (uint8_t)(arg >> 8), (uint8_t)arg, 0 };
    f[5] = (uint8_t)(sd_crc7(f, 5) << 1 | 1);
    spi_write_blocking(SPI, f, 6);
    uint8_t r = 0xFF;
    for (int i = 0; i < 10 && (r & 0x80); i++)     // R1 within 8 bytes (NCR)
        r = xfer(0xFF);
    return r;
}

static uint32_t take32(void)
{
    uint32_t v = 0;
    for (int i = 0; i < 4; i++)
        v = v << 8 | xfer(0xFF);
    return v;
}

typedef enum { BLOCK_OK, BLOCK_CRC, BLOCK_FAILED } block_t;

// A data block after a read command: its token, len bytes and its CRC16.
static block_t take_block(uint8_t *buf, size_t len)
{
    uint32_t start = now_ms();
    uint8_t token;
    do {
        token = xfer(0xFF);
    } while (token == 0xFF && now_ms() - start < TOKEN_MS);
    if (token != 0xFE)
        return BLOCK_FAILED;
    spi_read_blocking(SPI, 0xFF, buf, len);
    uint16_t crc = (uint16_t)(xfer(0xFF) << 8);
    crc |= xfer(0xFF);
    return crc == sd_crc16(buf, len) ? BLOCK_OK : BLOCK_CRC;
}

// --- Start-up, a step at a time ----------------------------------------------

static void fail(const char *at)
{
    deselect();
    info.state = SD_FAILED;
    info.failed_at = at;
    info.start_ms = now_ms() - started_ms;
    say("failed at %s, after %lu ms", at, (unsigned long)info.start_ms);
}

static void begin_start(void)
{
    info.state = SD_STARTING;
    info.failed_at = NULL;
    info.sectors = 0;
    step = STEP_POWER;
    started_ms = now_ms();
    step_ms = started_ms + POWER_MS;
}

// The CSD or the CID: a command, then a 16-byte block. True if it came, CRC right.
static bool take_register(uint8_t cmd, uint8_t reg[16])
{
    for (unsigned t = 0; t < SD_TRIES; t++) {
        select();
        uint8_t r = command(cmd, 0);
        block_t b = r == 0 ? take_block(reg, 16) : BLOCK_FAILED;
        deselect();
        say("CMD%u: R1 $%02X, %s", cmd, r, b == BLOCK_OK ? "block right" : b == BLOCK_CRC ? "CRC WRONG" : "no block");
        if (b == BLOCK_OK)
            return true;
    }
    return false;
}

static void finish(void)
{
    uint8_t r;
    info.high_capacity = false;
    info.ocr = 0;
    if (v2) {
        select();
        r = command(58, 0);
        info.ocr = take32();
        deselect();
        say("CMD58: R1 $%02X, OCR $%08lX", r, (unsigned long)info.ocr);
        if (r != 0)
            return fail("CMD58 (the OCR)");
        info.high_capacity = (info.ocr & (1u << 30)) != 0;      // CCS
    }
    select();
    r = command(59, 1);
    deselect();
    say("CMD59 (CRC on): R1 $%02X", r);
    if (r != 0)
        return fail("CMD59 (CRC on)");
    if (!take_register(9, info.csd))
        return fail("CMD9 (the CSD)");
    if (!take_register(10, info.cid))
        return fail("CMD10 (the CID)");
    if (!info.high_capacity) {
        select();
        r = command(16, 512);
        deselect();
        say("CMD16 (512-byte blocks): R1 $%02X", r);
        if (r != 0)
            return fail("CMD16 (512-byte blocks)");
    }
    info.sectors = sd_csd_sectors(info.csd);
    say("CSD %u.0: %lu sectors", sd_csd_version(info.csd), (unsigned long)info.sectors);
    if (info.sectors == 0)
        return fail("the CSD (a structure this doesn't know)");
    info.hz = spi_set_baudrate(SPI, run_hz);
    info.start_ms = now_ms() - started_ms;
    info.state = SD_READY;
    medium.generation++;
    say("ready: %s, %lu ms, clock %lu Hz", info.high_capacity ? "SDHC/SDXC" : "SDSC",
        (unsigned long)info.start_ms, (unsigned long)info.hz);
}

static void start_step(void)
{
    uint8_t r;
    switch (step) {
    case STEP_POWER:
        if (now_ms() < step_ms)
            break;
        spi_set_baudrate(SPI, START_HZ);
        tries = 0;
        info.restarts = 0;
        wake_deadline_ms = now_ms() + CMD0_MS;
        step_ms = 0;
        step = STEP_CMD0;
        break;
    case STEP_CMD0:
        // A card just put in may take a while to wake: each try is CMD0 after
        // at least 74 clocks with CS high, CMD0_GAP_MS apart, for up to CMD0_MS.
        if (now_ms() < step_ms)
            break;
        gpio_put(FW_PIN_SD_CS, 1);
        for (int i = 0; i < 10; i++)
            xfer(0xFF);
        select();
        r = command(0, 0);
        deselect();
        info.cmd0_tries = ++tries;
        info.cmd0_last_r1 = r;
        if (r == 0x01) {
            say("CMD0: R1 $01 after %u tries, %lu ms after card detect settled", tries,
                (unsigned long)(now_ms() - started_ms));
            step = STEP_CMD8;
        } else if ((int32_t)(now_ms() - wake_deadline_ms) >= 0) {
            say("CMD0: R1 $%02X after %u tries", r, tries);
            fail("CMD0 (no answer: is a card in?)");
        } else {
            step_ms = now_ms() + CMD0_GAP_MS;
        }
        break;
    case STEP_CMD8: {
        select();
        r = command(8, 0x1AA);
        uint32_t echo = (r & 0x04) ? 0 : take32();
        deselect();
        say("CMD8: R1 $%02X, echo $%08lX", r, (unsigned long)echo);
        info.cmd8_last_r1 = r;
        if (r == 0x01 && (echo & 0xFFF) == 0x1AA) {
            v2 = true;                      // version 2 or later: SDHC/SDXC possible
        } else if (r == 0x05) {
            v2 = false;                     // idle, and an illegal command: version 1, SDSC
        } else if ((int32_t)(now_ms() - wake_deadline_ms) < 0) {
            // A card just put in can answer CMD0 before it's settled, and then
            // fumble CMD8. Inside the wake window that's not a failure: start
            // again from CMD0.
            info.restarts++;
            step_ms = now_ms() + CMD0_GAP_MS;
            step = STEP_CMD0;
            break;
        } else {
            return fail("CMD8 (the voltage check)");
        }
        tries = 0;
        deadline_ms = now_ms() + ACMD41_MS;
        step_ms = 0;
        step = STEP_ACMD41;
        break;
    }
    case STEP_ACMD41:
        if (now_ms() < step_ms)
            break;
        select();
        command(55, 0);
        r = command(41, v2 ? 1u << 30 : 0);     // HCS: this host takes SDHC/SDXC
        deselect();
        tries++;
        if (r == 0x00) {
            info.acmd41_tries = tries;
            say("ACMD41: ready after %u tries", tries);
            step = STEP_FINISH;
        } else if (r & 0x04) {
            fail("ACMD41 (refused: an MMC card, not SD)");
        } else if ((int32_t)(now_ms() - deadline_ms) >= 0) {
            say("ACMD41: R1 $%02X after %u tries", r, tries);
            fail("ACMD41 (never ready)");
        } else {
            step_ms = now_ms() + 2;
        }
        break;
    case STEP_FINISH:
        finish();
        break;
    }
}

// --- Card detect --------------------------------------------------------------

bool sd_card_detect_raw(void)
{
    return gpio_get(FW_PIN_SD_CD) == FW_SD_CD_CARD_IN;
}

void sd_poll(void)
{
    bool raw = sd_card_detect_raw();
    uint32_t now = now_ms();
    if (raw != last_raw) {
        last_raw = raw;
        raw_since_ms = now;
    } else if (raw != info.card_in && now - raw_since_ms >= SD_DEBOUNCE_MS) {
        info.card_in = raw;
        if (raw)
            begin_start();
        else
            info.state = SD_EMPTY;
    }
    if (info.state == SD_STARTING)
        start_step();
}

// --- The medium -----------------------------------------------------------------

static bool sd_ready(medium_t *m)
{
    (void)m;
    return info.state == SD_READY;
}

static uint32_t sd_sectors(medium_t *m)
{
    (void)m;
    return info.state == SD_READY ? info.sectors : 0;
}

static medium_result_t failed(void)
{
    info.failures++;
    return sd_card_detect_raw() ? MEDIUM_FAILED : MEDIUM_GONE;
}

// A read or write that failed every try. If a card is in, it may not be the card
// that was started: one swapped while sd_poll() wasn't running (in a long job)
// leaves card detect where it was. So the card is started again from scratch,
// which reads its size again; a new start is a new generation, and the drive
// ends any command that was using the old one.
static medium_result_t gave_up(void)
{
    medium_result_t r = failed();
    if (r == MEDIUM_FAILED && info.state == SD_READY) {
        info.restarts_after_failure++;
        begin_start();
    }
    return r;
}

static uint32_t address(uint32_t sector)
{
    return info.high_capacity ? sector : sector * 512u;
}

static medium_result_t sd_read(medium_t *m, uint32_t sector, uint8_t *buf)
{
    (void)m;
    if (info.state != SD_READY || sector >= info.sectors)
        return failed();
    info.reads++;
    for (unsigned t = 0; t < SD_TRIES; t++) {
        select();
        uint8_t r = command(17, address(sector));
        block_t b = r == 0 ? take_block(buf, 512) : BLOCK_FAILED;
        deselect();
        if (b == BLOCK_OK)
            return MEDIUM_OK;
        if (b == BLOCK_CRC)
            info.crc_retries++;
        else if (!sd_card_detect_raw())
            break;
    }
    return gave_up();
}

static medium_result_t sd_write(medium_t *m, uint32_t sector, const uint8_t *buf)
{
    (void)m;
    if (info.state != SD_READY || sector >= info.sectors)
        return failed();
    info.writes++;
    uint16_t crc = sd_crc16(buf, 512);
    for (unsigned t = 0; t < SD_TRIES; t++) {
        select();
        uint8_t r = command(24, address(sector));
        uint8_t resp = 0xFF;
        bool idle = false;
        if (r == 0) {
            xfer(0xFF);                     // a byte's gap (NWR)
            xfer(0xFE);                     // the start token
            spi_write_blocking(SPI, buf, 512);
            xfer((uint8_t)(crc >> 8));
            xfer((uint8_t)crc);
            for (int i = 0; i < 8 && resp == 0xFF; i++)
                resp = xfer(0xFF);
            idle = wait_ready(WRITE_MS);    // the card holds DO low while it programs
        }
        deselect();
        if (r == 0 && (resp & 0x1F) == 0x05 && idle) {
            // Accepted and programmed: CMD13's R2 says whether it went in right.
            select();
            uint8_t r1 = command(13, 0);
            uint8_t r2 = xfer(0xFF);
            deselect();
            if (r1 == 0 && r2 == 0)
                return MEDIUM_OK;
            info.write_faults.status++;
            info.write_faults.last_status = (uint16_t)(r1 << 8 | r2);
        } else if (r != 0) {
            info.write_faults.command++;
            info.write_faults.last_r1 = r;
        } else if ((resp & 0x1F) == 0x0B) {
            info.crc_retries++;             // the card saw a CRC error: send it again
            continue;
        } else if ((resp & 0x1F) != 0x05) {
            info.write_faults.response++;
            info.write_faults.last_response = resp;
        } else {
            info.write_faults.busy++;
        }
        info.write_faults.last_sector = sector;
        if (!sd_card_detect_raw())
            break;
    }
    return gave_up();
}

// --- Set-up -------------------------------------------------------------------------

void sd_init(uint32_t hz)
{
    run_hz = hz;
    spi_init(SPI, START_HZ);
    spi_set_format(SPI, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_MSB_FIRST);
    gpio_set_function(FW_PIN_SD_SCK, GPIO_FUNC_SPI);
    gpio_set_function(FW_PIN_SD_MOSI, GPIO_FUNC_SPI);
    gpio_set_function(FW_PIN_SD_MISO, GPIO_FUNC_SPI);
    gpio_pull_up(FW_PIN_SD_MISO);           // DO floats until the card answers
    gpio_init(FW_PIN_SD_CS);
    gpio_put(FW_PIN_SD_CS, 1);
    gpio_set_dir(FW_PIN_SD_CS, GPIO_OUT);
    gpio_init(FW_PIN_SD_CD);
    gpio_set_dir(FW_PIN_SD_CD, GPIO_IN);
#if FW_SD_CD_PULLUP
    gpio_pull_up(FW_PIN_SD_CD);
#else
    gpio_disable_pulls(FW_PIN_SD_CD);       // the board's own pull-up
#endif
    busy_wait_us(100);                      // the pull-up settles

    memset(&info, 0, sizeof info);
    medium = (medium_t){
        .name = "SD card",
        .ready = sd_ready,
        .sectors = sd_sectors,
        .read = sd_read,
        .write = sd_write,
    };
    // At power-on a card in the slot isn't bouncing: start it now.
    last_raw = info.card_in = sd_card_detect_raw();
    raw_since_ms = now_ms();
    if (info.card_in)
        begin_start();
}

void sd_power_on(void)
{
    last_raw = info.card_in = sd_card_detect_raw();
    raw_since_ms = now_ms();
    if (info.card_in)
        begin_start();
    else
        info.state = SD_EMPTY;
}

void sd_restart(bool verbose_)
{
    verbose = verbose_;
    if (sd_card_detect_raw()) {
        info.card_in = last_raw = true;
        begin_start();
        while (info.state == SD_STARTING)
            start_step();
    } else {
        say("no card in the slot");
    }
    verbose = false;
}

uint32_t sd_set_hz(uint32_t hz)
{
    run_hz = hz;
    if (info.state == SD_READY)
        info.hz = spi_set_baudrate(SPI, hz);
    else
        info.hz = hz;
    return info.hz;
}

const sd_info_t *sd_info(void) { return &info; }
medium_t *sd_medium(void) { return &medium; }

#endif
