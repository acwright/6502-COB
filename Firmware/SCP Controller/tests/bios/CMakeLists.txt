# The stock BIOS against the controller's core, in a 65C02 emulator on the Mac.

# vrEmu6502 is third-party code, built as it comes and not held to this
# firmware's warnings.
add_library(vrEmu6502 STATIC vrEmu6502/vrEmu6502.c)
target_include_directories(vrEmu6502 PUBLIC ${CMAKE_CURRENT_LIST_DIR})
target_compile_definitions(vrEmu6502 PUBLIC VR_EMU_6502_STATIC)

add_library(bios_machine STATIC machine.c)
target_include_directories(bios_machine PUBLIC ${CMAKE_CURRENT_LIST_DIR})
target_link_libraries(bios_machine PUBLIC fw_core vrEmu6502 PRIVATE fw_warnings)

add_executable(bios_cli bios_cli.c)
target_link_libraries(bios_cli PRIVATE bios_machine fw_warnings)

# Every case on each ROM: BIOS 1.7 (the COB's) and BIOS 2.1.0 (the ACE's).
add_executable(test_bios test_bios.c)
target_link_libraries(test_bios PRIVATE bios_machine fw_warnings)
foreach(version 1.7 2.1.0)
    add_test(NAME bios_${version} COMMAND test_bios ${CMAKE_CURRENT_LIST_DIR}/roms/BIOS-${version}.bin)
endforeach()

# cffs is the oracle for the disk format. It runs where cffs is on the PATH.
find_program(FW_CFFS cffs)
find_package(Python3 COMPONENTS Interpreter)
if(FW_CFFS AND Python3_FOUND)
    foreach(version 1.7 2.1.0)
        add_test(NAME cffs_${version}
                 COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/cffs_interop.py
                         --cli $<TARGET_FILE:bios_cli> --rom ${CMAKE_CURRENT_LIST_DIR}/roms/BIOS-${version}.bin)
    endforeach()
else()
    message(STATUS "cffs or Python 3 not found: the cffs interop tests are left out")
endif()
