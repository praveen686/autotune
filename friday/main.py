"""
Main Friday script.
"""
import json

import numpy as np
import pandas as pd
import plotly.express as px
import vectorbt as vbt
from alpaca_trade_api import REST
from rich import print

from friday.data import Fetcher, Synthesizer
from friday.strategies import Strategy

# Sets maximum number of rows to be displayed in pandas data_types.
pd.set_option('display.max_rows', None)


def main():

    with open(r'config.json') as config: # Reads config.json
        config = json.load(config)       # Loads the variable attributes in config   
    api = REST(config['alpaca']['key'], config['alpaca']['secret'], api_version='v2')

    # _range: number of future simulations to generate
    _range = range(5)

    # start: start of window that will be used to gather "synthetic" data, for forward-walk
    # end: end of "synthetic" data window.
    # simulation_start: when to start calulating the potfolio gain. past dates will use real data.
    s = Synthesizer(start='2022-06-17', end='2022-08-17', simulation_start='2022-10-17', days=15, api=api, config=config)
    iterables = [[x for x in _range], ["SPY", "TQQQ", "SPXL", "UVXY", "SQQQ", "BSV", "TECL"]]
    index = pd.MultiIndex.from_product(iterables)
    result = pd.DataFrame(columns=index)
    cum_returns = pd.DataFrame(columns=_range)
    spy_plot = pd.DataFrame(columns=_range)

    for x in _range:
        data = s.synthetic_data()
        ste = Strategy(config)
        data, entries, exits = ste.strategy(data, s.days)

        pf = vbt.Portfolio.from_signals(
            close=data,
            entries=entries,
            exits=exits,
            price=data,
            cash_sharing=True,
            val_price=data.vbt.fshift(1),
            slippage=0.0,       # set slippage
            init_cash=100000,   # initial cash from 1000 to 10000
            group_by=True,
            call_seq='auto',
            freq='d')

        print(pf.stats())
        cum_returns[x] = pf.cumulative_returns(group_by=True)
        spy_plot[x] = data['SPY']

        # if x == 0:
        #     worst_drawdown = abs(pf.drawdown(group_by=True).min()) * 100
        #     temp_save_plot = pf.plot_drawdowns(group_by=True).show()

        # elif x > 0:
        #     if worst_drawdown < (abs(pf.drawdown(group_by=True).min()) * 100):
        #         worst_drawdown = abs(pf.drawdown(group_by=True).min()) * 100
        #         temp_save_plot = pf.plot_drawdowns(group_by=True).show()

    fig1 = px.line(cum_returns, x=cum_returns.index, y=cum_returns.columns[:], title='Cumulative Returns')
    fig1.add_hline(y=0, line_dash="dot")
    fig2 = px.line(spy_plot, x=spy_plot.index, y=spy_plot.columns[:], title='SPY')
    fig1.write_html("cumulative.html")
    fig2.write_html("spy.html")
    #temp_save_plot.show()
    fig1.show()
    fig2.show()

if __name__ == '__main__':
    # __name__ == '__main__' checks if a file is imported as a module or not.
    # If the file is imported the function will not run.
    main()