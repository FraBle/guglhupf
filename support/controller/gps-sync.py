#!/usr/bin/env python3
"""Integration with gpsd through separate thread.

/usr/local/bin/gps-sync
"""
import math
import os
from pathlib import Path
from time import sleep
from types import MappingProxyType

import gps


LATITUDE = 'lat'
LONGITUDE = 'lon'
COMPASS = MappingProxyType({
    LATITUDE: ('N', 'S'),
    LONGITUDE: ('E', 'W'),
})
OUTPUT_FILE = Path('/mnt/recordings/gps.txt')


class GpsCoordinates(object):
    """Wrapper for GPS coordinates (latitude/longitude).

    Attributes:
        lat: GPS latitude.
        lon: GPS longitude.
    """

    def __init__(self) -> None:
        """Initialize latitude, longitude, and internal lock."""
        self.lat: float = 0
        self.lon: float = 0

    def update(self, lat: float, lon: float) -> None:
        """Thread-safe update of latitude & longitude.

        Args:
            lat: GPS latitude.
            lon: GPS longitude.
        """
        self.lat = lat
        self.lon = lon

    def __str__(self) -> str:
        """Thread-safe string representation in DMS.

        DMS = degrees, minutes, and seconds

        Returns:
            DMS-converted GPS coordinates.
        """
        dms = '{0} {1}'.format(
            deg_to_dms(self.lat, unit=LATITUDE),
            deg_to_dms(self.lon, unit=LONGITUDE),
        )
        return dms


def deg_to_dms(deg: float, unit: str) -> str:  # noqa: WPS210
    """Convert decimal degrees to DMS.

    Based on https://stackoverflow.com/a/52371976
    DMS = degrees, minutes, and seconds

    Args:
        deg: Degree in decimal
        unit: Coordinates unit ('lat' or 'lon')

    Returns:
        DMS-converted GPS coordinates as string.
    """
    decimals, number = math.modf(deg)
    degrees = int(number)
    minutes = int(decimals * 60)
    seconds = (deg - degrees - minutes / 60) * 60 * 60

    return '{0}°{1:02}\'{2:04.1f}"{3}'.format(
        str(abs(degrees)).zfill(2 if unit == LATITUDE else 3),
        abs(minutes),
        abs(seconds),
        COMPASS[unit][0 if degrees >= 0 else 1],
    )


def main() -> None:
    """Start the main loop to process gpsd data."""
    # WATCH_ENABLE   # enable streaming
    # WATCH_NEWSTYLE # force JSON streaming
    gpsd = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    gps_coordinates = GpsCoordinates()

    with open(OUTPUT_FILE, 'w') as output_writer:
        while True:  # noqa: WPS457
            gps_data = next(gpsd)
            if gps_data.get('class') == 'TPV':
                if gps_data.get(LATITUDE) and gps_data.get(LONGITUDE):
                    gps_coordinates.update(
                        gps_data.get(LATITUDE),
                        gps_data.get(LONGITUDE),
                    )
            output_writer.seek(0)
            output_writer.write(str(gps_coordinates))
            output_writer.flush()
            os.fsync(output_writer)


if __name__ == "__main__":
    main()
