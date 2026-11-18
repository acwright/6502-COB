#include "bus.h"

#include <stdatomic.h>

#include "hardware/gpio.h"
#include "hardware/pio.h"
#include "hardware/structs/pio.h"
#include "hardware/clocks.h"
#include "hardware/structs/systick.h"
#include "pico/multicore.h"

#include "bus.pio.h"

#if FW_HAS_BUS

// bus.pio has these pins written into it.
_Static_assert(FW_PIN_D0 == 0 && FW_PIN_RESB == 8 && FW_PIN_RB == 9 && FW_PIN_WB == 10 && FW_PIN_CS == 11 &&
               FW_PIN_A2 == 12 && FW_PIN_A1 == 13 && FW_PIN_A0 == 14, "bus.pio's pin numbers");

#define BUS_PIO   pio0
#define SM_READ   0
#define SM_NOTE   1
#define SM_WRITE  2

static ata_t *bus_ata;
static atomic_int present_request = -1;     // -1 none; 0 or 1 from bus_set_present()
static bus_stats_t stats;
static uint32_t shadow[4];

// A2, A1, A0 arrive on GPIO12, 13, 14: bit 0 is A2. The register is A2:A1:A0.
static inline unsigned reg_of(uint32_t bits)
{
    return ((bits & 1) << 2) | (bits & 2) | ((bits >> 2) & 1);
}

// Rewrites the four words bus_read serves from. Word w is A1:A2 = w, so it holds
// registers A2 = w bit 0, A1 = w bit 1: A0 = 0 in bits 0-7, A0 = 1 in bits 8-15.
static void __not_in_flash_func(publish)(const ata_t *a)
{
    uint8_t regs[8];
    ata_registers(a, regs);
    for (unsigned w = 0; w < 4; w++) {
        unsigned base = ((w & 1) << 2) | (w & 2);
        uint32_t v = regs[base] | ((uint32_t)regs[base + 1] << 8);
        if (v != shadow[w]) {
            BUS_PIO->rxf_putget[SM_READ][w] = v;
            shadow[w] = v;
        }
    }
}

// Core 1's SysTick counts its clock cycles down from 2^24 - 1, for timing the loop.
static inline uint32_t cycles_now(void)
{
    return systick_hw->cvr;
}

// Every register reads BSY: the moment a command or a sector's last byte is taken.
static inline void publish_busy(void)
{
    for (unsigned w = 0; w < 4; w++) {
        BUS_PIO->rxf_putget[SM_READ][w] = ATA_SR_BSY | (ATA_SR_BSY << 8);
        shadow[w] = ATA_SR_BSY | (ATA_SR_BSY << 8);
    }
}

static void __not_in_flash_func(core1_loop)(void)
{
    ata_t *a = bus_ata;
    systick_hw->rvr = 0xFFFFFF;
    systick_hw->cvr = 0;
    systick_hw->csr = 0x5;                  // enabled, the processor's clock, no interrupt
    const uint32_t mhz = clock_get_hz(clk_sys) / 1000000u;
    bool resb_low = !gpio_get(FW_PIN_RESB);
    if (resb_low)
        ata_resb(a, true);
    publish(a);
    for (;;) {
        bool changed = false;
        bool timed = false, was_write = false;
        uint32_t t_op = 0, t_poll = 0;
        uint32_t taken = 0;
        if (!pio_sm_is_rx_fifo_empty(BUS_PIO, SM_WRITE)) {
            taken = cycles_now();
            timed = true;
            was_write = true;
            uint32_t e = BUS_PIO->rxf[SM_WRITE];
            unsigned reg = reg_of(e >> 12);
            if (ata_write_may_busy(a, reg))
                publish_busy();
            ata_write(a, reg, (uint8_t)e);
            stats.writes++;
            t_op = cycles_now();
            // A data byte in the middle of a sector changes nothing a read can see.
            changed = !(reg == ATA_REG_DATA && ata_mid_sector(a));
        } else if (!pio_sm_is_rx_fifo_empty(BUS_PIO, SM_NOTE)) {
            taken = cycles_now();
            timed = true;
            uint32_t e = BUS_PIO->rxf[SM_NOTE];
            unsigned reg = reg_of(e);
            ata_read(a, reg);
            stats.reads++;
            if (reg == ATA_REG_DATA && ata_mid_sector(a)) {
                // In the middle of a sector only the next data byte changes: put it
                // out first, before anything else.
                uint32_t v = ata_data_word(a);
                BUS_PIO->rxf_putget[SM_READ][0] = v;
                shadow[0] = v;
            } else {
                changed = true;
            }
            t_op = cycles_now();
            if (!changed) {
                uint32_t ns = ((taken - t_op) & 0xFFFFFF) * 1000u / mhz;
                if (ns > stats.longest_read_ns)
                    stats.longest_read_ns = ns;
                unsigned bucket = 0;
                for (uint32_t limit = 250; bucket < 7 && ns >= limit; limit *= 2)
                    bucket++;
                stats.histogram[bucket]++;
            }
        }
        bool low = !gpio_get(FW_PIN_RESB);
        if (low != resb_low) {
            resb_low = low;
            ata_resb(a, low);
            stats.resets += low;
            changed = true;
        }
        int p = atomic_exchange_explicit(&present_request, -1, memory_order_acquire);
        if (p >= 0) {
            ata_set_present(a, p != 0);
            changed = true;
        }
        bool before = a->waiting || a->resetting;
        ata_poll(a);
        if (before && !(a->waiting || a->resetting))
            changed = true;
        t_poll = cycles_now();
        if (changed) {
            publish(a);
            if (timed) {
                uint32_t t_pub = cycles_now();
                uint32_t sec[3] = { (taken - t_op) & 0xFFFFFF, (t_op - t_poll) & 0xFFFFFF, (t_poll - t_pub) & 0xFFFFFF };
                for (int i = 0; i < 3; i++)
                    if (sec[i] > stats.section_cycles[i])
                        stats.section_cycles[i] = sec[i];
            }
            if (timed) {
                uint32_t ns = ((taken - cycles_now()) & 0xFFFFFF) * 1000u / mhz;
                if (ns > stats.longest_ns)
                    stats.longest_ns = ns;
                uint32_t *longest = was_write ? &stats.longest_write_ns : &stats.longest_read_ns;
                if (ns > *longest)
                    *longest = ns;
                unsigned bucket = 0;
                for (uint32_t limit = 250; bucket < 7 && ns >= limit; limit *= 2)
                    bucket++;
                stats.histogram[bucket]++;
            }
        }
    }
}

static void program(uint sm, const pio_program_t *prog, pio_sm_config (*config)(uint), void (*setup)(pio_sm_config *))
{
    uint offset = pio_add_program(BUS_PIO, prog);
    pio_sm_config c = config(offset);
    setup(&c);
    pio_sm_claim(BUS_PIO, sm);
    pio_sm_init(BUS_PIO, sm, offset, &c);
}

static void setup_read(pio_sm_config *c)
{
    sm_config_set_in_pin_base(c, FW_PIN_A2);
    sm_config_set_in_pin_count(c, 2);
    sm_config_set_jmp_pin(c, FW_PIN_A0);
    sm_config_set_out_pins(c, FW_PIN_D0, 8);
    sm_config_set_out_shift(c, true, false, 32);
    sm_config_set_fifo_join(c, PIO_FIFO_JOIN_TXGET);
}

static void setup_note(pio_sm_config *c)
{
    sm_config_set_in_pin_base(c, FW_PIN_A2);
    sm_config_set_jmp_pin(c, FW_PIN_CS);
    sm_config_set_in_shift(c, false, false, 32);
    sm_config_set_fifo_join(c, PIO_FIFO_JOIN_RX);
}

static void setup_write(pio_sm_config *c)
{
    sm_config_set_in_pin_base(c, FW_PIN_D0);
    sm_config_set_jmp_pin(c, FW_PIN_CS);
    sm_config_set_in_shift(c, false, false, 32);
    sm_config_set_fifo_join(c, PIO_FIFO_JOIN_RX);
}

void bus_start(ata_t *a)
{
    bus_ata = a;
    // Every read answers BSY until the core says otherwise.
    for (unsigned w = 0; w < 4; w++)
        shadow[w] = 0xFFFFFFFF;

    for (unsigned pin = FW_PIN_RESB; pin <= FW_PIN_A0; pin++) {
        gpio_init(pin);
        gpio_disable_pulls(pin);
    }
    for (unsigned pin = FW_PIN_D0; pin < FW_PIN_D0 + 8; pin++) {
        pio_gpio_init(BUS_PIO, pin);
#if FW_BUS_INTERNAL_PULLS
        // No 4.7k resistors on a bare Pico 2: the pad's own pulls stand in, D7
        // up and D0-D6 down, so an undriven read is $80 as on the board.
        gpio_set_pulls(pin, pin == FW_PIN_D0 + 7, pin != FW_PIN_D0 + 7);
#else
        gpio_disable_pulls(pin);
#endif
    }
    pio_sm_set_consecutive_pindirs(BUS_PIO, SM_READ, FW_PIN_D0, 8, false);

    program(SM_READ, &bus_read_program, bus_read_program_get_default_config, setup_read);
    program(SM_NOTE, &bus_note_program, bus_note_program_get_default_config, setup_note);
    program(SM_WRITE, &bus_write_program, bus_write_program_get_default_config, setup_write);
    for (unsigned w = 0; w < 4; w++)
        BUS_PIO->rxf_putget[SM_READ][w] = ATA_SR_BSY | (ATA_SR_BSY << 8);

    multicore_launch_core1(core1_loop);
    pio_set_sm_mask_enabled(BUS_PIO, (1u << SM_READ) | (1u << SM_NOTE) | (1u << SM_WRITE), true);
}

void bus_bench(uint32_t cycles[3])
{
    static volatile uint32_t sink[4];
    (void)sink;
    systick_hw->rvr = 0xFFFFFF;
    systick_hw->cvr = 0;
    systick_hw->csr = 0x5;
    uint32_t t = cycles_now();
    uint32_t acc = 0;
    uint8_t regs[8];
    for (int i = 0; i < 1000; i++) {
        ata_registers(bus_ata, regs);
        acc += regs[i & 7];
    }
    cycles[0] = (t - cycles_now()) & 0xFFFFFF;
    t = cycles_now();
    for (int i = 0; i < 1000; i++)
        for (unsigned w = 0; w < 4; w++)
            BUS_PIO->rxf_putget[SM_READ][w] = shadow[w];
    cycles[1] = (t - cycles_now()) & 0xFFFFFF;
    t = cycles_now();
    for (int i = 0; i < 1000; i++)
        for (unsigned w = 0; w < 4; w++)
            sink[w] = shadow[w] + acc;
    cycles[2] = (t - cycles_now()) & 0xFFFFFF;
}

void bus_set_present(bool present)
{
    atomic_store_explicit(&present_request, present ? 1 : 0, memory_order_release);
}

bus_stats_t bus_stats(void)
{
    return stats;
}

#endif
