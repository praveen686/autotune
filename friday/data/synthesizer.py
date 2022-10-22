import numpy as np
import pandas as pd
import vectorbt as vbt

from friday.utils import generate_random_market_dates, get_future_dates

from .base import Base


class Synthesizer(Base):
    """Synthesizer class for synthetic data projection for Friday. Inherits the properties of Base class."""

    def __init__(self, 
                start, 
                end, 
                simulation_start, 
                days, 
                api, config, 
                interval: str = '1d') -> None:
        """See friday.data.base for params.
        Synthesizer generates future data till a specified date.
        Usage:
            >>> s = Synthesizer('2016-01-01', '2023-01-01', api, config)
            >>> s.synthetic_data()
                                            SPY       TQQQ       SPXL       UVXY       SQQQ        BSV       TECL
            2015-12-01 00:00:00+00:00      210.68      5.201      22.69   123150.0     7052.0      79.95      4.019
            2015-12-02 00:00:00+00:00      208.54      5.106      21.97   131800.0     7180.0      79.88      3.945
            2015-12-03 00:00:00+00:00      205.58      4.846      21.05   151000.0     7548.0       79.8      3.795
            2015-12-04 00:00:00+00:00      209.66      5.179      22.27   123800.0     7020.0       79.8      4.068
            2015-12-07 00:00:00+00:00      208.27      5.115      21.85   129850.0     7112.0      79.86      4.015
            ...                               ...        ...        ...        ...        ...        ...        ...
            2022-12-23 00:00:00+00:00  363.179272  16.479288  55.409949  11.835514  62.980323  73.917243  20.393797
            2022-12-27 00:00:00+00:00  362.594951  16.346747  55.148185  11.907071   63.43445  73.862334  20.118736
            2022-12-28 00:00:00+00:00   365.29778  16.570999  56.385405  10.959706  62.521286  73.890182   20.43521
            2022-12-29 00:00:00+00:00  362.674192  16.126394   55.16132  12.156413  64.206622  73.973277  19.876617
            2022-12-30 00:00:00+00:00  341.766423  13.753501  45.595294  18.254652  73.841664   73.88411   16.43349

            [1784 rows x 7 columns]"""

        super().__init__(start, end, simulation_start, days, api, config, interval) # super() functions enables the parent class functionality inside the child class
        self.data_stored = False

    def synthetic_data(self,
                       adjustment: str = 'split',
                       max_limit: int = 10000,
                       write_to_csv: bool = False) -> pd.DataFrame:
        """Synthetic data function downloads the historical data till the current date then projects into the future with a custom calculation method and combines the results.
        Parameters:
        adjustment: str = 'split'
        max_limit: int = 10000 (DataFrame values to be fetched, cannot exceed 10000)
        write_to_csv: bool = False. (True will generate a csv file with the closing prices from historical data till the projected date."""

        close = pd.DataFrame(columns=self.symbols) # Empty dataframe with symbol tickers as columns
        future_index = get_future_dates(self.start, self.simulation_end)
        selected_random_dates = generate_random_market_dates(self.start, self.end, future_index) # Returns random dates. See friday.utils.random_
        fi = pd.DataFrame(index=future_index, columns=['close'], dtype='float') # Empty dataframe with future dates as index and close as column value

        # For loop that gets close for each symbol, calculates synthetic prices for future dates and returns the result.
        for symbol in self.symbols:

            alpaca_data = self.api.get_bars(symbol, self.trading_timeframe, start=self.start, adjustment=adjustment, limit=max_limit).df.get(['close']) # Get data from alpaca api
            alpaca_data.index = alpaca_data.index.normalize() # Normalizes the time unit to easily compare with future time indexes
            random_alpaca_data = alpaca_data.loc[selected_random_dates] # Aligns the data for the random dates in a separate dataframe for the percent calculation
            random_percent_change = random_alpaca_data.pct_change().iloc[::-2][::-1] # Uses a pandas built-in pct_change() function which returns the percentage change between every row, then
                                                                                     # the dataframe is flipped and every 2 row is skipped using [::-2] and then it is flipped back with [::-1]

            for x in range(len(future_index)):
                if x == 0:
                    result = (alpaca_data.iloc[-1] * (1 + random_percent_change.iloc[0])).iloc[-1] # Synthetic price calculation
                    fi.iloc[x] = result # Store the result in the dataframe

                elif x > 0:
                    result = (fi.iloc[x-1] * (1 + random_percent_change.iloc[x]))
                    fi.iloc[x] = result # Store the result in the dataframe

            projected_data = pd.concat([alpaca_data, fi]) # Concatenates the result
            close[symbol] = projected_data # Stores the result in a dataframe

        if write_to_csv: # Optional parameter to write in CSV
            close.to_csv(f"close_data.csv")
        
        return close
        