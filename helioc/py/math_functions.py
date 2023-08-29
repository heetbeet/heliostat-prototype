import ctypes as _ctypes
from pathlib import Path as _Path
import numpy as _np
_this_dir = _Path(__file__).parent.absolute()

# Load the shared library
_lib = _ctypes.CDLL(str(_this_dir.parent / 'gcc/math_functions.dll'))

# Declare argument types for to_180_form
_lib.to_180_form.argtypes = [_ctypes.c_double]
def to_180_form(degrees):
    return _lib.to_180_form(degrees)

# Declare argument types for rotation_matrix_3d
_lib.rotation_matrix_3d.argtypes = [_ctypes.c_double, _ctypes.c_double, _ctypes.POINTER(_ctypes.c_double)]
def rotation_matrix_3d(theta_rad, phi_rad):
    return_matrix = _np.zeros((3, 3), dtype=_np.float64)
    assert return_matrix.shape == (3, 3)
    return_matrix_p = return_matrix.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    _lib.rotation_matrix_3d(theta_rad, phi_rad, return_matrix_p)
    return (return_matrix)

