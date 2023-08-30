#include "solar_position.h"
#include <math.h>
#include <stdio.h>


double julian_day(int year, int month, int day, int hour, int min, int sec) {
    if (month <= 2) {
        year -= 1;
        month += 12;
    }
    double jd = floor(365.25 * (year + 4716.0)) + floor(30.6001 * (month + 1.0)) + 2.0 -
        floor(year / 100.0) + floor(floor(year / 100.0) / 4.0) + day - 1524.5 +
        (hour + min / 60.0 + sec / 3600.0) / 24.0;
    return jd;
}

void SolarAzEl(int year, int month, int day, int hour, int min, int sec, double Lat, double Lon, double Alt, double* return_Az, double* return_El) {
    /*
    Calculates Solar Azimuth and Elevation using UTC time, latitude, longitude and altitude. Ported from MATLAB to C++ to C.
    
    - MATLAB: Darin C. Koblick https://www.mathworks.com/matlabcentral/profile/authors/1284781-darin-koblick
    - C++ port: Kevin Godden https://www.ridgesolutions.ie/index.php/2020/01/14/c-code-to-estimate-solar-azimuth-and-elevation-given-gps-position-and-time/

    Arguments:
        year: UTC year
        month: UTC month
        day: UTC day
        hour: UTC hour
        min: UTC minute
        sec: UTC second
        Lat: Latitude in degrees
        Lon: Longitude in degrees
        Alt: Altitude in meters

    Returns:
        Az: Azimuth in degrees 
        El: Elevation in degrees
    */

    double jd = julian_day(year, month, day, hour, min, sec);
    double d = jd - 2451543.5;

    double w = 282.9404 + 4.70935e-5 * d;
    double e = 0.016709 - 1.151e-9 * d;
    double M = fmod(356.0470 + 0.9856002585 * d, 360.0);

    double L = w + M;
    double oblecl = 23.4393 - 3.563e-7 * d;
    double E = M + (180 / M_PI) * e * sin(M * (M_PI / 180)) * (1 + e * cos(M * (M_PI / 180)));

    double x = cos(E * (M_PI / 180)) - e;
    double y = sin(E * (M_PI / 180)) * sqrt(1 - pow(e, 2));
    double r = sqrt(pow(x, 2) + pow(y, 2));
    double v = atan2(y, x) * (180 / M_PI);
    double lon = v + w;

    double xeclip = r * cos(lon * (M_PI / 180));
    double yeclip = r * sin(lon * (M_PI / 180));
    double zeclip = 0.0;

    double xequat = xeclip;
    double yequat = yeclip * cos(oblecl * (M_PI / 180)) + zeclip * sin(oblecl * (M_PI / 180));
    double zequat = yeclip * sin(23.4406 * (M_PI / 180)) + zeclip * cos(oblecl * (M_PI / 180));

    r = sqrt(pow(xequat, 2) + pow(yequat, 2) + pow(zequat, 2)) - (Alt / 149598000);
    double RA = atan2(yequat, xequat) * (180 / M_PI);
    double delta = asin(zequat / r) * (180 / M_PI);

    double UTH = (double)hour + (double)min / 60.0 + (double)sec / 3600.0;
    double GMST0 = fmod(L + 180, 360.0) / 15;
    double SIDTIME = GMST0 + UTH + Lon / 15;

    double HA = (SIDTIME * 15 - RA);

    x = cos(HA * (M_PI / 180)) * cos(delta * (M_PI / 180));
    y = sin(HA * (M_PI / 180)) * cos(delta * (M_PI / 180));
    double z = sin(delta * (M_PI / 180));

    double xhor = x * cos((90 - Lat) * (M_PI / 180)) - z * sin((90 - Lat) * (M_PI / 180));
    double yhor = y;
    double zhor = x * sin((90 - Lat) * (M_PI / 180)) + z * cos((90 - Lat) * (M_PI / 180));

    *return_Az = atan2(yhor, xhor) * (180 / M_PI) + 180;
    *return_El = asin(zhor) * (180 / M_PI);
}