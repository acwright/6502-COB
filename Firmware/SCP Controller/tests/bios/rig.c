#include "rig.h"

#include <errno.h>
#include <fcntl.h>
#include <glob.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>

#define ATA_STATUS 7

struct rig {
    int fd;
    uint8_t out[4096];
    size_t out_len;
    uint64_t round_trips;
};

static void fatal(const char *what)
{
    fprintf(stderr, "rig: %s\n", what);
    exit(3);
}

static void send_all(rig_t *r, const uint8_t *p, size_t n)
{
    while (n) {
        ssize_t k = write(r->fd, p, n);
        if (k < 0) {
            if (errno == EAGAIN || errno == EINTR) {
                usleep(100);
                continue;
            }
            fatal("write failed");
        }
        p += k;
        n -= (size_t)k;
    }
}

static void flush_out(rig_t *r)
{
    if (r->out_len) {
        send_all(r, r->out, r->out_len);
        r->out_len = 0;
    }
}

static void queue(rig_t *r, const uint8_t *p, size_t n)
{
    if (r->out_len + n > sizeof r->out)
        flush_out(r);
    memcpy(r->out + r->out_len, p, n);
    r->out_len += n;
}

// Reads exactly n bytes, or ends the program after RIG_TIMEOUT_S of silence.
static void take(rig_t *r, uint8_t *p, size_t n)
{
    while (n) {
        fd_set set;
        FD_ZERO(&set);
        FD_SET(r->fd, &set);
        struct timeval tv = { RIG_TIMEOUT_S, 0 };
        int s = select(r->fd + 1, &set, NULL, NULL, &tv);
        if (s == 0)
            fatal("no answer from the rig");
        if (s < 0) {
            if (errno == EINTR)
                continue;
            fatal("select failed");
        }
        ssize_t k = read(r->fd, p, n);
        if (k < 0) {
            if (errno == EAGAIN || errno == EINTR)
                continue;
            fatal("read failed");
        }
        p += k;
        n -= (size_t)k;
    }
}

static uint8_t take1(rig_t *r)
{
    uint8_t b;
    take(r, &b, 1);
    return b;
}

// Everything the rig says for `ms`, thrown away.
static void drain(rig_t *r, int ms)
{
    uint8_t junk[256];
    struct timespec t0;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (;;) {
        struct timespec t;
        clock_gettime(CLOCK_MONOTONIC, &t);
        long left = ms - ((t.tv_sec - t0.tv_sec) * 1000 + (t.tv_nsec - t0.tv_nsec) / 1000000);
        if (left <= 0)
            return;
        fd_set set;
        FD_ZERO(&set);
        FD_SET(r->fd, &set);
        struct timeval tv = { 0, left * 1000 };
        if (select(r->fd + 1, &set, NULL, NULL, &tv) > 0 && read(r->fd, junk, sizeof junk) < 0 && errno != EAGAIN)
            return;
    }
}

rig_t *rig_open(const char *port, double bus_mhz)
{
    char found[256] = "";
    if (!port) {
        glob_t g;
        if (glob("/dev/cu.usbmodem*", 0, NULL, &g) == 0 && g.gl_pathc)
            snprintf(found, sizeof found, "%s", g.gl_pathv[0]);
        globfree(&g);
        if (!found[0]) {
            fprintf(stderr, "rig: no /dev/cu.usbmodem*: is the Pico 2 plugged in and running a rig build?\n");
            return NULL;
        }
        port = found;
    }
    rig_t *r = calloc(1, sizeof *r);
    r->fd = open(port, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (r->fd < 0) {
        perror(port);
        free(r);
        return NULL;
    }
    struct termios t;
    tcgetattr(r->fd, &t);
    cfmakeraw(&t);
    t.c_cflag |= CLOCAL | CREAD;
    tcsetattr(r->fd, TCSANOW, &t);
    tcflush(r->fd, TCIOFLUSH);

    // Out of serve mode, if a run before this one left it there, then into it.
    uint8_t quit[2] = { SERVE_QUIT, '\r' };
    send_all(r, quit, 2);
    drain(r, 300);
    char cmd[32];
    snprintf(cmd, sizeof cmd, "serve %g\r", bus_mhz > 0 ? bus_mhz : 1.0);
    send_all(r, (const uint8_t *)cmd, strlen(cmd));
    const char *hello = SERVE_HELLO;
    size_t matched = 0, len = strlen(hello);
    while (matched < len) {
        uint8_t b = take1(r);
        matched = b == (uint8_t)hello[matched] ? matched + 1 : (b == (uint8_t)hello[0] ? 1 : 0);
    }
    return r;
}

void rig_close(rig_t *r)
{
    if (!r)
        return;
    uint8_t q = SERVE_QUIT;
    queue(r, &q, 1);
    flush_out(r);
    if (take1(r) != SERVE_OK)
        fprintf(stderr, "rig: no OK on quitting\n");
    close(r->fd);
    free(r);
}

uint8_t rig_read(rig_t *r, unsigned reg)
{
    uint8_t c[2] = { SERVE_READ, (uint8_t)reg };
    queue(r, c, 2);
    flush_out(r);
    r->round_trips++;
    return take1(r);
}

void rig_write(rig_t *r, unsigned reg, uint8_t value)
{
    uint8_t c[3] = { SERVE_WRITE, (uint8_t)reg, value };
    queue(r, c, 3);
}

size_t rig_data(rig_t *r, uint8_t *buf, size_t max)
{
    uint8_t c[3] = { SERVE_DATA, (uint8_t)max, (uint8_t)(max >> 8) };
    queue(r, c, 3);
    flush_out(r);
    r->round_trips++;
    uint8_t n2[2];
    take(r, n2, 2);
    size_t n = (size_t)(n2[0] | n2[1] << 8);
    if (n > max)
        fatal("a data run longer than asked for");
    take(r, buf, n);
    return n;
}

static void command(rig_t *r, uint8_t cmd, uint8_t arg)
{
    uint8_t c[2] = { cmd, arg };
    queue(r, c, 2);
    flush_out(r);
    r->round_trips++;
    if (take1(r) != SERVE_OK)
        fatal("a command not acknowledged");
}

void rig_power_on(rig_t *r, bool card)
{
    command(r, SERVE_POWER, card);
}

void rig_card(rig_t *r, bool in)
{
    command(r, SERVE_CARD, in);
}

void rig_stats(rig_t *r, uint32_t words[SERVE_STAT_COUNT])
{
    uint8_t c = SERVE_STATS;
    queue(r, &c, 1);
    flush_out(r);
    r->round_trips++;
    uint8_t n = take1(r);
    for (unsigned i = 0; i < n; i++) {
        uint8_t b[4];
        take(r, b, 4);
        if (i < SERVE_STAT_COUNT)
            words[i] = (uint32_t)(b[0] | b[1] << 8 | b[2] << 16 | (uint32_t)b[3] << 24);
    }
    for (unsigned i = n; i < SERVE_STAT_COUNT; i++)
        words[i] = 0;
}

static double seconds(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (double)t.tv_sec + (double)t.tv_nsec / 1e9;
}

// Polls status until (status & mask) == want. Returns the status, or -1 after RIG_TIMEOUT_S.
static int wait_status(rig_t *r, uint8_t mask, uint8_t want)
{
    double end = seconds() + RIG_TIMEOUT_S;
    do {
        uint8_t s = rig_read(r, ATA_STATUS);
        if ((s & mask) == want || (!(s & 0x80) && (s & 0x01)))
            return s;
    } while (seconds() < end);
    return -1;
}

bool rig_wait_ready(rig_t *r)
{
    int s = wait_status(r, 0x80, 0x00);
    return s > 0;
}

static bool command_sector(rig_t *r, uint8_t cmd, uint32_t lba)
{
    if (wait_status(r, 0x80, 0x00) < 0)
        return false;
    rig_write(r, 2, 1);
    rig_write(r, 3, (uint8_t)lba);
    rig_write(r, 4, (uint8_t)(lba >> 8));
    rig_write(r, 5, (uint8_t)(lba >> 16));
    rig_write(r, 6, (uint8_t)(0xE0 | ((lba >> 24) & 0x0F)));
    rig_write(r, ATA_STATUS, cmd);
    int s = wait_status(r, 0x88, 0x08);         // BSY clear, DRQ set
    return s >= 0 && !(s & 0x01);
}

bool rig_sector_read(rig_t *r, uint32_t lba, uint8_t buf[512])
{
    if (!command_sector(r, 0x20, lba))
        return false;
    size_t n = 0;
    while (n < 512) {
        size_t k = rig_data(r, buf + n, 512 - n);
        if (!k)
            return false;
        n += k;
    }
    return true;
}

bool rig_sector_write(rig_t *r, uint32_t lba, const uint8_t buf[512])
{
    if (!command_sector(r, 0x30, lba))
        return false;
    for (int i = 0; i < 512; i++)
        rig_write(r, 0, buf[i]);
    int s = wait_status(r, 0x80, 0x00);
    return s >= 0 && !(s & 0x01);
}

uint64_t rig_round_trips(const rig_t *r)
{
    return r->round_trips;
}
