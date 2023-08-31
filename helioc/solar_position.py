import ctypes as _ctypes
from pathlib import Path as _Path
import numpy as _np
_this_dir = _Path(__file__).parent.absolute()
_lib = _ctypes.CDLL(str(_this_dir / 'gcc/solar_position.dll'))


_lib.julian_day.argtypes = [_ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int]
_lib.julian_day.restype = _ctypes.c_double
def julian_day(year, month, day, hour, min, sec):
    r'''
    Calculates the Julian Day Number for a given date and time in UTC time. I found the least confusing way to enter
    a local time is to add the offset to sec, i.e. `sec = time.seconds + time.utcoffset().seconds`

    Args:
        year: The year as an integer (e.g., 2023).
        month: The month as an integer (1 for January, 12 for December).
        day: The day of the month as an integer.
        hour: The hour of the day (0-23).
        min: The minute of the hour (0-59).
        sec: The second of the minute (0-59).

    Returns:
        The Julian Day Number as a double precision doubleing-point number.

    '''
    return _lib.julian_day(year, month, day, hour, min, sec)


_lib.solar_az_el.argtypes = [_ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_double, _ctypes.c_double, _ctypes.c_double, _ctypes.POINTER(_ctypes.c_double), _ctypes.POINTER(_ctypes.c_double)]
def solar_az_el(year, month, day, hour, min, sec, lat, lon, alt):
    r'''
    Calculates solar azimuth and elevation using UTC time, latitude, longitude, and altitude. Ported from MATLAB to C++ to C.
    
    - MATLAB: Darin C. Koblick https://www.mathworks.com/matlabcentral/profile/authors/1284781-darin-koblick
    - C++ port: Kevin Godden https://www.ridgesolutions.ie/index.php/2020/01/14/c-code-to-estimate-solar-azimuth-and-elevation-given-gps-position-and-time/
    
    This function can be expanded by following these suggestions: https://chat.openai.com/share/98aebdd1-328c-4016-9860-02583f9f18b7

    Args:
        year: UTC year
        month: UTC month
        day: UTC day
        hour: UTC hour
        min: UTC minute
        sec: UTC second
        lat: Latitude in degrees
        lon: Longitude in degrees
        alt: Altitude in meters

    Returns:
        az: Azimuth in degrees 
        el: Elevation in degrees
        
    '''
    return_az = _np.zeros((1,), dtype=_np.float64)
    return_el = _np.zeros((1,), dtype=_np.float64)
    assert return_az.shape == (1,)
    return_az = _np.ascontiguousarray(return_az).astype(_np.float64)
    return_az_p = return_az.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    assert return_el.shape == (1,)
    return_el = _np.ascontiguousarray(return_el).astype(_np.float64)
    return_el_p = return_el.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
    _lib.solar_az_el(year, month, day, hour, min, sec, lat, lon, alt, return_az_p, return_el_p)
    return (return_az[0], return_el[0])

