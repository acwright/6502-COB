#include "serve.h"

#include <stdio.h>

#include "pico/stdlib.h"

#include "serve_protocol.h"

static const serve_ops_t *ops;

static uint8_t next(void)
{
    int c;
    while ((c = getchar_timeout_us(0)) < 0)
        ops->idle();
    return (uint8_t)c;
}

// Bytes go out as they are: no CR before LF, as printf would add.
static void put(uint8_t b)
{
    putchar_raw(b);
}

static void ok(void)
{
    put(SERVE_OK);
    stdio_flush();
}

static void data(uint16_t count)
{
    // The bytes are read first, so the count goes out ahead of them.
    static uint8_t buf[512];
    uint16_t n = 0;
    if (count > sizeof buf)
        count = sizeof buf;
    while (n < count) {
        buf[n++] = ops->read(0);
        if (!ops->transferring())
            break;                          // that read ended the sector
    }
    put((uint8_t)n);
    put((uint8_t)(n >> 8));
    for (uint16_t i = 0; i < n; i++)
        put(buf[i]);
    stdio_flush();
}

static void stats(void)
{
    uint32_t w[SERVE_STAT_COUNT] = { 0 };
    ops->stats(w);
    put(SERVE_STAT_COUNT);
    for (int i = 0; i < SERVE_STAT_COUNT; i++)
        for (int b = 0; b < 4; b++)
            put((uint8_t)(w[i] >> (8 * b)));
    stdio_flush();
}

void serve_run(const serve_ops_t *o)
{
    ops = o;
    fputs(SERVE_HELLO, stdout);
    stdio_flush();
    for (;;) {
        uint8_t cmd = next();
        switch (cmd) {
        case SERVE_READ: {
            uint8_t reg = next();
            put(ops->read(reg & 7));
            stdio_flush();
            break;
        }
        case SERVE_WRITE: {
            uint8_t reg = next();
            uint8_t v = next();
            ops->write(reg & 7, v);
            break;
        }
        case SERVE_DATA: {
            uint8_t lo = next();
            uint8_t hi = next();
            data((uint16_t)(lo | hi << 8));
            break;
        }
        case SERVE_POWER:
            ops->power_on(next() != 0);
            ok();
            break;
        case SERVE_CARD:
            ops->card(next() != 0);
            ok();
            break;
        case SERVE_RESB:
            ops->resb(next() != 0);
            ok();
            break;
        case SERVE_STATS:
            stats();
            break;
        case SERVE_QUIT:
            ops->quit();
            ok();
            return;
        default:
            break;                          // a stray byte (a CR after "serve"): skipped
        }
    }
}
