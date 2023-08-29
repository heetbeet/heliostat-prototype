import ctypes as _ctypes
_cygwin_dll = _ctypes.CDLL(__file__+'/../gcc/cygwin1.dll')
from . import math_functions