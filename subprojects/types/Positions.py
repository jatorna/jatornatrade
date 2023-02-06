from subprojects.misc.LowLevelFuncions import datetime64_to_datetime
from subprojects.types.Common import *


class Position:
    def __init__(self):
        self.id = ''
        self.shares_qty = 0
        self.open_price = 0
        self.stop_loss = None
        self.take_profit = None
        self.limit_status = False

    def close_position(self):
        self.id = ''
        self.shares_qty = 0
        self.open_price = 0
        self.stop_loss = None
        self.take_profit = None
        self.limit_status = False


class PositionsOutputData:
    def __init__(self):
        self.close_data = []
        self.current_data = []

    def set_close_data(self, orders_data):
        order_id = orders_data['Order_ID'].values[-1]
        position_df = orders_data[orders_data['Order_ID'] == order_id]
        position = PositionOutput()
        position.set_data(position_df)
        self.close_data.append(position)

    def set_current_data(self, current_date, data_handler, portfolio):

        if len(portfolio.orders_data) == 0:
            return

        positions_closed = list(portfolio.orders_data[portfolio.orders_data['Action'] == OrderType.EXIT.value]
                                ['Order_ID'].values)

        if len(positions_closed) > 0:
            current_orders_data = portfolio.orders_data[~portfolio.orders_data['Order_ID'].isin(positions_closed)]
        else:
            current_orders_data = portfolio.orders_data

        for row in range(len(current_orders_data)):
            order_id = current_orders_data['Order_ID'].values[row]
            symbol = current_orders_data['Symbol'].values[row]
            mkt_quantity = current_orders_data['Quantity'].values[row]
            cur_price = data_handler.get_last_price(symbol, current_date)
            cur_commission = portfolio.calculate_commission(abs(mkt_quantity), cur_price)
            position_df = current_orders_data[current_orders_data['Order_ID'] == order_id]
            position = PositionOutput()

            position.set_current_data(position_df, current_date, cur_price, cur_commission)
            self.current_data.append(position)

    def clear(self):
        self.close_data.clear()
        self.current_data.clear()


class PositionOutput:
    def __init__(self):
        self.id = ''
        self.symbol = ''
        self.action = ''
        self.open_dt = ''
        self.open_price = 0
        self.open_comm = 0
        self.shares_qty = 0
        self.cost = 0
        self.close_dt = ''
        self.close_price = 0
        self.close_comm = 0
        self.paying = 0
        self.total_commission = 0
        self.profit = 0
        self.profit_per = 0

    def set_data(self, position_df):
        self.id = position_df['Order_ID'].values[0]
        self.symbol = position_df['Symbol'].values[0]
        self.action = position_df['Action'].values[0]
        self.shares_qty = position_df['Quantity'].values[0]
        self.open_dt = datetime64_to_datetime(position_df['Date'].values[0])
        self.open_price = position_df['Price'].values[0]
        self.open_comm = position_df['Commission'].values[0]
        self.cost = self.shares_qty * self.open_price + self.open_comm
        self.close_dt = datetime64_to_datetime(position_df['Date'].values[1])
        self.close_price = position_df['Price'].values[1]
        self.close_comm = position_df['Commission'].values[1]
        if self.action == OrderType.LONG.value:
            self.paying = self.shares_qty * self.close_price - self.close_comm
        elif self.action == OrderType.SHORT.value:
            self.paying = - self.shares_qty * (self.close_price - 2 * self.open_price) - self.close_comm
        self.total_commission = self.open_comm + self.close_comm
        self.profit = self.paying - self.cost
        self.profit_per = self.profit / self.cost * 100

    def set_current_data(self, position_df, current_date, curr_price, curr_comm):
        self.id = position_df['Order_ID'].values[0]
        self.symbol = position_df['Symbol'].values[0]
        self.action = position_df['Action'].values[0]
        self.shares_qty = position_df['Quantity'].values[0]
        self.open_dt = datetime64_to_datetime(position_df['Date'].values[0])
        self.open_price = position_df['Price'].values[0]
        self.open_comm = position_df['Commission'].values[0]
        self.cost = self.shares_qty * self.open_price + self.open_comm
        self.close_dt = current_date
        self.close_price = curr_price
        self.close_comm = curr_comm
        if self.action == OrderType.LONG.value:
            self.paying = self.shares_qty * self.close_price - self.close_comm
        elif self.action == OrderType.SHORT.value:
            self.paying = - self.shares_qty * (self.close_price - 2 * self.open_price) - self.close_comm
        self.total_commission = self.open_comm + self.close_comm
        self.profit = self.paying - self.cost
        self.profit_per = self.profit / self.cost * 100

    def print_header(self):
        header = " Symbol        ID  Action       ODate OTime  Quantity      OPrice  OCommission       Cost       CDate CTime      CPrice  CCommission     Paying       Profit    Profit_%\n" \
                 "-------   -------  ------  ---------- -----  --------  ----------  -----------  ---------  ---------- -----  ----------  -----------  ---------  -----------  ----------\n"
        return header

    def print_data(self):
        data = "%7s %9s %7s  %s %9.2f %11.4f %12.3f %10.4f  %s %11.4f %12.3f %10.4f %12.4f %11.3f\n" \
        % (self.symbol, self.id, self.action, self.open_dt.strftime("%d-%m-%Y %H:%M"), self.shares_qty,
           self.open_price, self.open_comm, self.cost, self.close_dt.strftime("%d-%m-%Y %H:%M"), self.close_price,
           self.close_comm, self.paying, self.profit, self.profit_per)
        return data
