import ctypes as _ctypes
from pathlib import Path as _Path
import numpy as _np
_this_dir = _Path(__file__).parent.absolute()
_lib = _ctypes.CDLL(str(_this_dir / 'gcc/math_functions.dll'))


_lib.to_radians.argtypes = [_ctypes.c_double]
_lib.to_radians.restype = _ctypes.c_double
def to_radians(degrees):
    return _lib.to_radians(degrees)


_lib.to_degrees.argtypes = [_ctypes.c_double]
_lib.to_degrees.restype = _ctypes.c_double
def to_degrees(radians):
    return _lib.to_degrees(radians)


_lib.normalize_vector.argtypes = [_ctypes.POINTER(_ctypes.c_double), _ctypes.POINTER(_ctypes.c_double)]
def normalize_vector(vector):
    return_vector = _np.zeros((3,), dtype=_np.float64)
    assert vector.shape == (3,)
    vector = _np.ascontiguousarray(vector).astype(_np.float64)
    vector_p = vector.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    assert return_vector.shape == (3,)
    return_vector = _np.ascontiguousarray(return_vector).astype(_np.float64)
    return_vector_p = return_vector.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    _lib.normalize_vector(vector_p, return_vector_p)
    return (return_vector)


_lib.get_degrees.argtypes = [_ctypes.POINTER(_ctypes.c_double), _ctypes.POINTER(_ctypes.c_double), _ctypes.POINTER(_ctypes.c_double)]
def get_degrees(normal_vector):
    return_theta_deg = _np.zeros((1,), dtype=_np.float64)
    return_phi_deg = _np.zeros((1,), dtype=_np.float64)
    assert normal_vector.shape == (3,)
    normal_vector = _np.ascontiguousarray(normal_vector).astype(_np.float64)
    normal_vector_p = normal_vector.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    assert return_theta_deg.shape == (1,)
    return_theta_deg = _np.ascontiguousarray(return_theta_deg).astype(_np.float64)
    return_theta_deg_p = return_theta_deg.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    assert return_phi_deg.shape == (1,)
    return_phi_deg = _np.ascontiguousarray(return_phi_deg).astype(_np.float64)
    return_phi_deg_p = return_phi_deg.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    _lib.get_degrees(normal_vector_p, return_theta_deg_p, return_phi_deg_p)
    return (return_theta_deg[0], return_phi_deg[0])


_lib.dot_product.argtypes = [_ctypes.POINTER(_ctypes.c_double), _ctypes.POINTER(_ctypes.c_double)]
_lib.dot_product.restype = _ctypes.c_double
def dot_product(vector1, vector2):
    assert vector1.shape == (3,)
    vector1 = _np.ascontiguousarray(vector1).astype(_np.float64)
    vector1_p = vector1.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    assert vector2.shape == (3,)
    vector2 = _np.ascontiguousarray(vector2).astype(_np.float64)
    vector2_p = vector2.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    return _lib.dot_product(vector1_p, vector2_p)


_lib.to_180_form.argtypes = [_ctypes.c_double]
_lib.to_180_form.restype = _ctypes.c_double
def to_180_form(degrees):
    return _lib.to_180_form(degrees)


_lib.rotation_matrix_3d.argtypes = [_ctypes.c_double, _ctypes.c_double, _ctypes.POINTER(_ctypes.c_double)]
def rotation_matrix_3d(theta_rad, phi_rad):
    return_matrix = _np.zeros((3, 3), dtype=_np.float64)
    assert return_matrix.shape == (3, 3)
    return_matrix = _np.ascontiguousarray(return_matrix).astype(_np.float64)
    return_matrix_p = return_matrix.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    _lib.rotation_matrix_3d(theta_rad, phi_rad, return_matrix_p)
    return (return_matrix)


_lib.get_normal_vector.argtypes = [_ctypes.c_double, _ctypes.c_double, _ctypes.POINTER(_ctypes.c_double)]
def get_normal_vector(degrees_from_north, degrees_elevation):
    return_normal = _np.zeros((3,), dtype=_np.float64)
    assert return_normal.shape == (3,)
    return_normal = _np.ascontiguousarray(return_normal).astype(_np.float64)
    return_normal_p = return_normal.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    _lib.get_normal_vector(degrees_from_north, degrees_elevation, return_normal_p)
    return (return_normal)


_lib.closest_point_distance.argtypes = [_ctypes.POINTER(_ctypes.c_double), _ctypes.POINTER(_ctypes.c_double), _ctypes.POINTER(_ctypes.c_double)]
_lib.closest_point_distance.restype = _ctypes.c_double
def closest_point_distance(point, midpoint, direction):
    assert point.shape == (3,)
    point = _np.ascontiguousarray(point).astype(_np.float64)
    point_p = point.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    assert midpoint.shape == (3,)
    midpoint = _np.ascontiguousarray(midpoint).astype(_np.float64)
    midpoint_p = midpoint.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    assert direction.shape == (3,)
    direction = _np.ascontiguousarray(direction).astype(_np.float64)
    direction_p = direction.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    return _lib.closest_point_distance(point_p, midpoint_p, direction_p)


_lib.euclidean_distance.argtypes = [_ctypes.POINTER(_ctypes.c_double), _ctypes.POINTER(_ctypes.c_double)]
_lib.euclidean_distance.restype = _ctypes.c_double
def euclidean_distance(vector1, vector2):
    assert vector1.shape == (3,)
    vector1 = _np.ascontiguousarray(vector1).astype(_np.float64)
    vector1_p = vector1.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    assert vector2.shape == (3,)
    vector2 = _np.ascontiguousarray(vector2).astype(_np.float64)
    vector2_p = vector2.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    return _lib.euclidean_distance(vector1_p, vector2_p)


_lib.euclidean_vector_distance.argtypes = [_ctypes.POINTER(_ctypes.c_double), _ctypes.POINTER(_ctypes.c_double)]
_lib.euclidean_vector_distance.restype = _ctypes.c_double
def euclidean_vector_distance(vector1, vector2):
    assert vector1.shape == (3,)
    vector1 = _np.ascontiguousarray(vector1).astype(_np.float64)
    vector1_p = vector1.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    assert vector2.shape == (3,)
    vector2 = _np.ascontiguousarray(vector2).astype(_np.float64)
    vector2_p = vector2.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    return _lib.euclidean_vector_distance(vector1_p, vector2_p)

