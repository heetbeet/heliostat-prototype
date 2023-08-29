#include "math_functions.h"
#include <math.h>
#include <stdio.h>

#define PI 3.14159265358979323846
#define J2000_0 2451545.0
#define DEG_TO_RAD (PI / 180.0)
#define RAD_TO_DEG (180.0 / PI)


double to_radians(double degrees) {
    return (degrees * PI) / 180.0;
}

double to_degrees(double radians) {
    return (radians * 180.0) / PI;
}

void normalize_vector(double vector[3], double return_vector[3]) {
    for (int i = 0; i < 3; ++i) {
        return_vector[i] = vector[i];
    }

    double norm = sqrt(return_vector[0] * return_vector[0] + return_vector[1] * return_vector[1] + return_vector[2] * return_vector[2]);
    for (int i = 0; i < 3; ++i) {
        return_vector[i] /= norm;
    }
}

void get_degrees(double normal_vector[3], double *return_theta_deg, double *return_phi_deg) {
    double normalized_normal_vector[3];
    normalize_vector(normal_vector, normalized_normal_vector);
    double theta_rad = -asin(normalized_normal_vector[0]);
    double phi_rad = -atan2(normalized_normal_vector[2], normalized_normal_vector[1]) - PI;
    *return_theta_deg = to_180_form(to_degrees(theta_rad));
    *return_phi_deg = to_180_form(to_degrees(phi_rad));
}

double dot_product(double vector1[3], double vector2[3]) {
    double result = 0;
    for (int i = 0; i < 3; ++i) {
        result += vector1[i] * vector2[i];
    }
    return result;
}

double to_180_form(double degrees) {    
    degrees = fmod(degrees, 360.0);
    if (degrees > 180.0) {
        degrees -= 360.0;
    }

    return degrees;
}

void rotation_matrix_3d(double theta_rad, double phi_rad, double return_matrix[3][3]) {
    return_matrix[0][0] = cos(theta_rad);
    return_matrix[0][1] = -sin(theta_rad);
    return_matrix[0][2] = 0;
    return_matrix[1][0] = sin(theta_rad);
    return_matrix[1][1] = cos(theta_rad);
    return_matrix[1][2] = 0;
    return_matrix[2][0] = 0;
    return_matrix[2][1] = 0;
    return_matrix[2][2] = 1;

    double R_phi[3][3] = {
        {1, 0, 0},
        {0, cos(phi_rad), -sin(phi_rad)},
        {0, sin(phi_rad), cos(phi_rad)}
    };

    // Matrix multiplication
    double result[3][3] = {0};
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            for (int k = 0; k < 3; k++) {
                result[i][j] += R_phi[i][k] * return_matrix[k][j];
            }
        }
    }

    // Copy the result back into the input matrix
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            return_matrix[i][j] = result[i][j];
        }
    }
}


void get_normal_vector(double degrees_from_north, double degrees_elevation, double return_normal[3]) {
    double theta = -degrees_from_north;
    double phi = -degrees_elevation;

    double theta_rad = to_radians(theta);
    double phi_rad = to_radians(phi);

    double R[3][3];
    rotation_matrix_3d(theta_rad, phi_rad, R);

    // The original normal vector is [0, -1, 0]
    double original_normal[3] = {0, -1, 0};
    
    // Initialize the resulting normal vector to zero
    for (int i = 0; i < 3; ++i) {
        return_normal[i] = 0;
    }

    // Perform matrix-vector multiplication
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            return_normal[i] += R[i][j] * original_normal[j];
        }
    }
}

double closest_point_distance(double point[3], double midpoint[3], double direction[3]) {
    double P_minus_A[3] = {
        point[0] - midpoint[0],
        point[1] - midpoint[1],
        point[2] - midpoint[2]
    };
    double t = dot_product(P_minus_A, direction) / dot_product(direction, direction);
    double closest_point[3];
    for (int i = 0; i < 3; ++i) {
        closest_point[i] = midpoint[i] + t * direction[i];
    }
    return euclidean_distance(point, closest_point);
}

double euclidean_distance(double vector1[3], double vector2[3]) {
    double result = 0;
    for (int i = 0; i < 3; ++i) {
        double diff = vector1[i] - vector2[i];
        result += diff * diff;
    }
    return sqrt(result);
}

double euclidean_vector_distance(double vector1[3], double vector2[3]) {
    double normalize_vector1[3];
    double normalize_vector2[3];
    normalize_vector(vector1, normalize_vector1);
    normalize_vector(vector2, normalize_vector2);
    return euclidean_distance(normalize_vector1, normalize_vector2);
}


void calculate_sun_position(double day, double month, double year, double UT_hour, double UT_minute, double UT_second, double latitude, double longitude, double *return_Az, double *return_El) {
    // Convert Universal Time to a decimal (hours)
    double UT = UT_hour + UT_minute / 60.0 + UT_second / 3600.0;
  
    // Julian Date Calculation (Simplified)
    double JD = day + ((month - 1) / 12.0) + year + (UT / 24.0) - 0.5;

    // Number of Centuries since the Epoch (J2000.0)
    double n = JD - J2000_0;
    double T = n / 36525.0;

    // Sun's Mean Longitude (normalized to [0, 360))
    double L0 = fmod(280.46646 + 36000.76983 * T + 0.0003032 * pow(T, 2), 360.0);

    // Mean Anomaly (normalized to [0, 360))
    double M = fmod(357.52911 + 35999.05029 * T - 0.0001537 * pow(T, 2), 360.0);

    // Calculate Eccentricity
    double e = 0.016708634 - 0.000042037 * T - 0.0000001267 * pow(T, 2);

    // Calculate Sun's Apparent Longitude (degrees)
    double lambda = L0 + ( (1.914602 - 0.004817 * T - 0.000014 * pow(T, 2)) * sin(DEG_TO_RAD * M) + (0.019993 - 0.000101 * T) * sin(DEG_TO_RAD * 2 * M) + 0.000289 * sin(DEG_TO_RAD * 3 * M) );

    // Calculate Sun's Declination (degrees)
    double delta = asin(sin(DEG_TO_RAD * lambda) * sin(DEG_TO_RAD * (23.436993 + 0.000013 * T))) * RAD_TO_DEG;

    // Calculate Equation of Time in minutes
    double EoT = 229.18 * (0.000075 + 0.001868 * cos(DEG_TO_RAD * M) - 0.032077 * sin(DEG_TO_RAD * M) - 0.014615 * cos(DEG_TO_RAD * 2 * M) - 0.040849 * sin(DEG_TO_RAD * 2 * M));

    // Convert EoT to hours
    double EoT_hours = EoT / 60.0;

    // Hour Angle Calculation with Equation of Time
    double H = fmod(15.0 * (UT + 4.0 * (lambda - longitude) + EoT_hours) - 180.0, 360.0);

    // Calculate Elevation and Azimuth
    double phi = latitude * DEG_TO_RAD;
    double H_rad = H * DEG_TO_RAD;
    double delta_rad = delta * DEG_TO_RAD;

    double El_rad = asin(sin(phi) * sin(delta_rad) + cos(phi) * cos(delta_rad) * cos(H_rad));
    double Az_rad = acos((sin(delta_rad) - sin(El_rad) * sin(phi)) / (cos(El_rad) * cos(phi)));
    double Az_rad_corrected = (sin(delta_rad) < 0) ? (PI - Az_rad) : Az_rad;

    *return_El = El_rad * RAD_TO_DEG;
    *return_Az = Az_rad_corrected * RAD_TO_DEG;
}