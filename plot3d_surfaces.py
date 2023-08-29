import matplotlib.pyplot as plt
import numpy as np
from sun_vector import get_solar_position
from scipy.optimize import minimize
import helioc.math_functions
from helioc.math_functions import rotation_matrix_3d, to_180_form

# to_180_form = helioc.math_functions.to_180_form
# rotation_matrix_3d= helioc.math_functions.rotation_matrix_3d(theta_rad, phi_rad)


def get_normal_vector(degrees_from_north, degrees_elevation):
    """
    Get the normal vector of a surface given its orientation angles.

    Parameters:
        degrees_from_north (float): The angle of the surface normal from the North direction.
        degrees_elevation (float): The elevation angle of the surface normal.

    Returns:
        np.array: The normal vector corresponding to the given angles.
    """
    theta = -degrees_from_north
    phi = -degrees_elevation
    theta_rad = np.radians(theta)
    phi_rad = np.radians(phi)
    R = rotation_matrix_3d(theta_rad, phi_rad)

    normal_vector = R @ np.array([0, -1, 0])  # Rotate the normal vector
    return normal_vector


def get_degrees(normal_vector):
    normal_vector = normal_vector / np.linalg.norm(normal_vector)
    theta_rad = -np.arcsin(normal_vector[0])
    phi_rad = -np.arctan2(normal_vector[2], normal_vector[1]) - np.pi

    # is theta and phi degrees or radians?
    return to_180_form(np.degrees(theta_rad)), to_180_form(np.degrees(phi_rad))


def closest_point_distance(point, midpoint, direction):
    # Convert all inputs to numpy arrays for easier calculations
    P = np.array(point)
    A = np.array(midpoint)
    Dir = np.array(direction)

    # Calculate the closest point on the line to P
    t = np.dot(P - A, Dir) / np.dot(Dir, Dir)
    closest_point = A + t * Dir

    # Calculate the distance between P and the closest point on the line
    distance = np.linalg.norm(P - closest_point)

    return distance


def euclidean_vector_distance(vector1, vector2):
    return np.linalg.norm(vector1 - vector2)


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


def plot_sunray(ax, midpoint, degrees_azimuth, degrees_elevation, r=0.5):
    sunray_point = get_sunray(degrees_azimuth, degrees_elevation)
    # reflected_point = reflect_ray(sunray_point, np.array([0, 1, 0]))

    length = 15
    ax.quiver(
        midpoint[0] - sunray_point[0] * length,
        midpoint[1] - sunray_point[1] * length,
        midpoint[2] - sunray_point[2] * length,
        sunray_point[0],
        sunray_point[1],
        sunray_point[2],
        color="y",
        arrow_length_ratio=0,
        length=length,
    )
    # ax.quiver(
    #    midpoint[0],
    #    midpoint[1],
    #    midpoint[2],
    #    reflected_point[0],
    #    reflected_point[1],
    #    reflected_point[2],
    #    color="b",
    #    arrow_length_ratio=0,
    #    length=length,
    # )


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

    # Plot normal vector (15 units long)
    # normal_vector = R @ np.array([0, -1, 0])  # Rotate the normal vector
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

    # plot_surface(
    #    ax, midpoint=(-10, 0, 2.7), degrees_from_north=0, degrees_elevation=10
    # )  # Surface with red normal

    vector_dest = [9.5, -13, -2.2]
    print(get_degrees([0, 1, -1]))
    print(get_degrees([-1, -1, 0]))

    df = get_solar_position("2023-08-01", -33.8352, 18.6510)
    df = df.iloc[:: int(len(df) / 20)]
    for i, row in df.iterrows():
        start_degrees_from_north = 0
        start_degrees_elevation = 0

        plot_sunray(ax, (-10, 0, 2.7), row["azimuth"] - 8, row["elevation"])
        ray = get_sunray(row["azimuth"] - 8, row["elevation"])

        def objective(angles):
            reflection = reflect_ray(ray, get_normal_vector(angles[0], angles[1]))
            return euclidean_vector_distance(reflection, vector_dest)

        end_degrees_from_north, end_degrees_elivation = minimize(objective, (0, 0)).x
        reflection = reflect_ray(
            ray, get_normal_vector(end_degrees_from_north, end_degrees_elivation)
        )

        plot_point(ax, (-10, 0, 2.7), reflection, color="b", length=15)
        plot_surface(ax, (-10, 0, 2.7), end_degrees_from_north, end_degrees_elivation)

        # break

    # Labels and title
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Two Flat Surfaces")
    ax.set_aspect("equal")

    plt.show()
