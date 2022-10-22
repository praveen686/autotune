"""Trading utilities for Friday."""

from alpaca_trade_api import TimeFrame, TimeFrameUnit


def timeframe(interval):
    """Converts trading interval to Alpaca's TimeFrame object.
    Parameters:
    interval: str (Supported trading intervals - e.g. '1m', '45m', '1h', '1d' etc.)"""

    # Extracts the number (1, 3, 5, 45 etc.) from the assigned interval
    amount = int(interval[:-1]) 
    # Extracts the string (m, h, d, w, M) from the assigned interval
    unit = interval[-1]         

    if unit == 'm':                     # m = minute
        unit = TimeFrameUnit.Minute
    elif unit.lower() == 'h':           # h = hour
        unit = TimeFrameUnit.Hour
    elif unit.lower() == 'd':           # d = day
        unit = TimeFrameUnit.Day
    elif unit.lower() == 'w':           # w = week
        unit = TimeFrameUnit.Week
    elif unit == 'M':                   # M = Month
        unit = TimeFrameUnit.Month

    return TimeFrame(amount, unit)
