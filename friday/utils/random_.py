"""Random generation utilities for Friday."""

import random
from datetime import datetime

import pandas_market_calendars as mcal


def generate_random_market_dates(start,
                                 end,
                                 future_dates,
                                 interval: str = '1d'):
    """Fetches the active trading dates for the market and generates random dates to 
    to form synthetic data.
    Parameters:
    projection_date: str (Any date in the future. Format %Y-%m-%d)
    available_start: str = '2015-12-01' (Earliest starting point to fetch data from. Format %Y-%m-%d)
    interval: str (Supported trading intervals - e.g. '1m', '45m', '1h', '1d' etc.)"""
    
    nyse = mcal.get_calendar('NYSE')
    early = nyse.schedule(start_date=start, end_date=end)                   # Gets the scheduled dates between the given time range
    active_days = mcal.date_range(early, frequency=interval).normalize()    # Normalizes the time unit to easily compare with future time indexes

    end = datetime.strptime(end, '%Y-%m-%d').date()                         # Converts projection date into datetime format then extracts the date from it

    loc = active_days.get_loc(str(end))
    randomlist = random.sample(range(1, loc), len(future_dates))            # Returns a random sample of index locations that can be used to get random dates

    selected_random_dates = []

    for x in randomlist:
        idx = active_days.get_loc(active_days[x])
        selected_random_dates.append(active_days[idx-1])
        selected_random_dates.append(active_days[idx])

    return selected_random_dates