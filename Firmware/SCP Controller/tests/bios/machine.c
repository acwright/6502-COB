#include "machine.h"

#include "product.h"
#include "version.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Typical and worst-case costs. The SD card's are the SD specification's limits
// (100 ms to read, 250 ms to write on SDHC, 500 ms on SDXC) and a few ms
// typical; the chip's are the W25Q128JV datasheet's (page program 0.4 ms typical,
// 3 ms most; 4 KB erase 45 ms typical, 400 ms most) and a read at about 0.21 us
// a byte (SPI at about 37.5 MHz).
const media_timing_t SD_TYPICAL    = { "SD typical",     800,    3000,   0,    0,      0 };
const media_timing_t SD_SDHC_WORST = { "SDHC worst",     100000, 250000, 0,    0,      0 };
const media_timing_t SD_SDXC_WORST = { "SDXC worst",     100000, 500000, 0,    0,      0 };
const media_timing_t FLASH_TYPICAL = { "flash typical",  0,      0,      400,  45000,  21 };
const media_timing_t FLASH_WORST   = { "flash worst",    0,      0,      3000, 400000, 21 };

// vrEmu6502 calls back with no context: one machine at a time.
static machine_t *M;

uint64_t machine_cycles_for_us(const machine_t *m, uint64_t us)
{
    return (uint64_t)((double)us * m->cfg.mhz);
}

double machine_us(const machine_t *m)
{
    return (double)m->cycles / m->cfg.mhz;
}

// --- The controller's timeline ----------------------------------------------
//
// The bus side (ata.c) answers at once. When it posts a job, the worker does it
// here on the media models, which move the clock on by what the job costs; the
// bus side may see the result only once the machine has run that long.

static void storage_tick(machine_t *m)
{
    if (!m->present && m->cycles >= m->present_at) {
        m->present = true;
        ata_set_present(&m->ata, drive_choose(&m->drive) != NULL);
    }
    if (!m->job_out && atomic_load(&m->ata.job.state) == ATA_JOB_POSTED) {
        uint8_t op = m->ata.job.op;
        m->clock.us = (uint32_t)machine_us(m);
        uint32_t start = m->clock.us;
        drive_service(&m->drive);
        m->job_ready = m->cycles + machine_cycles_for_us(m, m->clock.us - start);
        m->job_out = true;
        if (m->job_count < sizeof m->jobs / sizeof m->jobs[0])
            m->jobs[m->job_count++] = (job_log_t){
                op, m->drive.current == &m->sd.medium, m->ata.job.error, m->clock.us - start
            };
    }
    if (m->job_out && m->cycles >= m->job_ready) {
        m->job_out = false;
        ata_poll(&m->ata);
    }
}

// --- A rig's controller ---------------------------------------------------------
//
// A data register read fetches the rest of the sector in one round trip, and the
// 6502's next reads of it are handed out from that. Any other access with bytes
// still unread would be the 6502 leaving a sector part read, which the BIOS
// never does: they're counted as strays, and thrown away.

static void rig_drop_data(machine_t *m)
{
    m->rig_strays += (uint32_t)(m->rig_data_len - m->rig_data_pos);
    m->rig_data_len = m->rig_data_pos = 0;
}

static uint8_t rig_storage_read(machine_t *m, unsigned reg)
{
    if (reg == ATA_REG_DATA) {
        if (m->rig_data_pos == m->rig_data_len) {
            m->rig_data_len = rig_data(m->cfg.rig, m->rig_data, sizeof m->rig_data);
            m->rig_data_pos = 0;
            if (!m->rig_data_len)
                return 0;
        }
        return m->rig_data[m->rig_data_pos++];
    }
    rig_drop_data(m);
    return rig_read(m->cfg.rig, reg);
}

static void rig_storage_write(machine_t *m, unsigned reg, uint8_t v)
{
    rig_drop_data(m);
    rig_write(m->cfg.rig, reg, v);
}

// --- The serial card ---------------------------------------------------------

#define SC_CMD_DTR  0x01
#define SC_CMD_IRD  0x02            // receiver interrupt disabled
#define SC_CMD_TIC  0x0C            // 00: transmitter off, RTSB high
#define SC_ST_RDRF  0x08
#define SC_ST_TDRE  0x10
#define SC_ST_IRQ   0x80

static void serial_tick(machine_t *m)
{
    // 19200 baud: a byte every 521 us. A byte goes in only while the BIOS holds
    // RTS low, as a terminal doing RTS/CTS sends.
    if (m->input && m->input[m->input_pos] && !m->acia_rx_full && (m->acia_cmd & SC_CMD_DTR) &&
        (m->acia_cmd & SC_CMD_TIC) && m->cycles >= m->next_rx) {
        m->acia_rx = (uint8_t)m->input[m->input_pos++];
        m->acia_rx_full = true;
        if (!(m->acia_cmd & SC_CMD_IRD))
            m->acia_irq = true;
        m->next_rx = m->cycles + machine_cycles_for_us(m, 521);
    }
    *vrEmu6502Int(m->cpu) = m->acia_irq ? IntRequested : IntCleared;
}

static uint8_t serial_read(machine_t *m, uint16_t reg, bool dbg)
{
    switch (reg & 3) {
    case 0:
        if (!dbg) {
            m->acia_rx_full = false;
            m->acia_irq = false;
        }
        return m->acia_rx;
    case 1: {
        uint8_t s = (uint8_t)(SC_ST_TDRE | (m->acia_rx_full ? SC_ST_RDRF : 0) | (m->acia_irq ? SC_ST_IRQ : 0));
        if (!dbg)
            m->acia_irq = false;
        return s;
    }
    case 2: return m->acia_cmd;
    default: return m->acia_ctrl;
    }
}

static void serial_write(machine_t *m, uint16_t reg, uint8_t v)
{
    switch (reg & 3) {
    case 0:
        // A terminal shows nothing for $00, and here it would end the string the
        // tests search: a DIR of a directory holding junk prints names with $00 in them.
        if (v == 0)
            break;
        if (m->out_len < sizeof m->out - 1) {
            m->out[m->out_len++] = (char)v;
            m->out[m->out_len] = 0;
        }
        break;
    case 1: m->acia_cmd &= 0xE0; break;     // programmed reset
    case 2: m->acia_cmd = v; break;
    default: m->acia_ctrl = v; break;
    }
}

// --- The bus -------------------------------------------------------------------

static uint8_t mem_read(uint16_t addr, bool dbg)
{
    machine_t *m = M;
    uint8_t v;
    if (addr < 0x8000) {
        v = m->ram[addr];
    } else if (addr < 0xA000) {
        unsigned slot = (addr - 0x8000) >> 10;
        if (slot == 3 && m->cfg.rig) {
            if (dbg)
                return 0;
            v = rig_storage_read(m, addr & 7);
        } else if (slot == 3) {
            if (dbg)
                return ata_peek(&m->ata, addr & 7);
            storage_tick(m);
            v = ata_read(&m->ata, addr & 7);
        } else if (slot == 4) {
            v = serial_read(m, addr, dbg);
        } else {
            v = m->bus;                     // an empty slot: open bus
        }
    } else {
        v = m->cfg.rom[addr - 0x8000];
    }
    if (!dbg)
        m->bus = v;
    return v;
}

static void mem_write(uint16_t addr, uint8_t v)
{
    machine_t *m = M;
    m->bus = v;
    if (addr < 0x8000) {
        m->ram[addr] = v;
    } else if (addr < 0xA000) {
        unsigned slot = (addr - 0x8000) >> 10;
        if (slot == 3 && m->cfg.rig) {
            rig_storage_write(m, addr & 7, v);
        } else if (slot == 3) {
            storage_tick(m);
            ata_write(&m->ata, addr & 7, v);
        } else if (slot == 4) {
            serial_write(m, addr, v);
        }
    }
}

// --- The machine -----------------------------------------------------------------

static void apply_timing(machine_t *m)
{
    const media_timing_t *sd = m->cfg.sd_timing ? m->cfg.sd_timing : &SD_TYPICAL;
    const media_timing_t *fl = m->cfg.flash_timing ? m->cfg.flash_timing : &FLASH_TYPICAL;
    m->sd.read_us = sd->read_us;
    m->sd.write_us = sd->write_us;
    m->chip.program_us = fl->program_us;
    m->chip.erase_us = fl->erase_us;
    m->chip.read_byte_us_x100 = fl->byte_us_x100;
}

machine_t *machine_new(const machine_config_t *cfg, const uint8_t *sd_image)
{
    machine_t *m = calloc(1, sizeof *m);
    m->cfg = *cfg;
    M = m;
    m->cpu = vrEmu6502New(CPU_W65C02, mem_read, mem_write);

    if (cfg->rig) {
        rig_power_on(cfg->rig, cfg->sd_sectors != 0);
        m->cfg.sd_sectors = 0;              // the rig's media, not these models
    }
    cfg = &m->cfg;
    ram_init(&m->sd, cfg->sd_sectors ? cfg->sd_sectors : 1);
    m->sd.in = m->sd.started = cfg->sd_sectors != 0;
    m->sd.clock = &m->clock;
    if (sd_image && cfg->sd_sectors)
        memcpy(m->sd.data, sd_image, (size_t)cfg->sd_sectors * 512);
    fnor_init(&m->chip, cfg->flash_bytes ? cfg->flash_bytes : NOR_SECTOR);
    if (!cfg->flash_bytes)
        m->chip.nor.size = 0;
    m->chip.clock = &m->clock;
    flashdisk_init(&m->flash, &m->chip.nor);
    apply_timing(m);

    ata_init(&m->ata);
    drive_init(&m->drive, &m->ata, &m->sd.medium, &m->flash.medium, fake_now, &m->clock,
               PRODUCT_MODEL, "HARNESS", FW_VERSION);

    // Power-on: the RP2350 starts; with a card in, it waits for the card to start
    // (or fail, or the 1.2 s to run out) before answering.
    uint32_t settle = cfg->boot_us;
    if (cfg->sd_sectors) {
        const uint32_t wait = DRIVE_BOOT_SD_WAIT_MS * 1000u;
        uint32_t start = cfg->sd_start_us < wait ? cfg->sd_start_us : wait;
        if (cfg->sd_start_fails || cfg->sd_start_us > wait)
            m->sd.started = false;          // failed, or given up on: the built-in drive answers
        settle += start;
    }
    m->present_at = machine_cycles_for_us(m, settle);

    vrEmu6502Reset(m->cpu);
    return m;
}

void machine_free(machine_t *m)
{
    vrEmu6502Destroy(m->cpu);
    ram_free(&m->sd);
    fnor_free(&m->chip);
    if (M == m)
        M = NULL;
    free(m);
}

static void step(machine_t *m)
{
    serial_tick(m);
    m->cycles += vrEmu6502InstCycle(m->cpu);
    if (m->job_out && m->cycles >= m->job_ready)
        storage_tick(m);
}

size_t machine_wait(machine_t *m, size_t from, const char *want, double seconds)
{
    M = m;
    uint64_t end = m->cycles + (uint64_t)(seconds * 1e6 * m->cfg.mhz);
    size_t len = strlen(want);
    while (m->cycles < end) {
        for (int i = 0; i < 64; i++)
            step(m);
        if (m->out_len >= from + len) {
            char *hit = strstr(m->out + from, want);
            if (hit)
                return (size_t)(hit - m->out) + len;
        }
    }
    return 0;
}

void machine_type(machine_t *m, const char *text)
{
    m->input = text;
    m->input_pos = 0;
}

// Runs the machine until everything typed has gone in.
static bool drain(machine_t *m, double seconds)
{
    uint64_t end = m->cycles + (uint64_t)(seconds * 1e6 * m->cfg.mhz);
    while (m->input && m->input[m->input_pos] && m->cycles < end)
        machine_wait(m, m->out_len, "\x01", 0.001);
    return !m->input || !m->input[m->input_pos];
}

bool machine_command(machine_t *m, const char *line, char *buf, size_t size, double seconds)
{
    static char typed[512];
    // A line holding a CR already is typed as it is: "FORMAT\rY" answers the
    // question with a key and no Return.
    snprintf(typed, sizeof typed, strchr(line, '\r') ? "%s" : "%s\r", line);
    size_t from = m->out_len;
    machine_type(m, typed);
    size_t end;
    if (line[0] >= '0' && line[0] <= '9') {
        // A program line is stored without a prompt: done once it has gone in,
        // echoed, and the machine has had 20 ms to store it.
        end = drain(m, seconds) ? machine_wait(m, from, "\r\n", seconds) : 0;
        if (end)
            machine_wait(m, m->out_len, "\x01", 0.02), end = m->out_len;
    } else {
        // The prompt counts only once the whole line has gone in.
        end = drain(m, seconds) ? machine_wait(m, from, "\r\nOK\r\n", seconds) : 0;
    }
    if (buf && size) {
        size_t n = (end ? end : m->out_len) - from;
        if (n >= size)
            n = size - 1;
        memcpy(buf, m->out + from, n);
        buf[n] = 0;
    }
    return end != 0;
}

uint8_t machine_peek(const machine_t *m, uint16_t addr)
{
    return addr < 0x8000 ? m->ram[addr] : (addr >= 0xA000 ? m->cfg.rom[addr - 0x8000] : 0);
}

void machine_controller(machine_t *m, machine_controller_t *c)
{
    memset(c, 0, sizeof *c);
    if (m->cfg.rig) {
        uint32_t w[SERVE_STAT_COUNT];
        rig_stats(m->cfg.rig, w);
        c->drive.sd = (drive_medium_stats_t){ w[SERVE_STAT_SD_READS], w[SERVE_STAT_SD_WRITES], w[SERVE_STAT_SD_ERRORS],
                                              w[SERVE_STAT_SD_LONGEST_READ_US], w[SERVE_STAT_SD_LONGEST_WRITE_US] };
        c->drive.flash = (drive_medium_stats_t){ w[SERVE_STAT_FLASH_READS], w[SERVE_STAT_FLASH_WRITES],
                                                 w[SERVE_STAT_FLASH_ERRORS], w[SERVE_STAT_FLASH_LONGEST_READ_US],
                                                 w[SERVE_STAT_FLASH_LONGEST_WRITE_US] };
        c->drive.longest_busy_us = w[SERVE_STAT_LONGEST_BUSY_US];
        c->drive.errors = w[SERVE_STAT_ERRORS];
        c->settle_ms = w[SERVE_STAT_SETTLE_MS];
        c->sd_disks = w[SERVE_STAT_SD_DISKS];
        c->flash_disks = w[SERVE_STAT_FLASH_DISKS];
        c->sd_led = w[SERVE_STAT_SD_LED] != 0;
        c->has_sd = w[SERVE_STAT_HAS_SD] != 0;
        c->late = w[SERVE_STAT_LATE];
        return;
    }
    c->drive = m->drive.stats;
    c->settle_ms = (uint32_t)(m->present_at / (uint64_t)(m->cfg.mhz * 1000));
    c->sd_disks = m->sd.medium.ready(&m->sd.medium) ? media_disks(m->sd.medium.sectors(&m->sd.medium)) : 0;
    c->flash_disks = media_disks(m->flash.medium.sectors(&m->flash.medium));
    c->sd_led = drive_leds(&m->drive, (uint32_t)machine_us(m)).sd;
    c->has_sd = true;
}

void machine_set_card(machine_t *m, bool in)
{
    if (m->cfg.rig) {
        rig_card(m->cfg.rig, in);
        return;
    }
    if (in && !m->sd.in)
        m->sd.medium.generation++;
    m->sd.in = m->sd.started = in;
}

uint32_t machine_longest(const machine_t *m, size_t from, uint8_t op)
{
    uint32_t longest = 0;
    for (size_t i = from; i < m->job_count; i++)
        if ((!op || m->jobs[i].op == op) && m->jobs[i].busy_us > longest)
            longest = m->jobs[i].busy_us;
    return longest;
}
