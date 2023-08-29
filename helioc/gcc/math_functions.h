#ifndef MATH_FUNCTIONS_H
#define MATH_FUNCTIONS_H

double to_radians(double degrees);
double to_180_form(double degrees);
void rotation_matrix_3d(double theta_rad, double phi_rad, double return_matrix[3][3]);
void get_normal_vector(double degrees_from_north, double degrees_elevation, double return_normal[3]);

#endif // MATH_FUNCTIONS_H