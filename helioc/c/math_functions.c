#include "math_functions.h"
#include <math.h>
#include <stdio.h>

#define PI 3.14159265358979323846
#define M_PI 3.14159265358979323846
#define J2000_0 2451545.0
#define DEG_TO_RAD (PI / 180.0)
#define RAD_TO_DEG (180.0 / PI)


double to_radians(double degrees) {
    /*
    Converts angles from degrees to radians.

    Args:
        degrees: The angle in degrees.

    Returns:
        The angle in radians.
    */

    return (degrees * PI) / 180.0;
}

double to_degrees(double radians) {
    /*
    Converts angles from radians to degrees.

    Args:
        radians: The angle in radians.

    Returns:
        The angle in degrees.
    */

    return (radians * 180.0) / PI;
}

void normalize_vector(double vector[3], double return_vector[3]) {
    /*
    Normalizes a 3D vector.

    Args:
        vector: The input vector.

    Returns:
        return_vector: The normalized output vector.

    */

    for (int i = 0; i < 3; ++i) {
        return_vector[i] = vector[i];
    }

    double norm = sqrt(return_vector[0] * return_vector[0] + return_vector[1] * return_vector[1] + return_vector[2] * return_vector[2]);
    for (int i = 0; i < 3; ++i) {
        return_vector[i] /= norm;
    }
}

void get_degrees(double normal_vector[3], double *return_theta_deg, double *return_phi_deg) {
    /*
    Gets the theta and phi angles in degrees for a given normal vector.

    Args:
        normal_vector: The input normal vector.

    Returns:
        return_theta_deg: The theta angle in degrees.
        return_phi_deg: The phi angle in degrees.

    */

    double normalized_normal_vector[3];
    normalize_vector(normal_vector, normalized_normal_vector);
    double theta_rad = -asin(normalized_normal_vector[0]);
    double phi_rad = -atan2(normalized_normal_vector[2], normalized_normal_vector[1]) - PI;
    *return_theta_deg = to_180_form(to_degrees(theta_rad));
    *return_phi_deg = to_180_form(to_degrees(phi_rad));
}

double dot_product(double vector1[3], double vector2[3]) {
    /*
    Calculates the dot product of two 3D vectors.

    Args:
        vector1: The first input vector.
        vector2: The second input vector.

    Returns:
        The dot product of the input vectors.

    */

    double result = 0;
    for (int i = 0; i < 3; ++i) {
        result += vector1[i] * vector2[i];
    }
    return result;
}

double to_180_form(double degrees) {    
    /*
    Converts any angle to its equivalent representation between -180 and 180 degrees.

    Args:
        degrees: The input angle in degrees.

    Returns:
        The angle in the -180 to 180 degree range.

    */

    degrees = fmod(degrees, 360.0);
    if (degrees > 180.0) {
        degrees -= 360.0;
    }

    return degrees;
}

void rotation_matrix_3d(double theta_rad, double phi_rad, double return_matrix[3][3]) {
    /*
    Calculates the 3D rotation matrix based on theta and phi angles in radians.

    Args:
        theta_rad: The theta angle in radians.
        phi_rad: The phi angle in radians.

    Returns:
        return_matrix: The resulting 3D rotation matrix.

    */

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
    /*
    Computes a normal vector based on input degrees from north and degrees elevation.

    Args:
        degrees_from_north: The angle from the north in degrees.
        degrees_elevation: The elevation angle in degrees.

    Returns:
        return_normal: The computed normal vector.

    */

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
    /*
    Computes the distance between a point and the closest point on a line specified by a midpoint and direction.
   
    Args:
        point: The point in 3D space.
        midpoint: The midpoint of the line segment.
        direction: The direction vector of the line segment.
   
    Returns:
        The distance between the point and the closest point on the line segment.

    */

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
    /*
    Calculates the Euclidean distance between two points in 3D space.

    Args:
        vector1: The coordinates of the first point.
        vector2: The coordinates of the second point.

    Returns:
        The Euclidean distance between the two points.

    */
    double result = 0;
    for (int i = 0; i < 3; ++i) {
        double diff = vector1[i] - vector2[i];
        result += diff * diff;
    }
    return sqrt(result);
}

double euclidean_vector_distance(double vector1[3], double vector2[3]) {
    /*
    Calculates the Euclidean distance between two normalized vectors in 3D space.
    
    Args:
        vector1: The first input vector.
        vector2: The second input vector.

    Returns:
        The Euclidean distance between the normalized vectors.

    */
    double normalize_vector1[3];
    double normalize_vector2[3];
    normalize_vector(vector1, normalize_vector1);
    normalize_vector(vector2, normalize_vector2);
    return euclidean_distance(normalize_vector1, normalize_vector2);
}
