project('temp-metrics-d-cpp', 'cpp',
  version : '0.1',
  default_options : ['warning_level=3', 'cpp_std=c++20'])

# see https://mesonbuild.com/IndepthTutorial.html

inc = include_directories('include')

exe = executable('temp_metrics_d_cpp', 
  'src/main.cpp',
  include_directories: inc,
  install : true)

test('basic', exe)
