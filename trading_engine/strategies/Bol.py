from trading_engine.Event import SignalEvent
from trading_engine.strategies.Strategy import Strategy
from trading_engine.Event import EventType
from subprojects.types.Common import *
import datetime
import subprojects.misc.LowLevelFuncions as llw
from subprojects.algorithm.TechnicalIndicators import *

logger = llw.script_logger('BOL STRATEGY')


class BollingerStrategy(Strategy):
    """
    Bollinger Strategy
    """

    def __init__(self, symbol_list, events, config, strategy_id):

        self.status = False
        self.symbol_list = symbol_list
        self.events = events
        self.window = config.bol_strategy.window
        self.n = config.bol_strategy.n_std
        self.strategy_id = strategy_id
        self.allowed_signals = config.bol_strategy.allowed_signals
        self.limit_orders = config.bol_strategy.limit_orders
        self.stop_loss = config.bol_strategy.stop_loss / 100
        self.trailing_stop = config.bol_strategy.trailing_stop
        self.take_profit = config.bol_strategy.take_profit / 100 + 1
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

            if event.type == EventType.MARKET:
                for symbol in self.symbol_list:

                    if not data_handler.has_current_price(symbol, current_date):
                        continue

                    bars = data_handler.get_current_data(symbol, current_date - datetime.timedelta(self.window * 2),
                                                         current_date)

                    if bars is None:
                        continue

                    if data_handler.get_current_tick(symbol, current_date, 'close') <= 0:
                        continue

                    if len(bars[price_type].values) < self.window:
                        continue

                    if not bars.empty:

                        price = data_handler.get_current_tick(symbol, current_date, 'close')

                        up_threshold, down_threshold, mean = bollinger_bands(bars[price_type], self.window, self.n)
                        dt = current_date
                        strength = 1.0
                        signal_detected = False

                        if price > up_threshold and self.bought[symbol] == PositionStatus.OUT \
                                and not self.allowed_signals == AllowedSignals('LONG'):
                            self.signal_number += 1
                            signal_detected = True
                            action = OrderType.SHORT
                            strategy_id = self.strategy_id + '{:04d}'.format(self.signal_number)

                        if price < down_threshold and self.bought[symbol] == PositionStatus.OUT \
                                and not self.allowed_signals == AllowedSignals.SHORT:
                            self.signal_number += 1
                            signal_detected = True
                            action = OrderType.LONG
                            strategy_id = self.strategy_id + '{:04d}'.format(self.signal_number)

                        elif price > mean and self.bought[symbol] == PositionStatus.LONG:
                            signal_detected = True
                            action = OrderType.EXIT
                            orders_data_tmp = orders_data[orders_data['Symbol'] == symbol]
                            orders_data_tmp = orders_data_tmp[orders_data_tmp['Direction'] == OrderDirection.BUY.value]
                            orders_data_tmp = orders_data_tmp[
                                orders_data_tmp['Order_ID'].str.contains(self.strategy_id)]
                            strategy_id = orders_data_tmp['Order_ID'].values[-1]

                        elif price < mean and self.bought[symbol] == PositionStatus.SHORT:
                            signal_detected = True
                            action = OrderType.EXIT
                            orders_data_tmp = orders_data[orders_data['Symbol'] == symbol]
                            orders_data_tmp = orders_data_tmp[orders_data_tmp['Direction'] == OrderDirection.SELL.value]
                            orders_data_tmp = orders_data_tmp[
                                orders_data_tmp['Order_ID'].str.contains(self.strategy_id)]
                            strategy_id = orders_data_tmp['Order_ID'].values[-1]

                        if signal_detected:
                            signal = SignalEvent(strategy_id, SignalType.MKT, symbol, dt, action, strength)
                            self.events.put(signal)
                            logger.debug('Signal detected! ' + current_date.strftime('%Y/%m/%d %H:%M:%S'))
                            logger.debug(action.value + ' ' + symbol + ' : ' + str(bars[price_type].values[-1]))
                            logger.debug('ID: ' + strategy_id)
