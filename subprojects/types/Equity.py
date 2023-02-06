

class EquityOutput():
    def __init__(self):
        self.datetime = 0
        self.mac = 0
        self.bol = 0
        self.invested = 0
        self.cash = 0
        self.commission = 0
        self.curr_comm = 0
        self.total = 0
        self.returns = 0
        self.equity_curve = 0
        self.drawdown = 0

    def set_data(self, datetime, invested, cash, commission, total, curr_comm, returns, equity_curve, drawdown):
        self.datetime = datetime
        self.invested = invested
        self.cash = cash
        self.commission = commission
        self.curr_comm = curr_comm
        self.total = total
        self.returns = returns
        self.equity_curve = equity_curve
        self.drawdown = drawdown

    def print_header(self):
        header = "      Date  Time    Invested       Cash  Commission  Curr_Comm       Total    Returns     Equity  Drawndown \n" \
                 "---------- -----    --------  ---------  ----------  ---------   ---------  ---------  ---------  --------- \n"
        return header

    def print_data(self):
        data = "%s  %10.3f %10.3f  %10.3f %10.3f  %10.3f %10.6f %10.6f %10.6f\n" \
        % (self.datetime.strftime("%d-%m-%Y %H:%M"), self.invested, self.cash, self.commission, self.curr_comm, self.total,
           self.returns, self.equity_curve, self.drawdown)
        return data

