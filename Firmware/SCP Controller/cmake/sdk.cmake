# The Raspberry Pi Pico SDK, pinned at one release. Include before project().
#
# PICO_SDK_PATH, from the cache or the environment, points at an SDK already on
# disk. Without it, the SDK is cloned once into build/pico-sdk-<version>, shared by
# every preset, with only the one submodule this firmware uses (TinyUSB, for the
# USB serial port). Either way the SDK must be the pinned release.

set(FW_SDK_VERSION 2.1.1)

if(NOT PICO_SDK_PATH AND DEFINED ENV{PICO_SDK_PATH})
    set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})
endif()

if(NOT PICO_SDK_PATH)
    set(PICO_SDK_PATH ${CMAKE_CURRENT_LIST_DIR}/../build/pico-sdk-${FW_SDK_VERSION})
    if(NOT EXISTS ${PICO_SDK_PATH}/pico_sdk_init.cmake)
        find_package(Git REQUIRED)
        message(STATUS "Cloning the Pico SDK ${FW_SDK_VERSION} into ${PICO_SDK_PATH}")
        execute_process(
            COMMAND ${GIT_EXECUTABLE} clone --quiet --depth 1 --branch ${FW_SDK_VERSION}
                    https://github.com/raspberrypi/pico-sdk ${PICO_SDK_PATH}
            RESULT_VARIABLE _rc)
        if(_rc EQUAL 0)
            execute_process(
                COMMAND ${GIT_EXECUTABLE} -C ${PICO_SDK_PATH} submodule update --quiet --init --depth 1 lib/tinyusb
                RESULT_VARIABLE _rc)
        endif()
        if(NOT _rc EQUAL 0)
            file(REMOVE_RECURSE ${PICO_SDK_PATH})
            message(FATAL_ERROR "Couldn't clone the Pico SDK ${FW_SDK_VERSION}. Check the network, or set PICO_SDK_PATH.")
        endif()
    endif()
endif()

get_filename_component(PICO_SDK_PATH ${PICO_SDK_PATH} REALPATH)
include(${PICO_SDK_PATH}/pico_sdk_version.cmake)
if(NOT PICO_SDK_VERSION_STRING STREQUAL FW_SDK_VERSION)
    message(FATAL_ERROR "This firmware is built with the Pico SDK ${FW_SDK_VERSION}, "
                        "but ${PICO_SDK_PATH} is ${PICO_SDK_VERSION_STRING}.")
endif()
set(PICO_SDK_PATH ${PICO_SDK_PATH} CACHE PATH "The Pico SDK" FORCE)
include(${PICO_SDK_PATH}/pico_sdk_init.cmake)
