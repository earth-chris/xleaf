project('xleaf', 'c',
  version : '1.0.0',
  meson_version : '>=1.1.0',
  default_options : ['warning_level=2'],
)

add_languages('fortran', native : false)

py = import('python').find_installation(pure : false)

np_dep = dependency('numpy')

incdir_f2py = run_command(py,
  ['-c', 'import os; import numpy.f2py; print(os.path.relpath(numpy.f2py.get_include()))'],
  check : true,
).stdout().strip()

fortranobject_c = incdir_f2py / 'fortranobject.c'

prosail_fortran_sources = files(
  'prosail/MODULE_PRO4SAIL.f90',
  'prosail/dataSpec_PDB.f90',
  'prosail/main_PROSAIL.f90',
  'prosail/LIDF.f90',
  'prosail/dladgen.f',
  'prosail/PRO4SAIL.f90',
  'prosail/prospect_DB.f90',
  'prosail/tav_abs.f90',
  'prosail/volscatt.f90',
)

prosail_f2py = custom_target('prosailmodule.c',
  input : prosail_fortran_sources,
  output : ['prosailmodule.c', 'prosail-f2pywrappers.f', 'prosail-f2pywrappers2.f90'],
  command : [py, '-m', 'numpy.f2py', '@INPUT@', '-m', 'prosail', '--lower'],
)

py.extension_module('prosail',
  [prosail_fortran_sources, prosail_f2py, fortranobject_c],
  include_directories : include_directories(incdir_f2py),
  dependencies : [np_dep],
  subdir : 'xleaf',
  install : true,
)

py.install_sources(
  'xleaf/__init__.py',
  'xleaf/parameters.py',
  'xleaf/samplers.py',
  'xleaf/simulators.py',
  subdir : 'xleaf',
)
