from geopy.geocoders import Nominatim
import pandas as pd
import pvlib
from timezonefinder import TimezoneFinder

def get_solar_position(date, latitude, longitude):
    """
    Calculate solar position (azimuth, elevation) for a given date and geographic coordinates.
    
    Parameters:
    - date (str): Date for which to calculate solar position in "YYYY-MM-DD" format.
    - latitude (float): Latitude of the location in decimal degrees.
    - longitude (float): Longitude of the location in decimal degrees.
    
    Returns:
    - pd.DataFrame: DataFrame containing azimuth, elevation, and time for every minute
                     from sunrise to sunset. Time is used as the DataFrame index.
    """
    tf = TimezoneFinder()
    tz = tf.timezone_at(lat=latitude, lng=longitude)

    times = pd.date_range(start=f'{date} 00:00:00', end=f'{date} 23:59:59', freq='1min', tz=tz)
    
    # Get solar position
    solar_position = pvlib.solarposition.get_solarposition(
        times, latitude, longitude#, tz=tz
    )
    solar_position["time"] = times
    
    # Filter times between sunrise and sunset (elevation >= 0)
    solar_position = solar_position[solar_position['elevation'] >= 0]

    return solar_position[['azimuth', 'elevation', "time"]]