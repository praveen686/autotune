import numpy as np
import pandas as pd
import vectorbt as vbt


class Strategy:
    """BacktestingAlpha class based on vectorbt."""

    def __init__(self,
                 config) -> None:
        """Initializes the class and pre-sets the following values as instance variables."""

        # Stocks under consideration
        self.symbols = config['assets']['symbols']
        # Stock currently in position
        self.in_trade = None
        # Trade status
        self.position_status = 'closed'

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

    def strategy(self, data, days):
    
        ma = vbt.MA.run(data, window=[20, 200]).ma
        rsi = vbt.talib('rsi').run(data, timeperiod=10).real

        ma = ma.iloc[-days:]
        rsi = rsi.iloc[-days:]
        data = data.iloc[-days:]
        entries = pd.DataFrame(np.nan, index=data.index, columns=self.symbols)
        exits = pd.DataFrame(np.nan, index=data.index, columns=self.symbols)

        for y in range(len(data['SPY'])):
            if data['SPY'][y] > ma[200]['SPY'][y]:
                if rsi[10]['TQQQ'][y] > 79:
                    self._signal_generator('UVXY', entries, exits, y)

                else:
                    if rsi[10]['SPXL'][y] > 80:
                        self._signal_generator('UVXY', entries, exits, y)

                    else:
                        self._signal_generator('TQQQ', entries, exits, y)

            else:
                if rsi[10]['TQQQ'][y] < 31:
                    self._signal_generator('TECL', entries, exits, y)

                else:
                    if rsi[10]['SPY'][y] < 30:
                        self._signal_generator('SPXL', entries, exits, y)

                    else:
                        if rsi[10]['UVXY'][y] > 74:
                            if rsi[10]['UVXY'][y] > 84:
                                if data['TQQQ'][y] > ma[20]['TQQQ'][y]:
                                    if rsi[10]['SQQQ'][y] < 31:
                                        self._signal_generator('SQQQ', entries, exits, y)

                                    else:
                                        self._signal_generator('TQQQ', entries, exits, y)
                                
                                else:
                                    if rsi[10]['SQQQ'][y] > rsi[10]['BSV'][y]:
                                        self._signal_generator('SQQQ', entries, exits, y)

                                    else:
                                        self._signal_generator('BSV', entries, exits, y)

                            else:
                                self._signal_generator('UVXY', entries, exits, y)

                        else:
                            if data['TQQQ'][y] > ma[20]['TQQQ'][y]:
                                if rsi[10]['SQQQ'][y] < 31:
                                    self._signal_generator('SQQQ', entries, exits, y)

                                else:
                                    self._signal_generator('TQQQ', entries, exits, y)

                            else:
                                if rsi[10]['SQQQ'][y] > rsi[10]['BSV'][y]:
                                    self._signal_generator('SQQQ', entries, exits, y)

                                else:
                                    self._signal_generator('BSV', entries, exits, y)

        entries.replace({1: True, np.nan: False, -1: False}, inplace=True)
        exits.replace({1: True, np.nan: False, -1: False}, inplace=True)
        entries = entries.values.tolist()
        exits = exits.values.tolist()    

        return data, entries, exits