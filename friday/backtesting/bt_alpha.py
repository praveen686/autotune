# TODO Proper Documentation and commenting

from alpaca_trade_api import REST, TimeFrame, TimeFrameUnit
from datetime import datetime, timedelta
from rich import print
import numpy as np
import pandas as pd
import pandas_market_calendars as mcal
import vectorbt as vbt

from functools import partial
import json

# Sets maximum number of rows to be displayed in pandas data_types.
pd.set_option('display.max_rows', None)

with open(r'config.json') as config:
    config = json.load(config)

api = REST(config['alpaca']['key'], config['alpaca']['secret'], api_version='v2')

class BacktestingAlpha:
    """BacktestingAlpha class based on vectorbt."""

    def __init__(self, start, end) -> None:
        """Initializes the class and pre-sets the following values as instance variables."""

        # Stocks under consideration
        self.symbols = ['SPY', 'TQQQ', 'SPXL', 'UVXY', 'SQQQ', 'BSV', 'TECL']
        # Trading timeframe
        self.interval = '1d'
        self.start_date = start
        self.end_date = end
        # Stock currently in position
        self.in_trade = None
        # Trade status
        self.position_status = 'closed'

    def data_collection(self) -> pd.Series:
        """Method to fetch market data from yahoo finance. Collectes OHLCV data and calculates
        Moving Average(MA) and Relative Strength Index(RSI) with window size 20, 200 for MA and
        10 for RSI."""

        _open = pd.DataFrame(columns=self.symbols)
        _high = pd.DataFrame(columns=self.symbols)
        _low = pd.DataFrame(columns=self.symbols)
        _close = pd.DataFrame(columns=self.symbols)
        _volume = pd.DataFrame(columns=self.symbols)
        
        timeframe = TimeFrame(1, TimeFrameUnit.Day)
        nyse = mcal.get_calendar('NYSE')
        adjusted = datetime.strptime(self.start_date, "%Y-%m-%d") - timedelta(365)
        early = nyse.schedule(start_date=adjusted, end_date=self.start_date)
        active_days = mcal.date_range(early, frequency='1D')

        self.start_date = datetime.strftime(active_days[-201], "%Y-%m-%d")

        for symbol in self.symbols:
            alpaca_data = api.get_bars(symbol, TimeFrame.Day, start=self.start_date, end=self.end_date,  adjustment='split', limit=10000).df
            _open[symbol] = alpaca_data['open']
            _high[symbol] = alpaca_data['high']
            _low[symbol] = alpaca_data['low']
            _close[symbol] = alpaca_data['close']
            _volume[symbol] = alpaca_data['volume']
            alpaca_data.to_csv(f"friday\\backtesting\\historicaldata\\{symbol}.csv")

        ohlcv = {'Open': _open, 'High': _high, 'Low': _low, 'Close': _close}

        # Indicator calculation
        # Moving Average(ma) and Relative Strength Index(rsi)
        ma = vbt.MA.run(ohlcv['Close'], window=[20, 200]).ma
        rsi = vbt.talib('rsi').run(ohlcv['Close'], timeperiod=10).real     # talib, vbt presents inaccurate results

        # Initial 200 values are dropped from all pandas series as the
        # highest window size observed is 200 for the moving average.
        # This fixes the inaccurate entries caused due to NaN values.
        ohlcv['Open'].drop(index=ohlcv['Open'].index[:200], inplace=True)
        ohlcv['Close'].drop(index=ohlcv['Close'].index[:200], inplace=True)
        ma.drop(index=ma.index[:200], inplace=True)
        rsi.drop(index=rsi.index[:200], inplace=True)
        ma.to_csv(f"friday\\backtesting\\historicaldata\\ind_ma.csv")
        rsi.to_csv(f"friday\\backtesting\\historicaldata\\ind_rsi.csv")

        # Returns the values of Close, Open, Moving Average and Relative
        # Strength Index.
        return ohlcv['Close'], ohlcv['Open'], ma, rsi

    def _signal_generator(self, symbol, en, ex, idx) -> None:

        en[symbol][idx] = 1

        if idx == 0:
            if en[symbol][idx] == 1:
                self.in_trade = symbol
                self.position_status = 'opened'

        elif idx > 0:
            if np.isnan(en[symbol][idx-1]):
                ex[self.in_trade][idx] = 1
                self.position_status = 'closed'

            if en[symbol][idx] == 1 and self.position_status == 'closed':
                self.position_status = 'opened'
            else:
                en[symbol][idx] = -1
                ex[self.in_trade][idx] = -1

        self.in_trade = symbol

    def strategy(self):

        close_price, open_price, ma, rsi = self.data_collection()
        entries = pd.DataFrame(np.nan, index=close_price.index, columns=self.symbols)
        exits = pd.DataFrame(np.nan, index=close_price.index, columns=self.symbols)

        for x in range(len(close_price['SPY'])):
            if close_price['SPY'][x] > ma[200]['SPY'][x]:
                if rsi[10]['TQQQ'][x] > 79:
                    self._signal_generator('UVXY', entries, exits, x)

                else:
                    if rsi[10]['SPXL'][x] > 80:
                        self._signal_generator('UVXY', entries, exits, x)

                    else:
                        self._signal_generator('TQQQ', entries, exits, x)

            else:
                if rsi[10]['TQQQ'][x] < 31:
                    self._signal_generator('TECL', entries, exits, x)

                else:
                    if rsi[10]['SPY'][x] < 30:
                        self._signal_generator('SPXL', entries, exits, x)

                    else:
                        if rsi[10]['UVXY'][x] > 74:
                            if rsi[10]['UVXY'][x] > 84:
                                if close_price['TQQQ'][x] > ma[20]['TQQQ'][x]:
                                    if rsi[10]['SQQQ'][x] < 31:
                                        self._signal_generator('SQQQ', entries, exits, x)

                                    else:
                                        self._signal_generator('TQQQ', entries, exits, x)
                                
                                else:
                                    if rsi[10]['SQQQ'][x] > rsi[10]['BSV'][x]:
                                        self._signal_generator('SQQQ', entries, exits, x)

                                    else:
                                        self._signal_generator('BSV', entries, exits, x)

                            else:
                                self._signal_generator('UVXY', entries, exits, x)

                        else:
                            if close_price['TQQQ'][x] > ma[20]['TQQQ'][x]:
                                if rsi[10]['SQQQ'][x] < 31:
                                    self._signal_generator('SQQQ', entries, exits, x)

                                else:
                                    self._signal_generator('TQQQ', entries, exits, x)

                            else:
                                if rsi[10]['SQQQ'][x] > rsi[10]['BSV'][x]:
                                    self._signal_generator('SQQQ', entries, exits, x)

                                else:
                                    self._signal_generator('BSV', entries, exits, x)

        entries.replace({1: True, np.nan: False, -1: False}, inplace=True)
        exits.replace({1: True, np.nan: False, -1: False}, inplace=True)

        return close_price, open_price, entries, exits


def main():
    ba = BacktestingAlpha('2016-01-01', '2022-10-07')
    close_price, open_price, en, ex = ba.strategy()

    en = en.values.tolist()
    ex = ex.values.tolist()
    pf = vbt.Portfolio.from_signals(
        close=close_price,
        entries=en,
        exits=ex,
        price=close_price,   # changed from open_price
        cash_sharing=True,
        val_price=close_price.vbt.fshift(1),
        slippage=0.0,        # set slippage
        init_cash=10000,     # initial cash from 1000 to 10000
        group_by=True,
        call_seq='auto',
        freq='d')

    pf.orders.records_readable.to_csv('userdata/signal_analysis.csv')
    print(pf.orders.records_readable)
    print(pf.stats())
    print(pf.returns_stats(group_by=True))
    print(pf.total_return(group_by=False))

    def plot_orders(portfolio, column=None, add_trace_kwargs=None, fig=None):
        portfolio.orders.plot(column=column, add_trace_kwargs=add_trace_kwargs, fig=fig)

    pf.plot(subplots=[
        (f'{ba.symbols[0]}_Orders', dict(
            title=f"Orders ({ba.symbols[0]})",
            check_is_not_grouped=False,
            plot_func=partial(plot_orders, column=ba.symbols[0]),
            pass_column=False
        )),
        (f'{ba.symbols[1]}_Orders', dict(
            title=f"Orders ({ba.symbols[1]})",
            check_is_not_grouped=False,
            plot_func=partial(plot_orders, column=ba.symbols[1]),
            pass_column=False
        )),
        (f'{ba.symbols[2]}_Orders', dict(
            title=f"Orders ({ba.symbols[2]})",
            check_is_not_grouped=False,
            plot_func=partial(plot_orders, column=ba.symbols[2]),
            pass_column=False
        )),
        (f'{ba.symbols[3]}_Orders', dict(
            title=f"Orders ({ba.symbols[3]})",
            check_is_not_grouped=False,
            plot_func=partial(plot_orders, column=ba.symbols[3]),
            pass_column=False
        )),
        (f'{ba.symbols[4]}_Orders', dict(
            title=f"Orders ({ba.symbols[4]})",
            check_is_not_grouped=False,
            plot_func=partial(plot_orders, column=ba.symbols[4]),
            pass_column=False
        )),
        (f'{ba.symbols[5]}_Orders', dict(
            title=f"Orders ({ba.symbols[5]})",
            check_is_not_grouped=False,
            plot_func=partial(plot_orders, column=ba.symbols[5]),
            pass_column=False
        )),
        (f'{ba.symbols[6]}_Orders', dict(
            title=f"Orders ({ba.symbols[6]})",
            check_is_not_grouped=False,
            plot_func=partial(plot_orders, column=ba.symbols[6]),
            pass_column=False
        ))
    ]).show()


if __name__ == '__main__':
    main()
