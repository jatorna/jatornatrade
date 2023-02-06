from trading_engine.Event import SignalEvent
from trading_engine.strategies.Strategy import Strategy
from trading_engine.Event import EventType
from subprojects.types.Common import *
import datetime
import subprojects.misc.LowLevelFuncions as llw
from subprojects.algorithm.TechnicalIndicators import *

logger = llw.script_logger('MAC STRATEGY')


class MovingAverageCrossStrategy(Strategy):
    """
    Mac Strategy
    """

    def __init__(self, symbol_list, events, config, strategy_id):

        self.status = False
        self.symbol_list = symbol_list
        self.events = events
        self.short_window = config.mac_strategy.short_window
        self.long_window = config.mac_strategy.long_window
        self.limit_orders = config.mac_strategy.limit_orders
        self.stop_loss = config.mac_strategy.stop_loss / 100
        self.take_profit = config.mac_strategy.take_profit / 100 + 1
        self.trailing_stop = config.mac_strategy.trailing_stop
        self.strategy_id = strategy_id
        self.signal_number = 0

        self.bought = self._calculate_initial_bought()
        self._check_strategy_status(config.strategies)

    def _calculate_initial_bought(self):

        bought = {}
        for s in self.symbol_list:
            bought[s] = PositionStatus.OUT
        return bought

    def _check_strategy_status(self, strategy_list):
        if self.strategy_id in strategy_list:
            self.status = True

    def calculate_signals(self, event, data_handler, current_date, orders_data, ppv):

        if self.status:
            price_type = 'close'

            if event.type == EventType('MARKET'):
                for symbol in self.symbol_list:

                    if not data_handler.has_current_price(symbol, current_date):
                        continue

                    if data_handler.get_current_tick(symbol, current_date, 'close') <= 0:
                        continue

                    bars = data_handler.get_current_data(symbol, current_date - datetime.timedelta(self.long_window*2),
                                                         current_date)

                    if bars is None:
                        continue

                    if len(bars[price_type].values) < self.long_window:
                        continue

                    if not bars.empty:
                        short_sma, long_sma = moving_average_con_div(bars[price_type].values, self.short_window,
                                                                     self.long_window)
                        dt = current_date
                        strength = 1.0
                        signal_detected = False

                        if short_sma > long_sma and self.bought[symbol] == PositionStatus.OUT:
                            self.signal_number += 1
                            signal_detected = True
                            action = OrderType.LONG
                            strategy_id = self.strategy_id + '{:04d}'.format(self.signal_number)

                        elif short_sma < long_sma and self.bought[symbol] == PositionStatus.LONG:
                            signal_detected = True
                            action = OrderType.EXIT
                            orders_data_tmp = orders_data[orders_data['Symbol'] == symbol]
                            orders_data_tmp = orders_data_tmp[orders_data_tmp['Direction'] == OrderDirection.BUY.value]
                            orders_data_tmp = orders_data_tmp[
                                orders_data_tmp['Order_ID'].str.contains(self.strategy_id)]
                            strategy_id = orders_data_tmp['Order_ID'].values[-1]

                        if signal_detected:
                            signal = SignalEvent(strategy_id, SignalType.MKT, symbol, dt, action, strength)
                            self.events.put(signal)
                            logger.debug('Signal detected! ' + current_date.strftime('%Y/%m/%d %H:%M:%S'))
                            logger.debug(action.value + ' ' + symbol + ' : ' + str(bars[price_type].values[-1]))
                            logger.debug('ID: ' + strategy_id)
