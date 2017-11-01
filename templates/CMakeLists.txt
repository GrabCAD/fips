#
# project: $project
#
cmake_minimum_required(VERSION 2.8)

# use FIPS_ROOT from environment 
get_filename_component(FIPS_ROOT_DIR "$ENV{FIPS_ROOT}" ABSOLUTE)
if(FIPS_ROOT_DIR)
    set(FIPS_ROOT_DIR "${FIPS_ROOT_DIR}/fips")
else(FIPS_ROOT_DIR)
    set(FIPS_ROOT_DIR "../fips")
endif(FIPS_ROOT_DIR)

# include the fips main cmake file
include("${FIPS_ROOT_DIR}/cmake/fips.cmake")


# include_directories(src)

fips_setup(PROJECT $project)
# fips_add_subdirectory(src/...)
# fips_add_subdirectory(src/...)
fips_finish()


