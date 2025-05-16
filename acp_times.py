"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_alg.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#  Note for CIS 322 Fall 2016:
#  You MUST provide the following two functions
#  with these signatures, so that I can write
#  automated tests for grading.  You must keep
#  these signatures even if you don't use all the
#  same arguments.  Arguments are explained in the
#  javadoc comments.
#
MAXIMUM_SPEEDS = {
        200: 34,
        400: 32,
        600: 30,
        1000: 28,
        1300: 26
}
MINIMUM_SPEEDS = {
        600: 15,
        1000: 11.428,
        1300: 13.333
}
DEFAULT_OPEN = {
        200: (5, 33),
        300: (9, 0),
        400: (12, 8),
        600: (18, 48),
        1000: (39, 0)
}
DEFAULT_CLOSE = {
        200: (13, 30),
        300: (20, 0),
        400: (27, 0),
        600: (40, 0),
        1000: (75, 0)
}


def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
       brevet_dist_km: number, the nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control open time.
       This will be in the same time zone as the brevet start time.
    """
    speeds = list(MAXIMUM_SPEEDS.keys())
    start_time = arrow.get(brevet_start_time)
    if control_dist_km >= brevet_dist_km:
        hour_open, minute_open = DEFAULT_OPEN[brevet_dist_km]
        open_time = start_time.shift(hours=hour_open, minutes=minute_open)
    else:
        for i in range(len(speeds)):
            if control_dist_km <= speeds[i]: 
                time = control_dist_km / MAXIMUM_SPEEDS[speeds[i]]
                logger.debug(f"speed = {MAXIMUM_SPEEDS[speeds[i]]}")
                hour_change = int(time)
                minute_change = int((time - hour_change) * 60)
                open_time = start_time.shift(hours=hour_change, minutes=minute_change)
                break
    
    return open_time.isoformat()

def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
          brevet_dist_km: number, the nominal distance of the brevet
          in kilometers, which must be one of 200, 300, 400, 600, or 1000
          (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control close time.
       This will be in the same time zone as the brevet start time.
    """
    start_time = arrow.get(brevet_start_time)
    speeds = list(MINIMUM_SPEEDS.keys())
    if (control_dist_km == 0):
        close_time = start_time.shift(hours=1)
    elif control_dist_km >= brevet_dist_km:
        hour_close, minute_close = DEFAULT_CLOSE[brevet_dist_km]
        close_time = start_time.shift(hours=hour_close, minutes=minute_close)
    else:    
        for i in range(len(speeds)):
            if control_dist_km <= speeds[i]:
                time = control_dist_km / MINIMUM_SPEEDS[speeds[i]]
                hour_change = int(time)
                minute_change = int((time - hour_change) * 60)
                close_time = start_time.shift(hours=hour_change, minutes=minute_change)
                break

    return close_time.isoformat()
