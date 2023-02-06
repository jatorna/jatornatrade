import investpy
import numpy as np
from trading_engine.Event import OrderEvent
from trading_engine.Event import SignalEvent
from trading_engine.Event import EventType
from subprojects.types.Common import *
from subprojects.misc import LowLevelFuncions as llw

logger = llw.script_logger('RISK MANAGER')


class RiskManager:

    def __init__(self, events, symbol_list, strategies_list, config, data_handler):
        self.events = events
        self.symbol_list = symbol_list
        self.strategies_list = strategies_list
        self.config = config
        self.data_handler = data_handler

    def generate_order(self, signal, current_date, portfolio):
        """

        Parameters:
        signal - The tuple containing Signal information.
        """
        order = None

        symbol = signal.symbol
        order_id = signal.strategy_id
        action = signal.action

        if signal.signal_type == SignalType.USR:
            price = self.data_handler.get_last_price(symbol, current_date)
        else:
            price = self.data_handler.get_current_tick(symbol, current_date, 'close')

        if action != OrderType.EXIT:

            strenght = 1.0

            if self.config.risk_manager.index_check:
                strenght = self.check_index(symbol, current_date)

            investment_quantity = self.config.risk_manager.order_invest * strenght

            if not investment_quantity:
                logger.info('Index so bad. Signal ' + order_id + ' discarted')
                return

            shares_quantity = 1 if round(investment_quantity / price) == 0 else round(investment_quantity / price)

            if shares_quantity * price > investment_quantity * 1.15:
                logger.info('Investment quantity too much high. Signal ' + order_id + ' discarted')
                return

            if shares_quantity * price < investment_quantity * 0.85:
                logger.info('Investment quantity too much slow. Signal ' + order_id + ' discarted')
                return

        cur_quantity = portfolio.current_positions[order_id[0:3]][symbol].shares_qty
        order_type = signal.signal_type

        if action == OrderType.LONG and cur_quantity == 0:
            order = OrderEvent(symbol, order_id, order_type, shares_quantity, price, action, OrderDirection.BUY,
                               strenght)
        if action == OrderType.SHORT and cur_quantity == 0:
            order = OrderEvent(symbol, order_id, order_type, shares_quantity, price, action, OrderDirection.SELL,
                               strenght)
        if action == OrderType.EXIT and cur_quantity > 0:
            order = OrderEvent(symbol, order_id, order_type, abs(cur_quantity), price, action, OrderDirection.SELL,
                               1)
        if action == OrderType.EXIT and cur_quantity < 0:
            order = OrderEvent(symbol, order_id, order_type, abs(cur_quantity), price, action, OrderDirection.BUY,
                               1)
        return order

    def update_signal(self, event, current_date, portfolio):
        """
        Acts on a SignalEvent to generate new orders.
        """
        if event.type == EventType.SIGNAL:
            order_event = self.generate_order(event, current_date, portfolio)
            self.events.put(order_event)

    def set_price_limits(self, fill):

        if not self.config.risk_manager.limit_orders:
            return None, None

        stop_loss_price = None
        take_profit_price = None

        for strategy in self.strategies_list:
            if fill.order_id[0:3] == strategy.strategy_id and strategy.limit_orders:
                stop_loss = strategy.stop_loss
                take_profit = strategy.take_profit
                break
            else:
                stop_loss = None
                take_profit = None
                pass

        if stop_loss is None or take_profit is None:
            return stop_loss_price, take_profit_price

        commission = self.config.risk_manager.comm_in_limits * fill.commission

        if fill.action == OrderType.LONG:
            stop_loss_price = - (((commission * 2 + fill.price *
                                   fill.quantity) * (stop_loss - 1)) / fill.quantity)
            take_profit_price = ((commission * 2 + fill.price *
                                  fill.quantity) * take_profit) / fill.quantity
            return stop_loss_price, take_profit_price

        if fill.action == OrderType.SHORT:
            stop_loss_price = (- commission + commission * stop_loss + fill.price * fill.quantity *
                               (1 + stop_loss)) / fill.quantity

            take_profit_price = - (commission + fill.price * fill.quantity * (-2 + take_profit) + commission *
                                   (1 - take_profit)) / fill.quantity

            return stop_loss_price, take_profit_price

    def update_price_limits(self, current_date, portfolio):

        for strategy in self.strategies_list:
            if not strategy.limit_orders or not strategy.trailing_stop:
                continue
            for symbol in self.symbol_list:
                price = self.data_handler.get_current_tick(symbol, current_date, price_type='close')
                if price is None or portfolio.current_positions[strategy.strategy_id][symbol].shares_qty == 0:
                    continue

                shares_qty = portfolio.current_positions[strategy.strategy_id][symbol].shares_qty
                open_price = portfolio.current_positions[strategy.strategy_id][symbol].open_price

                open_commission = portfolio.calculate_commission(abs(shares_qty), open_price) * \
                                  self.config.risk_manager.comm_in_limits
                current_commission = portfolio.calculate_commission(abs(shares_qty), price) * \
                                     self.config.risk_manager.comm_in_limits
                commission = open_commission + current_commission

                if shares_qty > 0:
                    stop_loss_price = - (((self.config.risk_manager.comm_in_limits *
                                           commission + price * shares_qty) *
                                          (strategy.stop_loss - 1)) / shares_qty)

                    if price > open_price:
                        portfolio.current_positions[strategy.strategy_id][symbol].stop_loss = stop_loss_price

                if shares_qty < 0:

                    stop_loss_price = (- current_commission + open_commission * strategy.stop_loss + price *
                                       shares_qty * (1 + strategy.stop_loss)) / shares_qty

                    if price < open_price:
                        portfolio.current_positions[strategy.strategy_id][symbol].stop_loss = stop_loss_price

    def calculate_limit_signals(self, current_date, current_positions):
        for symbol in self.symbol_list:
            current_price = self.data_handler.get_current_tick(symbol, current_date, 'close')
            if current_price is not None:
                for strategy in self.strategies_list:
                    if not strategy.limit_orders:
                        continue

                    signal_detected = False
                    if current_positions[strategy.strategy_id][symbol].shares_qty < 0:
                        if current_price >= current_positions[strategy.strategy_id][symbol].stop_loss:
                            signal_detected = True
                            signal_type = SignalType.STL
                            logger.info('S/L Limit Signal detected! ' + current_date.strftime('%Y/%m/%d %H:%M:%S'))

                        if current_price <= current_positions[strategy.strategy_id][symbol].take_profit:
                            signal_detected = True
                            signal_type = SignalType.TKP
                            logger.info('T/P Limit Signal detected! ' + current_date.strftime('%Y/%m/%d %H:%M:%S'))

                    if current_positions[strategy.strategy_id][symbol].shares_qty > 0:
                        if current_price <= current_positions[strategy.strategy_id][symbol].stop_loss:
                            signal_detected = True
                            signal_type = SignalType.STL
                            logger.info('S/L Limit Signal detected! ' + current_date.strftime('%Y/%m/%d %H:%M:%S'))

                        if current_price >= current_positions[strategy.strategy_id][symbol].take_profit:
                            signal_detected = True
                            signal_type = SignalType.TKP
                            logger.info('T/P Limit Signal detected! ' + current_date.strftime('%Y/%m/%d %H:%M:%S'))

                    if signal_detected:
                        logger.debug('EXIT ' + symbol + ' : ' + str(current_price))
                        logger.debug('ID: ' + current_positions[strategy.strategy_id][symbol].id)
                        signal = SignalEvent(current_positions[strategy.strategy_id][symbol].id, signal_type,
                                             symbol, current_date, OrderType.EXIT, 1)
                        self.events.put(signal)

    def check_index(self, symbol, current_date):

        try:
            exchange = Exchange(investpy.search_quotes(symbol, countries=['united states'],
                                                       products=['stocks'])[0].exchange)
        except:
            exchange = Exchange.NYSE

        if exchange == Exchange.NASDAQ:
            index = 'QQQ'
        else:
            index = 'SPY'

        index_price = self.data_handler.symbol_data[index].loc[:current_date]['close'].values[-1]
        sma50 = np.mean(self.data_handler.symbol_data[index].loc[:current_date]['close'].values[-50:])
        sma100 = np.mean(self.data_handler.symbol_data[index].loc[:current_date]['close'].values[-100:])
        sma200 = np.mean(self.data_handler.symbol_data[index].loc[:current_date]['close'].values[-200:])

        if index_price >= sma50:
            strenght = 1
        elif index_price >= sma100:
            strenght = 0.5
        elif index_price >= sma200:
            strenght = 0.25
        elif index_price < sma200:
            strenght = 0

        strenght = 0 if not (sma50 > sma100 > sma200) else strenght

        return strenght
