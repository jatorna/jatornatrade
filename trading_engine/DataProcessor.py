from subprojects.types import Equity, Orders, Positions, ScreenerData
from subprojects.misc.LowLevelFuncions import datetime64_to_datetime
import subprojects.misc.LowLevelFuncions as llw
import pandas as pd
import numpy as np

logger = llw.script_logger('DATA PROCESSOR')

# Global variables
total_list_ = []
equity_list_ = []


class DataProcessor:
    def __init__(self):
        self.data_output = DataOutput

    def write_sequential_equity_output(self, holdings, initial_capital):
        global total_list_
        global equity_list_

        all_holdings = []
        for index in holdings[-2:]:
            all_holdings.append(index.copy())

        all_curve = pd.DataFrame(holdings)
        curve = pd.DataFrame(all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()

        curve['equity_curve'] = curve['total'].values[-1]/initial_capital
        date = datetime64_to_datetime(curve.index[-1])
        invested = curve['invested'].values[-1]
        cash = curve['cash'].values[-1]
        commission = curve['commission'].values[-1]
        total = curve['total'].values[-1]
        curr_comm = curve['curr_comm'][-1]
        max_total = np.max(all_curve['total'].values)
        returns = curve['returns'].values[-1]
        equity_curve = curve['equity_curve'].values[-1]
        drawdown = (max_total / initial_capital - curve['equity_curve'].values[-1])
        # drawdown = (max_total-curve.total[-1]) / max_total   choose best option for drawdown
        if drawdown < 0:
            drawdown = 0
        self.data_output.equity_output.set_data(date, invested, cash, commission, total, curr_comm, returns,
                                                equity_curve, drawdown)

    def write_sequential_order_output(self, orders_data):
        self.data_output.orders_output.set_data(orders_data)

    def write_sequential_close_positions_output(self, orders_data):
        self.data_output.positions_output.set_close_data(orders_data)

    def write_sequential_current_positions_output(self, current_date, data_handler, portfolio):
        self.data_output.positions_output.set_current_data(current_date, data_handler, portfolio)

    def write_screener_data(self, current_date, screener_data):
        try:
            symbols = screener_data[current_date]
            self.data_output.screener_symbols_output.set_data(current_date, symbols)
        except:
            logger.error('No screener data for ' + current_date.strftime("%m/%d/%Y"))

    def clear_sequential_output(self):
        self.data_output.orders_output.clear()
        self.data_output.positions_output.clear()
        self.data_output.screener_symbols_output.clear()


class DataOutput:
    equity_output = Equity.EquityOutput()
    orders_output = Orders.OrdersOutputData()
    positions_output = Positions.PositionsOutputData()
    screener_symbols_output = ScreenerData.ScreenerOutputData()
