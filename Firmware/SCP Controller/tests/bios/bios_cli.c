// The BIOS harness from the command line: boots a ROM against the controller,
// types BASIC lines at it and prints the console.
//
//   bios_cli ROM [options] [LINE ...]
//     --mhz N            the clock, 1 or 2 (default 1)
//     --sd FILE          an SD card holding FILE's bytes (a cffs image, say)
//     --sd-blank MB      a blank SD card of MB megabytes
//     --sd-out FILE      write the SD card's bytes to FILE at the end
//     --flash MB         the built-in drive's size (default 16; 0 for none)
//     --flash-out FILE   write the built-in drive's sectors, as the 6502 sees them, to FILE
//     --sd-timing T      typical, sdhc-worst or sdxc-worst
//     --flash-timing T   typical or worst
//
// Each LINE is typed and the BASIC prompt waited for. The exit status is 1 if
// the machine never reached the prompt, or a line never got one back.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "machine.h"

static uint8_t *slurp(const char *path, size_t *len)
{
    FILE *f = fopen(path, "rb");
    if (!f) {
        perror(path);
        exit(2);
    }
    fseek(f, 0, SEEK_END);
    *len = (size_t)ftell(f);
    fseek(f, 0, SEEK_SET);
    uint8_t *p = malloc(*len ? *len : 1);
    if (fread(p, 1, *len, f) != *len) {
        perror(path);
        exit(2);
    }
    fclose(f);
    return p;
}

static void spill(const char *path, const uint8_t *p, size_t len)
{
    FILE *f = fopen(path, "wb");
    if (!f || fwrite(p, 1, len, f) != len) {
        perror(path);
        exit(2);
    }
    fclose(f);
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: bios_cli ROM [options] [LINE ...]\n");
        return 2;
    }
    size_t rom_len;
    uint8_t *rom = slurp(argv[1], &rom_len);
    if (rom_len != 0x8000) {
        fprintf(stderr, "%s: a ROM is 32768 bytes, not %zu\n", argv[1], rom_len);
        return 2;
    }
    machine_config_t cfg = { .mhz = 1, .rom = rom, .flash_bytes = 16u << 20, .boot_us = 250000 };
    const char *sd_out = NULL, *flash_out = NULL;
    uint8_t *image = NULL;
    int i = 2;
    for (; i < argc && strncmp(argv[i], "--", 2) == 0; i += 2) {
        const char *opt = argv[i], *val = i + 1 < argc ? argv[i + 1] : "";
        if (!strcmp(opt, "--mhz")) cfg.mhz = atof(val);
        else if (!strcmp(opt, "--sd")) {
            size_t len;
            image = slurp(val, &len);
            cfg.sd_sectors = (uint32_t)(len / 512);
        } else if (!strcmp(opt, "--sd-blank")) cfg.sd_sectors = (uint32_t)atoi(val) * 2048u;
        else if (!strcmp(opt, "--sd-out")) sd_out = val;
        else if (!strcmp(opt, "--flash")) cfg.flash_bytes = (uint32_t)atoi(val) << 20;
        else if (!strcmp(opt, "--flash-out")) flash_out = val;
        else if (!strcmp(opt, "--sd-timing"))
            cfg.sd_timing = !strcmp(val, "sdhc-worst") ? &SD_SDHC_WORST : !strcmp(val, "sdxc-worst") ? &SD_SDXC_WORST : &SD_TYPICAL;
        else if (!strcmp(opt, "--flash-timing"))
            cfg.flash_timing = !strcmp(val, "worst") ? &FLASH_WORST : &FLASH_TYPICAL;
        else {
            fprintf(stderr, "unknown option %s\n", opt);
            return 2;
        }
    }

    machine_t *m = machine_new(&cfg, image);
    int status = 0;
    if (!machine_wait(m, 0, "\r\nOK\r\n", 10)) {
        fputs(m->out, stdout);
        fprintf(stderr, "\nbios_cli: no prompt after 10 s\n");
        return 1;
    }
    fputs(m->out, stdout);
    for (; i < argc; i++) {
        static char buf[1 << 15], line[512];
        // "\r" in an argument is a Return: "FORMAT\rY" answers FORMAT's question.
        size_t n = 0;
        for (const char *p = argv[i]; *p && n < sizeof line - 1; p++) {
            if (p[0] == '\\' && p[1] == 'r') {
                line[n++] = '\r';
                p++;
            } else {
                line[n++] = *p;
            }
        }
        line[n] = 0;
        bool ok = machine_command(m, line, buf, sizeof buf, 10);
        fputs(buf, stdout);
        if (!ok) {
            fprintf(stderr, "\nbios_cli: no prompt after \"%s\"\n", argv[i]);
            status = 1;
            break;
        }
    }
    fflush(stdout);
    if (sd_out)
        spill(sd_out, m->sd.data, (size_t)cfg.sd_sectors * 512);
    if (flash_out && cfg.flash_bytes) {
        uint8_t sector[512];
        FILE *f = fopen(flash_out, "wb");
        for (uint32_t s = 0; f && s < cfg.flash_bytes / 512; s++) {
            m->flash.medium.read(&m->flash.medium, s, sector);
            fwrite(sector, 1, 512, f);
        }
        if (f)
            fclose(f);
    }
    fprintf(stderr, "bios_cli: %.3f s of machine time, %zu jobs, longest busy %u us\n",
            machine_us(m) / 1e6, m->job_count, machine_longest(m, 0, 0));
    machine_free(m);
    free(image);
    free(rom);
    return status;
}
