import pandas as pd
import subprojects.misc.LowLevelFuncions as llw
from subprojects.types.Common import *
from trading_engine.Event import EventType
import copy
import datetime as dt
from subprojects.types import Positions

logger = llw.script_logger('PORTFOLIO')


class Portfolio(object):

    def __init__(self, config, events, symbol_list, strategies_list, start_date, data_handler, risk_manager,
                 initial_capital, mode):

        self.events = events
        self.symbol_list = symbol_list
        self.strategies_list = copy.copy(strategies_list)
        self.start_date = start_date
        self.data_handler = data_handler
        self.risk_manager = risk_manager
        self.initial_capital = initial_capital
        self.mode = mode
        self.config = config

        self.all_positions = self.init_all_positions()
        self.current_positions = self.init_current_positions()
        self.all_holdings = self.init_all_holdings()
        self.current_holdings = self.init_current_holdings()
        self.orders_data = pd.DataFrame(columns=['Date', 'Order_ID', 'Symbol', 'Action', 'Direction', 'Type', 'Price',
                                                 'Strength', 'Quantity', 'Commission', 'Order_Date', 'Order_Price'])
        self.close_positions_data = []
        self.current_positions_data = []

    def init_all_positions(self):

        position = Positions.Position()
        d_temp = dict((k, v) for k, v in [(s, copy.copy(position)) for s in self.symbol_list])
        d = dict((k, v) for k, v in [(s, d_temp.copy()) for s in self.strategies_list])
        d['datetime'] = self.start_date
        return [d]

    def init_all_holdings(self):

        d_temp = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        d = dict((k, v) for k, v in [(s, [d_temp.copy(), 0]) for s in self.strategies_list])
        if self.mode == EngineMode.BACKTEST:
            d['datetime'] = self.start_date
        if self.mode == EngineMode.REALTIME:
            d['datetime'] = dt.datetime(dt.datetime.now().year, dt.datetime.now().month, dt.datetime.now().day,
                                        dt.datetime.now().hour, dt.datetime.now().minute)
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        d['curr_comm'] = 0.0
        d['invested'] = 0.0

        return [d]

    def init_current_holdings(self):

        d_temp = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        d = dict((k, v) for k, v in [(s, [d_temp.copy(), 0]) for s in self.strategies_list])
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        d['curr_comm'] = 0.0
        d['invested'] = 0.0
        return d

    def init_current_positions(self):

        position = Positions.Position()
        d = dict((k, v) for k, v in [(s, dict((k, v) for k, v in [(s, copy.copy(position)) for s
                                in self.symbol_list])) for s in self.strategies_list])
        return d

    def update_portfolio(self, current_date):

        latest_datetime = current_date

        # Update positions
        # ================
        position = Positions.Position()
        dp_tmp = dict((k, v) for k, v in [(s, copy.copy(position)) for s in self.symbol_list])
        dp = dict((k, v) for k, v in [(s, dp_tmp.copy()) for s in self.strategies_list])
        dp['datetime'] = latest_datetime

        for strategy in self.strategies_list:
            for s in self.symbol_list:

                # TODO: REVIEW THIS IN ORDER TO IMPROVE THE PROGRAM

                if s not in self.current_positions[strategy]:
                    position = Positions.Position()
                    self.current_positions[strategy][s] = position

                dp[strategy][s] = copy.copy(self.current_positions[strategy][s])

        # Append the current positions
        self.all_positions.append(dp)

        # Update holdings
        # ===============
        dh_tmp = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        dh = dict((k, v) for k, v in [(s, [dh_tmp.copy(), 0]) for s in self.strategies_list])
        dh['datetime'] = latest_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['total']

        current_commissions = 0
        current_invested = 0

        dh['curr_comm'] = current_commissions
        dh['invested'] = current_invested

        for strategy in self.strategies_list:
            for s in self.symbol_list:
                mkt_quantity = self.current_positions[strategy][s].shares_qty
                open_price = self.current_positions[strategy][s].open_price
                last_price = self.data_handler.get_last_price(s, current_date)

                if mkt_quantity == 0:
                    market_value = 0
                elif mkt_quantity > 0 and last_price is not None:
                    market_value = mkt_quantity * last_price
                elif mkt_quantity < 0 and last_price is not None:
                    market_value = mkt_quantity * (last_price - 2 * open_price)

                if mkt_quantity == 0:
                    commission = 0
                else:
                    commission = self.calculate_commission(abs(mkt_quantity), last_price)

                current_commissions += commission

                dh[strategy][0][s] = market_value
                dh[strategy][1] += market_value
                dh['total'] += market_value - commission
                dh['curr_comm'] = current_commissions

            current_invested += dh[strategy][1]

        dh['invested'] = current_invested

        # Append the current holdings
        self.all_holdings.append(dh)

    def update_positions_from_fill(self, fill):

        # Check whether the fill is a buy or sell
        stop_loss = 0
        take_profit = 0
        fill_dir = 1 if fill.direction == OrderDirection.BUY else -1

        if fill.action != OrderType.EXIT:
            stop_loss, take_profit = self.risk_manager.set_price_limits(fill)

        # Update positions list with new quantities
        self.current_positions[fill.order_id[0:3]][fill.symbol].shares_qty += fill_dir * fill.quantity
        if self.current_positions[fill.order_id[0:3]][fill.symbol].shares_qty != 0:
            self.current_positions[fill.order_id[0:3]][fill.symbol].open_price = fill.price
            self.current_positions[fill.order_id[0:3]][fill.symbol].stop_loss = stop_loss
            self.current_positions[fill.order_id[0:3]][fill.symbol].take_profit = take_profit
            self.current_positions[fill.order_id[0:3]][fill.symbol].id = fill.order_id

        else:
            self.current_positions[fill.order_id[0:3]][fill.symbol].close_position()

    def update_holdings_from_fill(self, fill):

        fill_dir = -1 if fill.action == OrderType.EXIT else 1

        if fill.action == OrderType.EXIT and fill.direction == OrderDirection.BUY:
            cost = (self.all_positions[-1][fill.order_id[0:3]][fill.symbol].shares_qty *
                    self.all_positions[-1][fill.order_id[0:3]][fill.symbol].open_price) + \
                   (self.all_positions[-1][fill.order_id[0:3]][fill.symbol].open_price -
                    fill.price) * self.all_positions[-1][fill.order_id[0:3]][fill.symbol].shares_qty
        else:
            cost = fill_dir * fill.price * fill.quantity

        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)

    def update_fill(self, event):

        if event.type == EventType.FILL:
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def update_orders_data(self, fill, current_date):

        self.orders_data.loc[len(self.orders_data)] = [current_date, fill.order_id, fill.symbol, fill.action.value,
                                                       fill.direction.value, fill.fill_type.value, fill.price,
                                                       fill.strength, fill.quantity, fill.commission,
                                                       fill.order_timeindex, fill.order_price]

    def confirm_fill_order(self, current_date, strategies, fill):

        fill.filled = self.data_handler.has_current_price(fill.symbol, current_date)

        if fill.filled:
            fill.price = self.data_handler.get_current_tick(fill.symbol, current_date, 'open')

            for strategy in strategies:
                if strategy.strategy_id == fill.order_id[0:3]:
                    if fill.action == OrderType.EXIT:
                        strategy.bought[fill.symbol] = PositionStatus.OUT
                    else:
                        strategy.bought[fill.symbol] = PositionStatus(fill.action.value)

        else:
            logger.warning(
                fill.order_id + ' without market data. Order pending ' + current_date.strftime('%Y/%m/%d %H:%M:%S'))

        self.events.put(fill)

    def calculate_commission(self, market_qty, price):
        # Calculate commission
        commission = 0
        if not market_qty:
            return commission

        if self.config.portfolio.commiss_model == ComissModel.NONE:
            commission = 0
            return commission

        elif self.config.portfolio.commiss_model == ComissModel.COMBINED:
            commission = self.config.portfolio.min_commission + self.config.portfolio.commission * market_qty * price
            if self.config.portfolio.max_commission > 0:
                commission = min(self.config.portfolio.max_commission, commission)
            return commission

        elif self.config.portfolio.commiss_model == ComissModel.FIXED:
            commission = self.config.portfolio.min_commission
            return commission

        elif self.config.portfolio.commiss_model == ComissModel.VARIABLE:
            commission = self.config.portfolio.commission * market_qty * price
            if self.config.portfolio.min_commission > 0:
                commission = max(self.config.portfolio.min_commission, commission)
            if self.config.portfolio.max_commission > 0:
                commission = min(self.config.portfolio.max_commission, commission)
            return commission

        elif self.config.portfolio.commiss_model == ComissModel.DEGIRO:
            commission = 0.5 * 1.18 + market_qty * 0.004
            return commission
