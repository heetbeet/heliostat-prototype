import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#from pvlib import solarposition
#import matplotlib.colors as mcolors

import helioc
from helioc.solar_position import solar_az_el
from helioc.math_functions import to_180_form


def flatten(lst):
    return [item for sublist in lst for item in sublist]


#def to_180_form(degrees):
#    degrees = degrees % 360  # Normalize to [0, 360)
#    degrees[degrees > 180] -= 360  # Convert to [-180, 180]
#    return degrees


# Constants
latitude, longitude = -33.8352, 18.6510  # Durbanville, South Africa
tz = "Africa/Johannesburg"
# date = '2023-06-21'  # You can choose any date

# Create polar plot
plt.figure(figsize=(10, 10))
ax = plt.subplot(111, projection="polar")

# Limit theta to run from -180 to +180 degrees
ax.set_thetamin(-180)
ax.set_thetamax(180)


for date in flatten([[f'2023-{i:02d}-{int(j)}' for j in np.linspace(1, 31, 10)] for i in range(1, 13)]):
    # Generate time range for the specific date
    try:
        times = pd.date_range(date, freq="5min", periods=288, tz=tz)
    except pd._libs.tslibs.parsing.DateParseError:
        continue

    # Calculate solar position
    #solpos = solarposition.get_solarposition(times, latitude, longitude)
    solpos = [solar_az_el(i.year, i.month, i.day, i.hour, i.minute, i.second - i.utcoffset().seconds, latitude, longitude, 0) for i in times]

    solpos = [list(sp)+[times[i]] for i, sp in enumerate(solpos) if sp[1] >= 0]
    # Filter out times when the sun is below the horizon
    #solpos = solpos[solpos["elevation"] >= 0]

    # Normalize colors
    norm = plt.Normalize(vmin=0, vmax=23)

    # Convert azimuth to radians
    azimuth_radians = np.radians([to_180_form(i[0]) for i in solpos])

    # Plot the sun path
    sc = ax.scatter(
        azimuth_radians,
        [to_180_form(90 - i[1]) for i in solpos],
        c=[i[2].hour for i in solpos],
        cmap="bwr",
        norm=norm,
        s=10,
    )


# Customize the tick labels
ticks = np.linspace(-180, 180, 37)
ax.set_xticks(np.radians(ticks))
ax.set_xticklabels([str(int(tick)) for tick in ticks])

# Set the direction and labels
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_yticklabels([])

plt.colorbar(sc, label="Hour of the Day", orientation="horizontal")
plt.title("Solar Path for Durbanville, South Africa on ")  # + date)
plt.show()
