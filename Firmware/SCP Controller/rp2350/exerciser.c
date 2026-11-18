#include "exerciser.h"

#include "pico.h"          // the board header: FW_HAS_EXERCISER

#if FW_HAS_EXERCISER

#include <math.h>
#include <string.h>

#include "hardware/clocks.h"
#include "hardware/dma.h"
#include "hardware/gpio.h"
#include "hardware/pio.h"
#include "hardware/structs/io_bank0.h"
#include "pico/time.h"

#include "exerciser.pio.h"

_Static_assert(FW_PIN_EXER_BASE == 15 && FW_PIN_RB == 9 && FW_PIN_CS == 11 && FW_PIN_D0 == 0,
               "exerciser.pio's pin numbers");

#define EX_PIO      pio1
#define SM_PLAYER   0
#define SM_SAMPLER  1

// The phase word's pins: GPIO15-21 drive GPIO8-14.
#define P_RESB 0x01u
#define P_RB   0x02u
#define P_WB   0x04u
#define P_CS   0x08u
#define P_ADDR 0x70u
#define P_IDLE (P_RESB | P_RB | P_WB | P_CS)
#define SAMPLE 0x80u

static int dma_tx = -1, dma_rx = -1;
static uint sampler_offset;
static uint32_t rx_words[1024];

static uint32_t addr_pins(unsigned reg)
{
    return (((reg >> 2) & 1u) << 4) | (((reg >> 1) & 1u) << 5) | ((reg & 1u) << 6);
}

void stream_init(stream_t *s, uint32_t *words, size_t cap, double mhz)
{
    memset(s, 0, sizeof *s);
    s->words = words;
    s->cap = cap;
    s->pins = P_IDLE;
    s->mhz = mhz;
    s->ns_per_clock = 1e9 / (double)clock_get_hz(clk_sys);
}

static long clocks(const stream_t *s, double ns)
{
    return lround(ns / s->ns_per_clock);
}

// A phase of `total` clocks. One that changes no pin and samples nothing just
// makes the phase before it longer.
static void phase(stream_t *s, uint32_t pins, long total, bool sample)
{
    if (s->marker) {
        sample = true;
        s->marker = false;
    }
    long delay = total - (sample ? 7 : 5);
    if (delay < 0)
        delay = 0;
    if (!sample && s->count && pins == s->pins && !(s->words[s->count - 1] & SAMPLE)) {
        s->words[s->count - 1] += (uint32_t)total << 8;
        return;
    }
    if (s->count < s->cap)
        s->words[s->count++] = pins | (sample ? SAMPLE : 0) | ((uint32_t)delay << 8);
    s->pins = pins;
    if (sample)
        s->samples++;
}

double stream_latch_ns(const stream_t *s)
{
    return 0.45 * 1000.0 / s->mhz - 40.0;
}

void stream_cycle(stream_t *s, cycle_t kind, unsigned reg, double sample_ns, bool marker)
{
    const double period = 1000.0 / s->mhz, high = 0.45 * period, low = period - high;
    const uint32_t strobes = P_RESB | P_RB | P_WB;
    bool ours = kind == CYCLE_OUR_READ || kind == CYCLE_OUR_WRITE;
    bool read = kind == CYCLE_READ || kind == CYCLE_OUR_READ;
    uint32_t hold = strobes | (s->pins & (P_CS | P_ADDR));
    uint32_t addr = strobes | (ours ? addr_pins(reg) : (P_CS | (s->pins & P_ADDR)));
    uint32_t strobe = addr & ~(read ? P_RB : P_WB);
    long t_hold = clocks(s, 30), t_low = clocks(s, low), t_high = clocks(s, high);

    phase(s, hold, t_hold, false);
    phase(s, addr, t_low - t_hold, false);
    if (kind == CYCLE_OUR_READ && sample_ns >= 0) {
        long first = clocks(s, sample_ns) + 2;     // the sample is taken 2 clocks before its phase ends
        phase(s, strobe, first, true);
        phase(s, strobe, t_high - first, false);
    } else {
        phase(s, strobe, t_high, false);
    }
    if (kind == CYCLE_OUR_WRITE && marker)
        s->marker = true;
}

void stream_resb(stream_t *s, bool low, double ns)
{
    phase(s, (P_RB | P_WB | P_CS | (s->pins & P_ADDR)) | (low ? 0 : P_RESB), clocks(s, ns), false);
}

void exerciser_init(void)
{
    for (unsigned pin = FW_PIN_EXER_BASE; pin < FW_PIN_EXER_BASE + 7; pin++)
        pio_gpio_init(EX_PIO, pin);

    uint offset = pio_add_program(EX_PIO, &player_program);
    pio_sm_config c = player_program_get_default_config(offset);
    sm_config_set_out_pins(&c, FW_PIN_EXER_BASE, 7);
    sm_config_set_out_shift(&c, true, true, 32);
    sm_config_set_in_pin_base(&c, FW_PIN_D0);
    sm_config_set_in_shift(&c, false, false, 32);
    pio_sm_claim(EX_PIO, SM_PLAYER);
    pio_sm_init(EX_PIO, SM_PLAYER, offset, &c);
    pio_sm_set_pins_with_mask(EX_PIO, SM_PLAYER, P_IDLE << FW_PIN_EXER_BASE, 0x7Fu << FW_PIN_EXER_BASE);
    pio_sm_set_pindirs_with_mask(EX_PIO, SM_PLAYER, 0x7Fu << FW_PIN_EXER_BASE, 0x7Fu << FW_PIN_EXER_BASE);
    pio_sm_set_enabled(EX_PIO, SM_PLAYER, true);

    sampler_offset = pio_add_program(EX_PIO, &sampler_program);
    c = sampler_program_get_default_config(sampler_offset);
    sm_config_set_jmp_pin(&c, FW_PIN_CS);
    sm_config_set_in_pin_base(&c, FW_PIN_D0);
    sm_config_set_in_shift(&c, false, false, 32);
    // The delay goes in by the TX FIFO first; the samples come out by DMA.
    pio_sm_claim(EX_PIO, SM_SAMPLER);
    pio_sm_init(EX_PIO, SM_SAMPLER, sampler_offset, &c);

    dma_tx = dma_claim_unused_channel(true);
    dma_rx = dma_claim_unused_channel(true);
}

uint32_t exerciser_wires(uint32_t pins)
{
    // One phase, long enough to settle; the player holds its pins when it runs dry.
    static uint32_t word;
    word = (pins & 0x7Fu) | (100u << 8);
    while (!pio_sm_is_tx_fifo_empty(EX_PIO, SM_PLAYER))
        tight_loop_contents();
    pio_sm_put_blocking(EX_PIO, SM_PLAYER, word);
    busy_wait_us(20);
    return (gpio_get_all() >> FW_PIN_RESB) & 0x7Fu;
}

static void start_tx(const stream_t *s)
{
    dma_channel_config c = dma_channel_get_default_config((uint)dma_tx);
    channel_config_set_transfer_data_size(&c, DMA_SIZE_32);
    channel_config_set_read_increment(&c, true);
    channel_config_set_write_increment(&c, false);
    channel_config_set_dreq(&c, pio_get_dreq(EX_PIO, SM_PLAYER, true));
    channel_config_set_high_priority(&c, true);
    dma_channel_configure((uint)dma_tx, &c, &EX_PIO->txf[SM_PLAYER], s->words, s->count, true);
    // The player was stalled waiting for this stream, which set its stall flag:
    // clear it once the first words are in and it's running.
    busy_wait_us(1);
    EX_PIO->fdebug = 1u << (PIO_FDEBUG_TXSTALL_LSB + SM_PLAYER);
}

// Every stream ends with the pins idle (RESB, RB, WB and CS high), so whatever
// comes next starts from a quiet bus: a stream that ended in a read would leave
// RB and CS low, and the next to look at them would see a read that isn't there.
static void end_idle(void)
{
    pio_sm_put_blocking(EX_PIO, SM_PLAYER, P_IDLE | (20u << 8));
}

// Waits for the stream to finish. It ran late if the player stalled for want of
// a word while the DMA still had words to give it.
static bool finish_tx(void (*idle)(void), void (*poll)(void))
{
    bool late = false;
    const uint32_t stall = 1u << (PIO_FDEBUG_TXSTALL_LSB + SM_PLAYER);
    while (dma_channel_is_busy((uint)dma_tx)) {
        if ((EX_PIO->fdebug & stall) && dma_channel_is_busy((uint)dma_tx))
            late = true;
        if (poll)
            poll();
        if (idle)
            idle();
    }
    end_idle();
    // The last words drain from the FIFO, then the player stalls at the end.
    while (!(EX_PIO->fdebug & stall)) {
        if (poll)
            poll();
    }
    if (poll)
        poll();
    return !late;
}

bool exerciser_play(const stream_t *s, uint8_t *samples, void (*idle)(void))
{
    uint32_t n = s->samples < 1024 ? s->samples : 1024;
    pio_sm_clear_fifos(EX_PIO, SM_PLAYER);
    if (n) {
        dma_channel_config c = dma_channel_get_default_config((uint)dma_rx);
        channel_config_set_transfer_data_size(&c, DMA_SIZE_32);
        channel_config_set_read_increment(&c, false);
        channel_config_set_write_increment(&c, true);
        channel_config_set_dreq(&c, pio_get_dreq(EX_PIO, SM_PLAYER, false));
        dma_channel_configure((uint)dma_rx, &c, rx_words, &EX_PIO->rxf[SM_PLAYER], n, true);
    }
    start_tx(s);
    bool ok = finish_tx(idle, NULL);
    while (n && dma_channel_is_busy((uint)dma_rx))
        if (idle)
            idle();
    for (uint32_t i = 0; samples && i < n; i++)
        samples[i] = (uint8_t)rx_words[i];
    return ok;
}

static void (*live_cb)(uint32_t, uint8_t);
static uint32_t live_index;

static void live_poll(void)
{
    while (!pio_sm_is_rx_fifo_empty(EX_PIO, SM_PLAYER))
        live_cb(live_index++, (uint8_t)EX_PIO->rxf[SM_PLAYER]);
}

bool exerciser_play_live(const stream_t *s, void (*on_sample)(uint32_t index, uint8_t value), void (*idle)(void))
{
    pio_sm_clear_fifos(EX_PIO, SM_PLAYER);
    live_cb = on_sample;
    live_index = 0;
    start_tx(s);
    // No idle work while live: the CPU must answer each marker within a few
    // bus cycles.
    (void)idle;
    return finish_tx(NULL, live_poll);
}

// The pads' control registers written directly: the SDK's calls take about 20
// cycles each, and a release must be done long before the next read.
#define OVER_MASK (IO_BANK0_GPIO0_CTRL_OUTOVER_BITS | IO_BANK0_GPIO0_CTRL_OEOVER_BITS)

void exerciser_drive_data(uint8_t value)
{
    for (unsigned i = 0; i < 8; i++) {
        uint32_t ctrl = io_bank0_hw->io[FW_PIN_D0 + i].ctrl & ~OVER_MASK;
        uint32_t out = (value >> i) & 1 ? GPIO_OVERRIDE_HIGH : GPIO_OVERRIDE_LOW;
        io_bank0_hw->io[FW_PIN_D0 + i].ctrl = ctrl | (out << IO_BANK0_GPIO0_CTRL_OUTOVER_LSB) |
                                              (GPIO_OVERRIDE_HIGH << IO_BANK0_GPIO0_CTRL_OEOVER_LSB);
    }
}

void exerciser_release_data(void)
{
    for (unsigned i = 0; i < 8; i++)
        io_bank0_hw->io[FW_PIN_D0 + i].ctrl &= ~OVER_MASK;
}

size_t exerciser_sample_play(const stream_t *s, uint32_t delay_clocks, uint8_t *samples, size_t max, void (*idle)(void))
{
    pio_sm_set_enabled(EX_PIO, SM_SAMPLER, false);
    pio_sm_clear_fifos(EX_PIO, SM_SAMPLER);
    pio_sm_restart(EX_PIO, SM_SAMPLER);
    pio_sm_exec(EX_PIO, SM_SAMPLER, pio_encode_jmp(sampler_offset));
    pio_sm_put(EX_PIO, SM_SAMPLER, delay_clocks);
    pio_sm_set_enabled(EX_PIO, SM_SAMPLER, true);

    // The samples go straight to RAM by DMA: the CPU, held off by USB's
    // interrupts, can't be trusted to empty the FIFO before the next read.
    if (max > 1024)
        max = 1024;
    dma_channel_config c = dma_channel_get_default_config((uint)dma_rx);
    channel_config_set_transfer_data_size(&c, DMA_SIZE_32);
    channel_config_set_read_increment(&c, false);
    channel_config_set_write_increment(&c, true);
    channel_config_set_dreq(&c, pio_get_dreq(EX_PIO, SM_SAMPLER, false));
    dma_channel_configure((uint)dma_rx, &c, rx_words, &EX_PIO->rxf[SM_SAMPLER], max, true);

    pio_sm_clear_fifos(EX_PIO, SM_PLAYER);
    start_tx(s);
    while (dma_channel_is_busy((uint)dma_tx))
        if (idle)
            idle();
    end_idle();
    while (!pio_sm_is_tx_fifo_empty(EX_PIO, SM_PLAYER))
        if (idle)
            idle();
    busy_wait_us(5);
    size_t n = max - dma_channel_hw_addr((uint)dma_rx)->transfer_count;
    dma_channel_abort((uint)dma_rx);
    pio_sm_set_enabled(EX_PIO, SM_SAMPLER, false);
    for (size_t i = 0; i < n; i++)
        samples[i] = (uint8_t)rx_words[i];
    return n;
}

#endif
