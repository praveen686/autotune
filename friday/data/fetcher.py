from time import time

import pandas as pd

from .synthesizer import Synthesizer


class Fetcher(Synthesizer):
    """Fetcher class for data generation for Friday. Inherits the properties of Synthesizer class which is inheriting Base."""

    def __init__(self, 
                start, 
                end, 
                simulation_start, 
                days, 
                api, 
                config, 
                interval: str = '1d') -> None:
        super().__init__(start, end, simulation_start, days, api, config, interval)

        """See friday.data.base for params.
        Synthesizer generates future data till a specified date.
        Usage:
            >>> f = Fetcher('2018-01-01', '2020-01-01', api, config)
            >>> f.historical_data()
                                        SPY    TQQQ   SPXL    UVXY     SQQQ    BSV    TECL
            timestamp
            2017-03-16 04:00:00+00:00  238.48   7.267  32.40  3340.0  3761.00  79.44   6.708
            2017-03-17 04:00:00+00:00  237.03   7.249  32.21  3264.0  3772.00  79.50   6.720
            2017-03-20 04:00:00+00:00  236.77   7.271  32.09  3270.0  3757.00  79.55   6.737
            2017-03-21 04:00:00+00:00  233.73   6.947  30.88  3512.0  3926.00  79.65   6.459
            2017-03-22 04:00:00+00:00  234.28   7.083  31.05  3546.0  3850.00  79.68   6.577
            ...                           ...     ...    ...     ...      ...    ...     ...
            2019-12-24 05:00:00+00:00  321.23  21.460  65.78   126.8   565.25  80.47  23.900
            2019-12-26 05:00:00+00:00  322.94  22.020  66.78   126.4   550.25  80.47  24.400
            2019-12-27 05:00:00+00:00  322.86  21.950  66.74   130.3   552.25  80.57  24.430
            2019-12-30 05:00:00+00:00  321.08  21.520  65.57   137.4   563.00  80.63  24.000
            2019-12-31 05:00:00+00:00  321.86  21.640  66.08   128.9   559.75  80.61  24.180

            [704 rows x 7 columns]"""

        super().__init__(start, end, simulation_start, days, api, config, interval) # super() functions enables the parent class functionality inside the child class

    def historical_data(self,
                        adjustment: str = 'split',
                        max_limit: int = 10000,
                        project_future: bool = False,
                        write_to_csv: bool = False
                        ):
        """Historical data function downloads the historical data till the specified date, has an optional functionality to call synthetic_data() from within this function.
        Parameters:
        adjustment: str = 'split'
        max_limit: int = 10000 (DataFrame values to be fetched, cannot exceed 10000)
        project_future: bool = False (True will call the synthetic_data() functionality for future data. See friday.data.synthesizer)
        write_to_csv: bool = False. (True will generate a csv file with the closing prices from historical data till the projected date."""

        if project_future: # Checks for future projection requirement
            close = self.synthetic_data(adjustment=adjustment,
                                        max_limit=max_limit,
                                        write_to_csv=write_to_csv)
            
        else: # Else uses alpaca api to get close data for each symbol.
            close = pd.DataFrame(columns=self.symbols) # Empty dataframe with symbol tickers as columns
            alpaca_data = self.api.get_bars(self.symbols,
                                            self.trading_timeframe, 
                                            start=self.start,
                                            end=self.end, 
                                            adjustment=adjustment, 
                                            limit=max_limit).df.get(['close', 'symbol']) # Get data from alpaca api
            grouped_data = alpaca_data.groupby('symbol')

            for symbol in self.symbols:
                close[symbol] = grouped_data.get_group(symbol)['close']

        if write_to_csv:
            close.to_csv(f"close_data.csv") # Optional parameter to write in CSV

        return close