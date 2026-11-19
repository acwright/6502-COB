// The controller as the boards run it: the bus on core 1, the worker on core 0.
#pragma once

void controller_main(void (*banner)(void));
