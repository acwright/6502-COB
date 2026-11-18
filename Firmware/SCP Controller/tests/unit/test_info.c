// The banner the firmware prints on its USB serial port.
#include "fw_info.h"
#include "product.h"
#include "version.h"

#include "test.h"

static const char hash[] = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";

TEST(banner_names_the_build)
{
    char buf[200];
    int n = fw_banner(buf, sizeof buf, "SCP Controller", "0.1.0", hash, "Pico 2: SD card and flash rig");
    CHECK_STR("SCP Controller 0.1.0 (source 0123456789ab), Pico 2: SD card and flash rig\r\n"
              "Copyright (c) 2026 A.C. Wright Design\r\n", buf);
    CHECK_EQ((long long)strlen(buf), n);
}

TEST(banner_truncates_safely)
{
    char buf[8];
    int n = fw_banner(buf, sizeof buf, "SCP Controller", "0.1.0", hash, "board");
    CHECK_STR("SCP Con", buf);
    CHECK(n > (int)sizeof buf);
}

TEST(product_fits_identify)
{
    // IDENTIFY's model field is 40 characters.
    CHECK(strlen(PRODUCT_MODEL) <= 40);
    CHECK(strlen(PRODUCT_FIRMWARE) > 0);
    CHECK(strlen(FW_VERSION) >= 5);
}

int main(void)
{
    RUN(banner_names_the_build);
    RUN(banner_truncates_safely);
    RUN(product_fits_identify);
    return TEST_RESULT();
}
