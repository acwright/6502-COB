# Unit tests on the Mac, one executable per concern.
function(fw_unit_test name)
    add_executable(${name} ${name}.c)
    target_link_libraries(${name} PRIVATE fw_core fw_warnings)
    add_test(NAME ${name} COMMAND ${name} ${ARGN})
endfunction()

fw_unit_test(test_info)     # the banner, and product.h's strings
