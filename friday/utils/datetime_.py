"""Datetime utilities for Friday."""

from datetime import datetime, timedelta

import pandas_market_calendars as mcal
import pytz


def get_future_dates(start,
                     simulation_end,
                     interval: str = '1d'):
    """Fetches the active trading dates till simulation_end to get future trading dates.
    Parameters:
    start: str
    simulation_end: str (Any date in the future. Format %Y-%m-%d)
    interval: str (Supported trading intervals - e.g. '1m', '45m', '1h', '1d' etc.)"""
    
    tz = pytz.timezone('US/Eastern')                                            # Gets the New_york timezone
    nyse = mcal.get_calendar('NYSE')
    early = nyse.schedule(start_date=start, end_date=simulation_end)            # Gets the scheduled dates between the given time range
    active_days = mcal.date_range(early, frequency=interval).normalize()        # Normalizes the time unit to easily compare with future time indexes

    current_date = datetime.now(tz).date()                                      # Gets the current date for the selected timezone
    simulation_end = datetime.strptime(simulation_end, '%Y-%m-%d').date()       # Converts projection date into datetime format then extracts the date from it

    if str(current_date) in active_days:
        loc = active_days.get_loc(str(current_date))                            # Gets the index location of the current date in the NYSE market calendar
    else:
        int_day = current_date.isoweekday()                                     # Checks if the current date is a weekday, returns 1 for Monday ... 7 for Sunday.
        adjusted_date = current_date + timedelta(8-int_day)                     # Offsets the date (e.g., If current days results as a Saturday, 
                                                                                # int_day = 6 Hence the current date will shift forward  2 days)
        loc = active_days.get_loc(str(adjusted_date))                           # Gets the index location of the adjusted date in the NYSE market calendar

    future_index = [active_days[x] for x in range(loc, len(active_days))]       # Returns a list of future dates that will be active uptil projection date

    return future_index

def get_processed_dates(start: str, 
                        end: str, 
                        available_start: str = '2015-12-01', 
                        interval: str = '1d', 
                        highest_window: int = 200):
    """Adjusts the start and end date to be fed into the trading system.
    Parameters:
    start: str (Format %Y-%m-%d)
    end: str (Format %Y-%m-%d)
    available_start: str = '2015-12-01' (Earliest starting point to fetch data from. Format %Y-%m-%d)
    interval: str (Supported trading intervals - e.g. '1m', '45m', '1h', '1d' etc.)
    highest_window: int = 200 (Highest window used in the specified indicators. 
    (e.g. If the strategy includes 14-Day RSI and a 9-Day Moving Average. the highest_window will be set to 14)"""

    tz = pytz.timezone('US/Eastern')                                    # Gets the New_york timezone

    nyse = mcal.get_calendar('NYSE')
    early = nyse.schedule(start_date=available_start, end_date='2022-01-01')   # Gets the scheduled dates between the given time range
    active_days = mcal.date_range(early, frequency=interval)

    current_date = datetime.now(tz).date()                              # Gets the current date for the selected timezone
    end_date = datetime.strptime(end, '%Y-%m-%d').date()                # Converts projection date into datetime format then extracts the date from it

    if (c := current_date.isoweekday()) > 5:                            # Checks if the current date is a weekend, returns 1 for Monday ... 7 for Sunday.
        current_date = current_date - timedelta(abs(5-c))               # Offsets the date (e.g., If current days results as a Saturday, 
                                                                        # c = 6 Hence the current date will shift forward 1 day. Note the absolute func.)
    else: 
        current_date = current_date - timedelta(1)                      # Offsets the date by negative 1 if it is a weekday

    if end_date > current_date: 
        adjusted_end = current_date 
    else:
        adjusted_end = end

    # Converts the date in a string format
    start = str(active_days[-(highest_window+1)].date())                 # Array slicing to get the date n days in the past.
    end = str(adjusted_end)

    return start, end, available_start

def get_simulation_end_date(start, 
                            days,
                            interval: str = '1d'):

    adjusted_start = str((datetime.strptime(start, '%Y-%m-%d') - timedelta(1)).date()) # Offset the date by 1
    nyse = mcal.get_calendar('NYSE')
    early = nyse.schedule(start_date=adjusted_start, end_date='2030-01-01') # Gets the scheduled dates between the given time range
    active_days = mcal.date_range(early, frequency=interval)
    simulation_end_date = str(active_days[days].date())

    return simulation_end_date
