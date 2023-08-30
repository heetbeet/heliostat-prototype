import helioc
import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import minimize
from helioc.math_functions import (
    rotation_matrix_3d,
    to_180_form,
    get_normal_vector,
    get_degrees,
    closest_point_distance,
    euclidean_vector_distance, 
)
from sun_vector import get_solar_position


def reflect_ray(ray_direction, normal):
    """
    Calculate the direction vector of a reflected ray.

    Parameters:
        ray_direction (np.array): The direction vector of the incoming ray.
        normal (np.array): The normal vector of the surface at the point of intersection.

    Returns:
        np.array: The direction vector of the reflected ray.
    """

    # Normalize the vectors
    ray_direction = ray_direction / np.linalg.norm(ray_direction)
    normal = normal / np.linalg.norm(normal)

    # Calculate the reflected ray
    reflected_ray = ray_direction - 2 * np.dot(ray_direction, normal) * normal

    return reflected_ray


def get_sunray(sun_degrees_azimuth, sun_degrees_elevation):
    """
    Calculate the direction vector of a sun ray.

    Parameters:
        sun_degrees_azimuth (float): The azimuth angle of the sun in degrees.
        sun_degrees_elevation (float): The elevation angle of the sun in degrees.

    Returns:
        np.array: The direction vector of the sun ray.
    """

    # Convert angles to radians
    theta_rad = np.radians(-sun_degrees_azimuth)
    phi_rad = np.radians(-sun_degrees_elevation)

    point = np.array([0, 1, 0])

    R = rotation_matrix_3d(theta_rad, phi_rad)
    point = R @ point
    point = point / np.linalg.norm(point)

    return point


def plot_point(ax, midpoint, point, **kwargs):
    if not "arrow_length_ratio" in kwargs:
        kwargs["arrow_length_ratio"] = 0
    if not "length" in kwargs:
        kwargs["length"] = 1
    if not "linewidth" in kwargs:
        kwargs["linewidth"] = 1

    ax.quiver(
        midpoint[0],
        midpoint[1],
        midpoint[2],
        point[0],
        point[1],
        point[2],
        **kwargs,
    )


def plot_sunray(ax, midpoint, degrees_azimuth, degrees_elevation, **kwargs):
    sunray_point = get_sunray(degrees_azimuth, degrees_elevation)

    if "length" not in kwargs:
        kwargs["length"] = 15
    if "arrow_length_ratio" not in kwargs:
        kwargs["arrow_length_ratio"] = 0
    if "color" not in kwargs:
        kwargs["color"] = "y"
    
    length = kwargs["length"]
    ax.quiver(
        midpoint[0] - sunray_point[0] * length,
        midpoint[1] - sunray_point[1] * length,
        midpoint[2] - sunray_point[2] * length,
        sunray_point[0],
        sunray_point[1],
        sunray_point[2],
        **kwargs
    )


def plot_surface(ax, midpoint, degrees_from_north, degrees_elevation, r=0.5):
    theta = -degrees_from_north
    phi = -degrees_elevation

    u, v = np.mgrid[0 : np.pi : 20j, 0 : np.pi : 10j]
    x = 0.5 * np.cos(u) * np.sin(v)
    y = np.zeros_like(x)
    z = 0.5 * np.cos(v)

    # Transform circle to target midpoint and orientation
    theta_rad = np.radians(theta)
    phi_rad = np.radians(phi)
    R = rotation_matrix_3d(theta_rad, phi_rad)
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            vec = [x[i, j], y[i, j], z[i, j]]
            x[i, j], y[i, j], z[i, j] = R @ vec

    x = x + midpoint[0]
    y = y + midpoint[1]
    z = z + midpoint[2]

    # Plot surface
    ax.plot_surface(
        x, y, z, alpha=0.5, facecolors="r", rstride=100, cstride=100, linewidth=0
    )

    normal_vector = get_normal_vector(degrees_from_north, degrees_elevation)

    ax.quiver(
        midpoint[0],
        midpoint[1],
        midpoint[2],
        normal_vector[0],
        normal_vector[1],
        normal_vector[2],
        color="r",
        arrow_length_ratio=0,
        length=1,
        linewidth=1,
    )


if __name__ == "__main__":
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # Define points for the first surface (keep y=0)
    x1 = np.array([0, -10, 0, -10])
    z1 = np.array([0, 0, 2.7, 2.7])
    y1 = np.array([0, 0, 0, 0])

    # Reshape and plot
    X1 = x1.reshape((2, 2))
    Y1 = y1.reshape((2, 2))
    Z1 = z1.reshape((2, 2))

    ax.plot_surface(X1, Y1, Z1, alpha=0.5, rstride=100, cstride=100)

    # Define points for the second surface (keep z=0)
    x2 = np.array([0, -2, 0, -2])
    y2 = np.array([0, 0, -13, -13])
    z2 = np.array([0, 0, 0, 0])

    # Reshape and plot
    X2 = x2.reshape((2, 2))
    Y2 = y2.reshape((2, 2))
    Z2 = z2.reshape((2, 2))

    ax.plot_surface(
        X2, Y2, Z2, alpha=0.5, facecolors="g", rstride=100, cstride=100, linewidth=0
    )

    vector_dest = np.array([9.5, -13, -2.2])

    df = get_solar_position("2023-08-01", -33.8352, 18.6510)
    df = df.iloc[:: int(len(df) / 20)]

    for i, row in df.iterrows():
        time = row["time"]
        
        plot_sunray(ax, (-10, 0, 2.7), row["azimuth"] -8, row["elevation"], color="y")

        ray = get_sunray(row["azimuth"] -8, row["elevation"])

        
        surface_normal = ((-ray / np.linalg.norm(ray)) + (vector_dest/ np.linalg.norm(vector_dest)))/2

        degrees_from_north, degrees_elivation = get_degrees(surface_normal)
        reflection = reflect_ray(
            ray, get_normal_vector(degrees_from_north, degrees_elivation)
        )

        plot_point(ax, (-10, 0, 2.7), reflection, color="b", length=15)
        plot_surface(ax, (-10, 0, 2.7), degrees_from_north, degrees_elivation)
        

    # Labels and title
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Two Flat Surfaces")
    ax.set_aspect("equal")

    plt.show()
