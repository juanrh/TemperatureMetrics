cmake_minimum_required(VERSION 3.16.0)
project(online_temp_metrics)

# Enable C++17
# We can also use this to define arbitrary variables,
# that can then be referred with ${}
set(CMAKE_CXX_STANDARD 17)

# To enable threads
# https://cmake.org/pipermail/cmake/2016-February/062729.html
# find_package (Threads)

# declare the _header files_ are in `include` directory of the project
include_directories("include")

# https://stackoverflow.com/questions/3201154/automatically-add-all-files-in-a-folder-to-a-target-using-cmake
# NOTE: after adding a new source file we still need to regenerate
# to make files, with either `cmake ..` or in VsCode with the task
# "CMake: Configure"
file(GLOB all_SRC
     "src/*.cpp"
)

add_executable(main ${all_SRC} "src/sht31_sensor.c")

# To enable threads
# https://stackoverflow.com/questions/5395309/how-do-i-force-cmake-to-include-pthread-option-during-compilation
# target_link_libraries( main ${CMAKE_THREAD_LIBS_INIT} )

# To use libi2c. Install with conan following https://docs.conan.io/en/1.36/reference/conanfile/methods.html#system-requirements
# https://stackoverflow.com/questions/63890499/how-to-link-dynamic-library-li2c-with-cmake-undefined-reference-to-i2c-smb
# target_link_libraries(main i2c)
