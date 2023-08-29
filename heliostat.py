import pvlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np


def flatten(lst):
    return [item for sublist in lst for item in sublist]


def to_180_form(degrees):
    degrees = degrees % 360  # Normalize to [0, 360)
    degrees[degrees > 180] -= 360  # Convert to [-180, 180]
    return degrees


def plot_solar_path(latitude, longitude, degree_offset, date):
    fig, ax1 = plt.subplots(figsize=(8, 6))

    # Normalize colors
    norm = plt.Normalize(vmin=0, vmax=23)

    for date in flatten(
        [
            [f"2023-{i:02d}-{int(j)}" for j in np.linspace(1, 31, 10)]
            for i in range(1, 13)
        ]
    ):
        try:
            times = pd.date_range(
                date, periods=24 * 60, freq="1T"
            )  # Generating timestamps for every minute of the day
        except pd._libs.tslibs.parsing.DateParseError:
            continue

        solar_position = pvlib.solarposition.get_solarposition(
            times, latitude, longitude
        )
        solar_position = solar_position[solar_position["elevation"] >= 0]
        sc = ax1.scatter(
            to_180_form(solar_position.azimuth + degree_offset),
            solar_position.elevation,
            c=solar_position.index.hour,
            cmap="bwr",
            norm=norm,
            s=10,
        )

    ax1.set_title("North-facing 2D Curve")
    ax1.set_xlabel("Degrees from North (0=North, 180=South)")
    ax1.set_ylabel("Elevation Angle (Degrees)")
    ax1.set_xlim([-180, 180])
    ax1.set_xticks((np.arange(-180, 181, 30)))
    ax1.set_xticklabels([str(angle) for angle in np.arange(-180, 181, 30)])
    ax1.set_xticks((np.arange(-180, 181, 10)), minor=True)
    ax1.grid(color="gray", linestyle="-", linewidth=0.5, which="both")
    ax1.set_yticks(np.arange(0, 91, 10))
    ax1.set_ylim([0, 90])
    ax1.grid(True)

    # Add a color bar
    cbar = plt.colorbar(sc, ax=ax1, orientation="vertical", pad=0.1, cmap="bwr")
    cbar.set_label("Hour of the day")

    plt.tight_layout()
    plt.show()


latitude, longitude = -33.8352, 18.6510  # Durbanville, South Africa
date = "2023-08-01"
plot_solar_path(latitude, longitude, 0, date)
