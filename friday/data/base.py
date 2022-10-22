from friday.utils import (get_processed_dates, get_simulation_end_date,
                          timeframe)


class Base:
    """Base class for data functionality for Friday."""

    def __init__(self, 
                start, 
                end, 
                simulation_start,
                days,
                api, 
                config, 
                interval: str = '1d'
                ) -> None:
        """Initializes the given parameters and stores them as an instance attribute to be used by any class inheriting its properties.
        Parameters
        start: str (Format %Y-%m-%d)
        end: str (Format %Y-%m-%d)
        api: Alpaca REST API.
        config: Configuration file for various predefined data attributes.
        interval: str (Supported trading intervals - e.g. '1m', '45m', '1h', '1d' etc.)"""

        self.api = api
        self.config = config
        self.start = start
        self.end = end
        #self.start, self.end, self.available_start = get_processed_dates(start, end) # Calls for get_processed_date from utils/datetime_.py
        self.simulation_start = simulation_start
        self.days = days
        self.simulation_end = get_simulation_end_date(self.simulation_start, days)  # Generates an end date going for x number of 'days' in the future
        self.interval = interval
        self.symbols = config['assets']['symbols']
        self.trading_timeframe = timeframe(self.interval)                           # Calls for timeframe from utils/trading_.py
