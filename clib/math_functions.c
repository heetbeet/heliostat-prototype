#include "math_functions.h"
#include <math.h>
#include <stdio.h>

double to_180_form(double degrees) {    
    degrees = fmod(degrees, 360.0);
    if (degrees > 180.0) {
        degrees -= 360.0;
    }

    return degrees;
}

void rotation_matrix_3d(double theta_rad, double phi_rad, double matrix[3][3]) {
    matrix[0][0] = cos(theta_rad);
    matrix[0][1] = -sin(theta_rad);
    matrix[0][2] = 0;
    matrix[1][0] = sin(theta_rad);
    matrix[1][1] = cos(theta_rad);
    matrix[1][2] = 0;
    matrix[2][0] = 0;
    matrix[2][1] = 0;
    matrix[2][2] = 1;

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
                result[i][j] += R_phi[i][k] * matrix[k][j];
            }
        }
    }

    // Copy the result back into the input matrix
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            matrix[i][j] = result[i][j];
        }
    }
}

