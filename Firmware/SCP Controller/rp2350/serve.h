// The rigs' "serve" mode: the protocol in serve_protocol.h, over the USB serial
// port. Each rig gives the ways it reaches the controller's registers; the loop
// here reads the Mac's commands and answers them.
#pragma once

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    uint8_t (*read)(unsigned reg);          // one register read, by the 6502
    void (*write)(unsigned reg, uint8_t value);
    bool (*transferring)(void);             // DRQ: a sector's bytes are moving
    void (*power_on)(bool card);
    void (*card)(bool in);
    void (*resb)(bool low);
    void (*stats)(uint32_t *words);         // SERVE_STAT_COUNT of them
    void (*idle)(void);                     // while waiting for the Mac's next byte
    void (*quit)(void);
} serve_ops_t;

// Prints SERVE_HELLO and serves until SERVE_QUIT.
void serve_run(const serve_ops_t *ops);
