project('temp-metrics-d-cpp', 'cpp',
  version : '0.1',
  default_options : ['warning_level=3', 'cpp_std=c++20'])

# see https://mesonbuild.com/IndepthTutorial.html

# Corroutines support in gcc seems to be available only for gcc 10+ (check version with `gcc --version`) https://www.phoronix.com/scan.php?page=news_item&px=GCC-11-Flips-On-CPP20-Coroutine
# Also this should be conditional to specific compiler that we know supports C++20, see doc below also to force compiler
# https://mesonbuild.com/howtox.html#use-an-argument-only-with-a-specific-compiler
# add_global_arguments('-fcoroutines -fno-exceptions', language : 'cpp')

# https://mesonbuild.com/howtox.html#enable-threads
thread_dep = dependency('threads')

inc = include_directories('include')

exe = executable('temp_metrics_d_cpp', 
  'src/main.cpp',
  include_directories : inc,
  dependencies : thread_dep,
  install : true)

test('basic', exe)
