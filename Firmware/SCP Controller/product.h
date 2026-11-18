// The board this copy of the firmware is for.
//
// This firmware is kept in two copies: the SCP Controller in 6502-COB, for the
// Storage Card Pro, and the ASDA Controller in 6502-ACE, for the ACE SD Adapter.
// The two boards share one circuit, so the copies are the same, byte for byte,
// except this file and README.md. Tools/firmware/twins.py checks that.
#pragma once

#define PRODUCT_NAME     "Storage Card Pro"                       // USB product string
#define PRODUCT_FIRMWARE "SCP Controller"                         // the firmware's name and its .uf2 file
#define PRODUCT_MODEL    "AC6502 Storage Card Pro"                // IDENTIFY's model string, 40 characters at most
#define PRODUCT_REPO_URL "https://github.com/acwright/6502-COB"
