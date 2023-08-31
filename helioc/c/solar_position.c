#include "solar_position.h"
#include <math.h>
#include <stdio.h>

double julian_day(int year, int month, int day, int hour, int min, int sec) {
    /*
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

    */
    if (month <= 2) {
        year -= 1;
        month += 12;
    }
    double jd = floor(365.25 * (year + 4716.0)) + floor(30.6001 * (month + 1.0)) + 2.0 -
                floor(year / 100.0) + floor(floor(year / 100.0) / 4.0) + day - 1524.5 +
                (hour + min / 60.0 + sec / 3600.0) / 24.0;
    return jd;
}

void solar_az_el(int year, int month, int day, int hour, int min, int sec, double lat, double lon, double alt, double* return_az, double* return_el) {
    /*
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
        
    */

    double pi = 3.14159265358979323846;
    double jd = julian_day(year, month, day, hour, min, sec);
    double d = jd - 2451543.5;

    double w = 282.9404 + 4.70935e-5 * d;
    double e = 0.016709 - 1.151e-9 * d;
    double m = fmod(356.0470 + 0.9856002585 * d, 360.0);

    double l = w + m;
    double oblecl = 23.4393 - 3.563e-7 * d;
    double e_angle = m + (180 / pi) * e * sin(m * (pi / 180)) * (1 + e * cos(m * (pi / 180)));

    double x = cos(e_angle * (pi / 180)) - e;
    double y = sin(e_angle * (pi / 180)) * sqrt(1 - pow(e, 2));
    double r = sqrt(pow(x, 2) + pow(y, 2));
    double v = atan2(y, x) * (180 / pi);
    double lon_angle = v + w;

    double xeclip = r * cos(lon_angle * (pi / 180));
    double yeclip = r * sin(lon_angle * (pi / 180));
    double zeclip = 0.0;

    double xequat = xeclip;
    double yequat = yeclip * cos(oblecl * (pi / 180)) + zeclip * sin(oblecl * (pi / 180));
    double zequat = yeclip * sin(23.4406 * (pi / 180)) + zeclip * cos(oblecl * (pi / 180));

    r = sqrt(pow(xequat, 2) + pow(yequat, 2) + pow(zequat, 2)) - (alt / 149598000);
    double ra = atan2(yequat, xequat) * (180 / pi);
    double delta = asin(zequat / r) * (180 / pi);

    double uth = (double)hour + (double)min / 60.0 + (double)sec / 3600.0;
    double gmst0 = fmod(l + 180, 360.0) / 15;
    double sidtime = gmst0 + uth + lon / 15;

    double ha = (sidtime * 15 - ra);

    x = cos(ha * (pi / 180)) * cos(delta * (pi / 180));
    y = sin(ha * (pi / 180)) * cos(delta * (pi / 180));
    double z = sin(delta * (pi / 180));

    double xhor = x * cos((90 - lat) * (pi / 180)) - z * sin((90 - lat) * (pi / 180));
    double yhor = y;
    double zhor = x * sin((90 - lat) * (pi / 180)) + z * cos((90 - lat) * (pi / 180));

    *return_az = atan2(yhor, xhor) * (180 / pi) + 180;
    *return_el = asin(zhor) * (180 / pi);
}
