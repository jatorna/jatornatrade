import pickle
import subprojects.misc.LowLevelFuncions as llw
from subprojects.types.Positions import Position
from subprojects.types.Common import *
import sys
import copy
import queue
from trading_engine.Event import SignalEvent

logger = llw.script_logger('SESSION MGR')


class SessionManager:

    def __init__(self, config, session_id, output_path, data_handler, portfolio, strategies,
                 screener_deactivated_symbols, pending_orders,
                 start_date):

        self.output_path = output_path
        self.portfolio = portfolio
        self.data_handler = data_handler
        self.strategies = strategies
        self.start_date = start_date
        self.pending_orders = pending_orders
        self.config = config
        self.session_id = session_id
        self.config_deactivate_symbols = queue.Queue()
        self.screener_deactivated_symbols = screener_deactivated_symbols

        if config.general.continue_session:
            config.general.continue_session = self.load_session_data()

    def save_session_data(self):

        session_data = [self.data_handler.symbol_list, self.portfolio.all_holdings, self.portfolio.all_positions,
                        self.portfolio.current_holdings, self.portfolio.current_positions,
                        self.portfolio.initial_capital, self.portfolio.orders_data, self.portfolio.close_positions_data,
                        self.portfolio.current_positions_data]

        with open(self.output_path + '/' + self.session_id + '.dat', "wb") as f:

            pending_orders = self.pending_orders.queue
            pending_orders_list = []
            for order in pending_orders:
                pending_orders_list.append(order)

            pickle.dump(pending_orders_list, f)

            screener_deactivated_symbols = self.screener_deactivated_symbols.queue
            screener_deactivated_list = []
            for symbol in screener_deactivated_symbols:
                screener_deactivated_list.append(symbol)

            pickle.dump(screener_deactivated_list, f)

            pickle.dump(session_data, f)
            for strategy in self.strategies:
                if strategy.strategy_id == 'car':
                    strategy_data = [strategy.strategy_id, strategy.bought, strategy.signal_number, strategy.periods_in_market,
                                 strategy.periods_in_watchlist, strategy.periods_in_consolidation]
                else:
                    strategy_data = [strategy.strategy_id, strategy.bought, strategy.signal_number]
                pickle.dump(strategy_data, f)

    def load_session_data(self):
        logger.info('Loading session data')
        try:
            with open(self.output_path + '/' + self.session_id + '.dat', "rb") as f:
                pending_orders_list = pickle.load(f)
                for pending_order in pending_orders_list:
                    self.pending_orders.put(pending_order)

                screener_deactivated_symbols = pickle.load(f)
                for symbol in screener_deactivated_symbols:
                    self.screener_deactivated_symbols.put(symbol)

                session_data = pickle.load(f)
                strategy_data = []
                for s in self.strategies:
                    strategy_data.append(pickle.load(f))

            if self.start_date <= session_data[1][-1]['datetime']:
                logger.error('No valid epoch to load ' + self.session_id + '.dat. Program aborted')
                logger.info('Last epoch ' + session_data[1][-1]['datetime'].strftime(format='%d/%m/%Y %H:%M'))
                sys.exit()

            for s in strategy_data:
                for strategy in self.strategies:
                    if s[0] == strategy.strategy_id:
                        strategy.bought = s[1]
                        strategy.signal_number = s[2]

                        if strategy.strategy_id == 'car':
                            strategy.periods_in_market = s[3]
                            strategy.periods_in_watchlist = s[4]
                            strategy.periods_in_consolidation = s[5]

            old_symbol_list = set(session_data[0])
            self.portfolio.all_holdings = session_data[1]
            self.portfolio.all_positions = session_data[2]
            self.portfolio.current_holdings = session_data[3]
            self.portfolio.current_positions = session_data[4]
            self.portfolio.initial_capital = session_data[5]
            self.portfolio.orders_data = session_data[6]
            self.portfolio.close_positions_data = session_data[7]
            self.portfolio.current_positions_data = session_data[8]

            if self.data_handler.type == DataHandlerType.FIXED:
                self.update_fixed_config_symbol_list(old_symbol_list, pending_orders_list)

            elif self.data_handler.type == DataHandlerType.SCREENER:
                for symbol in old_symbol_list:
                    self.data_handler.symbol_list.add(symbol)

            logger.log(5, 'Session data loaded succesfully')

            return True
        except Exception as e:
            logger.error(e)
            logger.error('Error loading session data. Session will be started at ' +
                         self.start_date.strftime(format='%d/%m/%Y %H:%M'))
            return False

    def calculate_exit_signals(self, events, current_date):
        while True:
            try:
                symbol = self.config_deactivate_symbols.get(False)
            except queue.Empty:
                break
            else:
                if symbol is not None:
                    for strategy in self.strategies:
                        if strategy.bought[symbol] != PositionStatus.OUT:
                            orders_data_tmp = self.portfolio.orders_data[self.portfolio.orders_data['Symbol'] == symbol]
                            orders_data_tmp = orders_data_tmp[
                                orders_data_tmp['Order_ID'].str.contains(strategy.strategy_id)]
                            strategy_id = orders_data_tmp['Order_ID'].values[-1]
                            signal = SignalEvent(strategy_id, SignalType.USR, symbol, current_date,
                                                 OrderType.EXIT, 1)
                            events.put(signal)
                            logger.debug('Exit signal because symbol is deactivated ' +
                                         current_date.strftime('%Y/%m/%d %H:%M:%S'))
                            logger.debug('EXIT' + ' ' + symbol)
                            logger.debug('ID: ' + strategy_id)

    def update_fixed_config_symbol_list(self, old_symbol_list, pending_orders_list):

        # TODO: Check this method. Probable bug because add symbol always to data handler symbol list.

        new_symbols = set()
        config_deactivate_symbols = set()
        for symbol in old_symbol_list:
            if symbol not in self.config.symbol_list:
                config_deactivate_symbols.add(symbol)

        for symbol in self.config.symbol_list:
            if symbol not in old_symbol_list:
                new_symbols.add(symbol)

        for symbol in config_deactivate_symbols:
            self.data_handler.symbol_list.add(symbol)

        for order in pending_orders_list:
            if order.symbol not in self.data_handler.symbol_list:
                self.data_handler.symbol_list.add(order.symbol)

        position = Position()
        for symbol in new_symbols:
            for strategy in self.strategies:
                self.portfolio.current_positions[strategy.strategy_id][symbol] = copy.copy(position)
                strategy.bought[symbol] = PositionStatus.OUT

        # TODO: Update portfolio
        if len(config_deactivate_symbols) > 0:
            for symbol in config_deactivate_symbols:
                self.config_deactivate_symbols.put(symbol)
            logger.info(
                'Symbols ' + str(config_deactivate_symbols) + ' has been deactivated. All positions will be closed.')

        if len(new_symbols) > 0:
            logger.info('Symbols ' + str(new_symbols) + ' has been activated.')
