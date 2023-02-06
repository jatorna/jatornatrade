from trading_engine.Event import SignalEvent
from trading_engine.strategies.Strategy import Strategy
from trading_engine.Event import EventType
from subprojects.types.Common import *
import datetime
import subprojects.misc.LowLevelFuncions as llw
from subprojects.algorithm.TechnicalIndicators import *
import os

logger = llw.script_logger('CAR STRATEGY')


class CarvasBoxStrategy(Strategy):
    """
    CarvasBoxStrategy Strategy
    """

    def __init__(self, symbol_list, deactivated_symbols, events, config, alert_mgr, strategy_id):

        self.status = False
        self.symbol_list = symbol_list
        self.deactivated_symbols = deactivated_symbols
        self.events = events
        self.config = config
        self.limit_orders = config.car_strategy.limit_orders
        self.stop_loss = config.car_strategy.stop_loss / 100
        self.take_profit = config.car_strategy.take_profit / 100 + 1
        self.trailing_stop = config.car_strategy.trailing_stop
        self.enable_debug_file = config.car_strategy.enable_debug_file
        self.output_path = config.general.output_path
        self.alert_mgr = alert_mgr
        self.strategy_id = strategy_id
        self.signal_number = 0
        self.bought = {}
        self.periods_in_market = {}
        self.periods_whithout_data = {}
        self.periods_in_watchlist = {}
        self.periods_in_consolidation = {}

        self._update_bought()
        self._check_strategy_status(config.strategies)

    def _update_symbol(self, s):

        if s not in self.bought:
            self.bought[s] = PositionStatus.OUT
        if s not in self.periods_in_market:
            self.periods_in_market[s] = 0
        if s not in self.periods_in_watchlist:
            self.periods_in_watchlist[s] = 0
        if s not in self.periods_in_consolidation:
            # item 1 days in period, item 2 init price consolidate
            self.periods_in_consolidation[s] = [0, 0]
        if s not in self.periods_whithout_data:
            self.periods_whithout_data[s] = 0

    def _update_bought(self):

        for s in self.symbol_list:
            self._update_symbol(s)

    def _check_strategy_status(self, strategy_list):
        if self.strategy_id in strategy_list:
            self.status = True

    def _remove_no_data_symbol(self, symbol):
        if self.periods_whithout_data[symbol] > 2:
            self.deactivated_symbols.put(symbol)
            logger.debug(symbol + ' removed because 3 days without valid data')

    def calculate_signals(self, event, data_handler, current_date, orders_data, ppv):

        msg = ""

        if self.status:

            if event.type == EventType.MARKET:
                for symbol in sorted(self.symbol_list):

                    if symbol in self.deactivated_symbols.queue:
                        continue

                    self._update_symbol(symbol)

                    if not data_handler.has_current_price(symbol, current_date):
                        msg += "No data for symbol: " + symbol + "\n"
                        self.periods_whithout_data[symbol] += 1
                        self._remove_no_data_symbol(symbol)
                        continue

                    #TODO implement tick check

                    signal_detected = False
                    strength = 1.0

                    if self.bought[symbol] == PositionStatus.LONG:

                        self.periods_whithout_data[symbol] = 0

                        self.periods_in_market[symbol] += 1

                        if self.periods_in_market[symbol] >= 9:
                            signal_detected = True
                            action = OrderType.EXIT
                            orders_data_tmp = orders_data[orders_data['Symbol'] == symbol]
                            orders_data_tmp = orders_data_tmp[orders_data_tmp['Direction'] == OrderDirection.BUY.value]
                            orders_data_tmp = orders_data_tmp[
                                orders_data_tmp['Order_ID'].str.contains(self.strategy_id)]
                            signal_id = orders_data_tmp['Order_ID'].values[-1]

                    else:

                        bars = data_handler.get_current_data(symbol, current_date - datetime.timedelta(15),
                                                             current_date)

                        if len(bars) < 10:
                            msg += "No enough data for symbol: " + symbol + "\n"
                            self.periods_whithout_data[symbol] += 1
                            self._remove_no_data_symbol(symbol)
                            continue

                        avg_volume = np.mean(bars.volume.values[-10:])

                        volume = data_handler.get_current_tick(symbol, current_date, 'volume')
                        price = data_handler.get_current_tick(symbol, current_date, 'close')

                        volume_change = (volume / bars.volume.values[-2] - 1) * 100

                        if price <= 0:
                            msg += "Negative price for symbol: " + symbol + "\n"
                            self.periods_whithout_data[symbol] += 1
                            self._remove_no_data_symbol(symbol)
                            continue

                        self.periods_whithout_data[symbol] = 0

                        self.periods_in_watchlist[symbol] += 1

                        is_consolided = True if volume < avg_volume * 0.3 else False
                        if is_consolided:
                            if self.periods_in_consolidation[symbol][0] == 0:
                                self.periods_in_consolidation[symbol][1] = price

                            if price > self.periods_in_consolidation[symbol][1] * 1.09 or price < \
                                    self.periods_in_consolidation[symbol][1] * 0.91:
                                is_consolided = False

                        if not is_consolided:
                            self.periods_in_consolidation[symbol][1] = 0

                        self.periods_in_consolidation[symbol][0] = (self.periods_in_consolidation[symbol][0] + 1) if \
                            is_consolided else 0

                        if self.periods_in_consolidation[symbol][0] > 2 and volume_change > 20:

                            self.periods_in_watchlist[symbol] = 0
                            self.periods_in_consolidation[symbol][0] = 0
                            self.periods_in_consolidation[symbol][1] = 0

                            self.signal_number += 1
                            signal_detected = True
                            action = OrderType.LONG
                            signal_id = self.strategy_id + '{:04d}'.format(self.signal_number)

                        if self.periods_in_watchlist[symbol] > 4 and \
                                self.periods_in_consolidation[symbol][0] == 0 and not signal_detected:
                            # reset dictionaries because if symbol appears again in screener

                            self.periods_whithout_data[symbol] = 0
                            self.periods_in_market[symbol] = 0
                            self.periods_in_watchlist[symbol] = 0
                            self.periods_in_consolidation[symbol][0] = 0
                            self.periods_in_consolidation[symbol][1] = 0
                            self.deactivated_symbols.put(symbol)

                    if signal_detected:
                        #TODO if symbol has not data
                        if not data_handler.has_current_price(symbol, current_date):
                            self.periods_whithout_data[symbol] = 0
                            self._remove_no_data_symbol(symbol)
                            continue

                        price = data_handler.get_current_tick(symbol, current_date, 'close')
                        signal = SignalEvent(signal_id, SignalType.MKT, symbol, current_date, action, strength)
                        self.events.put(signal)
                        logger.debug('Signal detected! ' + current_date.strftime('%Y/%m/%d %H:%M:%S'))
                        logger.debug(action.value + ' ' + symbol + ' : ' + str(price))
                        logger.debug('ID: ' + signal_id)

                    self._print_debug_info(current_date, symbol)

                # Reset symbols status and build alert msg

                symbols_tracked = set()
                symbols_tracked.update(
                    list(self.periods_in_watchlist.keys()) + list(self.periods_in_consolidation.keys()) + list(
                        self.periods_in_market.keys()))

                msg_watchlist, msg_consolidation, msg_market = "", "", ""

                for symbol in symbols_tracked:
                    if symbol not in self.symbol_list:
                        self.periods_whithout_data[symbol] = 0
                        del self.periods_in_watchlist[symbol], self.periods_whithout_data[symbol], \
                            self.periods_in_consolidation[symbol], self.periods_in_market[symbol]

                    else:
                        if self.periods_in_watchlist[symbol] > 0:
                            msg_watchlist += symbol + " " + str(self.periods_in_watchlist[symbol]) + " "

                        if self.periods_in_consolidation[symbol][0] > 0:
                            msg_consolidation += symbol + " " + str(self.periods_in_consolidation[symbol][0]) + " "

                        if self.periods_in_market[symbol] > 0:
                            msg_market += symbol + " " + str(self.periods_in_market[symbol]) + " "

                msg += "\nSymbols watchlist:\n" + msg_watchlist + "\nSymbols consolidating:\n" + msg_consolidation + \
                       "\nSymbols in market:\n" + msg_market

                self.alert_mgr.send_telegram_alert(msg)

    def print_debug_header(self):

        if self.enable_debug_file and self.status:
            if self.config.general.continue_session:
                try:
                    os.stat(self.output_path + '/car_debug.txt')
                    return
                except:
                    pass

            header = "Date              Symbol   Watch  Conso  Markt\n" \
                     "----------------  -------  -----  -----  -----\n"

            f = open(self.output_path + '/car_debug.txt', 'w')
            f.write(header)
            f.close()
            logger.info('File ' + self.output_path + '/car_debug.txt opened')

    def _print_debug_info(self, current_date, symbol):

        if self.enable_debug_file:
            f = open(self.output_path + '/car_debug.txt', 'a')
            date_str = current_date.strftime("%d-%m-%Y %H:%M")

            if self.periods_in_watchlist[symbol] != 0 or self.periods_in_consolidation[symbol][0] != 0 or \
                    self.periods_in_market[symbol] != 0:
                data = "%s %8s %6d %6d %6d \n" \
                       % (date_str, symbol, self.periods_in_watchlist[symbol], self.periods_in_consolidation[symbol][0],
                          self.periods_in_market[symbol])

                f.write(data)
            f.close()
