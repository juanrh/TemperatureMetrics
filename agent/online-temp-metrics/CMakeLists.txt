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

add_executable(main ${all_SRC} )

# To enable threads
# https://stackoverflow.com/questions/5395309/how-do-i-force-cmake-to-include-pthread-option-during-compilation
# target_link_libraries( main ${CMAKE_THREAD_LIBS_INIT} )
