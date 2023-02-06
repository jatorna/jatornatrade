from trading_engine.Event import SignalEvent
from trading_engine.strategies.Strategy import Strategy
from trading_engine.Event import EventType
import subprojects.misc.LowLevelFuncions as llw
from subprojects.types.Common import *

logger = llw.script_logger('BAH STRATEGY')


class BuyAndHoldStrategy(Strategy):
    """
    Buy and Hold Strategy
    """

    def __init__(self, symbol_list, events, config, strategy_id):
        self.status = False
        self.symbol_list = symbol_list
        self.events = events
        self.limit_orders = False
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

            if event.type == EventType.MARKET:
                for symbol in self.symbol_list:

                    if not data_handler.has_current_price(symbol, current_date):
                        continue

                    price = data_handler.get_current_tick(symbol, current_date, 'close')
                    if data_handler.get_current_tick(symbol, current_date, 'close') <= 0:
                        continue

                    dt = current_date
                    strength = 1.0
                    signal_detected = False

                    if self.bought[symbol] == PositionStatus.OUT:
                        self.signal_number += 1
                        signal_detected = True
                        action = OrderType.LONG
                        strategy_id = self.strategy_id + '{:04d}'.format(self.signal_number)

                    if signal_detected:
                        signal = SignalEvent(strategy_id, SignalType.MKT, symbol, dt, action, strength)
                        self.events.put(signal)
                        logger.debug('Signal detected! ' + current_date.strftime('%Y/%m/%d %H:%M:%S'))
                        logger.debug(action.value + ' ' + symbol + ' : ' + str(price))
                        logger.debug('ID: ' + strategy_id)
