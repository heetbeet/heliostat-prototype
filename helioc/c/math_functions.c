#include "math_functions.h"
#include <math.h>
#include <stdio.h>

#define PI 3.14159265358979323846

double to_radians(double degrees) {
    return (degrees * PI) / 180.0;
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