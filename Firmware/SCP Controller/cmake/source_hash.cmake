# Writes OUT, a header defining FW_SOURCE_HASH: one SHA-256 over every file that
# goes into the firmware. The build stamps it into the .uf2, and
# Tools/firmware/twins.py computes the same hash from the files to check that a
# tracked .uf2 was built from the sources beside it.
#
#   cmake -DROOT=<firmware folder> -DOUT=<header> -P source_hash.cmake
#
# The files: product.h, CMakeLists.txt, CMakePresets.json, and everything under
# cmake/, core/ and rp2350/ (but .DS_Store), sorted by path. The hash is taken
# over one line per file, "<sha256 of the file>  <path>\n", paths relative to
# ROOT with forward slashes. twins.py must do exactly the same.

set(_files product.h CMakeLists.txt CMakePresets.json)
foreach(_dir cmake core rp2350)
    file(GLOB_RECURSE _found RELATIVE ${ROOT} ${ROOT}/${_dir}/*)
    list(APPEND _files ${_found})
endforeach()
list(FILTER _files EXCLUDE REGEX "(^|/)\\.DS_Store$")
list(SORT _files)

set(_lines "")
foreach(_f IN LISTS _files)
    file(SHA256 ${ROOT}/${_f} _h)
    string(APPEND _lines "${_h}  ${_f}\n")
endforeach()
string(SHA256 _tree "${_lines}")

set(_text "// Written by cmake/source_hash.cmake. Don't edit.\n#pragma once\n#define FW_SOURCE_HASH \"${_tree}\"\n")
if(EXISTS ${OUT})
    file(READ ${OUT} _old)
else()
    set(_old "")
endif()
if(NOT _old STREQUAL _text)
    file(WRITE ${OUT} "${_text}")
endif()
