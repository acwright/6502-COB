#include "drive.h"

#include <string.h>

#include "identify.h"

void drive_init(drive_t *d, ata_t *ata, medium_t *sd, medium_t *flash,
                uint32_t (*now_us)(void *clock), void *clock,
                const char *model, const char *serial, const char *firmware)
{
    memset(d, 0, sizeof *d);
    d->ata = ata;
    d->sd = sd;
    d->flash = flash;
    d->now_us = now_us;
    d->clock = clock;
    d->model = model;
    d->serial = serial;
    d->firmware = firmware;
}

static bool ready(medium_t *m)
{
    return m && m->ready(m);
}

medium_t *drive_choose(drive_t *d)
{
    if (ready(d->sd))
        return d->sd;
    if (ready(d->flash))
        return d->flash;
    return NULL;
}

static uint8_t outcome(medium_result_t r)
{
    switch (r) {
    case MEDIUM_OK: return 0;
    case MEDIUM_GONE: return ATA_ER_ABRT;
    default: return ATA_ER_UNC;
    }
}

static uint8_t sector_job(medium_t *m, uint8_t op, uint32_t lba, uint8_t *buf)
{
    uint32_t sector;
    if (!media_map(m->sectors(m), lba, &sector))
        return ATA_ER_IDNF | ATA_ER_ABRT;
    switch (op) {
    case ATA_JOB_READ:
        return outcome(m->read(m, sector, buf));
    case ATA_JOB_ERASE:
        memset(buf, 0, ATA_SECTOR);
        return outcome(m->write(m, sector, buf));
    default:
        return outcome(m->write(m, sector, buf));
    }
}

static void identify(drive_t *d, medium_t *m)
{
    identify_t id = {
        .model = d->model,
        .serial = d->serial,
        .firmware = d->firmware,
        .sectors = media_disks(m->sectors(m)) * MEDIA_DISK_SECTORS,
        .longest_busy_us = d->stats.longest_busy_us,
        .longest_sd_write_us = d->stats.sd.longest_write_us,
        .longest_flash_write_us = d->stats.flash.longest_write_us,
        .medium = m == d->sd ? IDENTIFY_MEDIUM_SD : IDENTIFY_MEDIUM_FLASH,
        .disks = (uint16_t)media_disks(m->sectors(m)),
        .errors = d->stats.errors,
    };
    identify_build(d->ata->buffer, &id);
}

static void record(drive_t *d, medium_t *m, uint8_t op, uint8_t error, uint32_t us)
{
    if (us > d->stats.longest_busy_us)
        d->stats.longest_busy_us = us;
    if (error)
        d->stats.errors++;
    if (!m || op == ATA_JOB_IDENTIFY)
        return;
    drive_medium_stats_t *s = m == d->sd ? &d->stats.sd : &d->stats.flash;
    if (error)
        s->errors++;
    if (op == ATA_JOB_READ) {
        s->reads++;
        if (us > s->longest_read_us)
            s->longest_read_us = us;
    } else {
        s->writes++;
        if (us > s->longest_write_us)
            s->longest_write_us = us;
    }
}

bool drive_service(drive_t *d)
{
    ata_job_t *job = ata_job_begin(d->ata);
    if (!job)
        return false;
    uint32_t start = d->now_us(d->clock);
    d->busy = true;

    if (job->first) {
        d->current = drive_choose(d);
        d->current_generation = d->current ? d->current->generation : 0;
    }
    medium_t *m = d->current;
    uint8_t error;
    if (!m)
        error = ATA_ER_AMNF;            // nothing to answer with
    else if (!m->ready(m) || m->generation != d->current_generation)
        error = ATA_ER_ABRT;            // the command's medium went mid-command, or was swapped
    else if (job->op == ATA_JOB_IDENTIFY) {
        identify(d, m);
        error = 0;
    } else
        error = sector_job(m, job->op, job->lba, d->ata->buffer);

    uint32_t end = d->now_us(d->clock);
    record(d, m, job->op, error, end - start);
    d->busy = false;
    d->active = true;
    d->last_end_us = end;
    ata_job_end(d->ata, error);
    return true;
}

bool drive_boot_settled(bool card_in, bool sd_ready, bool sd_failed, uint32_t elapsed_ms)
{
    return !card_in || sd_ready || sd_failed || elapsed_ms >= DRIVE_BOOT_SD_WAIT_MS;
}

drive_leds_t drive_leds(const drive_t *d, uint32_t now_us)
{
    drive_leds_t leds;
    leds.sd = ready(d->sd);
    leds.act = d->busy || (d->active && now_us - d->last_end_us < DRIVE_ACT_HOLD_US);
    return leds;
}
