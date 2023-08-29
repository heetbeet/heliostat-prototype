#ifndef MATH_FUNCTIONS_H
#define MATH_FUNCTIONS_H

double to_radians(double degrees);
double to_degrees(double radians);
void normalize_vector(double vector[3], double return_vector[3]);
void get_degrees(double normal_vector[3], double *return_theta_deg, double *return_phi_deg);
double dot_product(double vector1[3], double vector2[3]);
double to_180_form(double degrees);
void rotation_matrix_3d(double theta_rad, double phi_rad, double return_matrix[3][3]);
void get_normal_vector(double degrees_from_north, double degrees_elevation, double return_normal[3]);
double closest_point_distance(double point[3], double midpoint[3], double direction[3]);
double euclidean_distance(double vector1[3], double vector2[3]);
double euclidean_vector_distance(double vector1[3], double vector2[3]);
void calculate_sun_position(double day, double month, double year, double UT_hour, double UT_minute, double UT_second, double latitude, double longitude, double *return_Az, double *return_El);

#endif // MATH_FUNCTIONS_H