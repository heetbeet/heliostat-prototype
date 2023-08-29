import ctypes as _ctypes
from pathlib import Path as _Path
_this_dir = _Path(__file__).parent.absolute()

# Load the shared library
_cygwin_dll = _ctypes.CDLL(r'C:\Users\simon\Applications\cygwin\bin\cygwin1.dll')
_lib = _ctypes.CDLL(str(_this_dir / 'math_functions.dll'))

# Declare argument types for to_180_form
_lib.to_180_form.argtypes = [_ctypes.c_double]
_lib.to_180_form.restype = _ctypes.c_double
to_180_form = _lib.to_180_form

# Declare argument types for rotation_matrix_3d
_lib.rotation_matrix_3d.argtypes = [_ctypes.c_double, _ctypes.c_double, _ctypes.c_double]
_lib.rotation_matrix_3d.restype = None
rotation_matrix_3d = _lib.rotation_matrix_3d

