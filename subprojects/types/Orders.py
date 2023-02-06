from subprojects.misc.LowLevelFuncions import datetime64_to_datetime


class OrdersOutputData:
    def __init__(self):
        self.data = []

    def set_data(self, orders_data):
        order = OrderOutput()
        date = datetime64_to_datetime(orders_data['Date'].values[-1])
        order_id = orders_data['Order_ID'].values[-1]
        symbol = orders_data['Symbol'].values[-1]
        action = orders_data['Action'].values[-1]
        order_type = orders_data['Type'].values[-1]
        price = orders_data['Price'].values[-1]
        strength = orders_data['Strength'].values[-1]
        quantity = orders_data['Quantity'].values[-1]
        commission = orders_data['Commission'].values[-1]
        order_date = datetime64_to_datetime(orders_data['Order_Date'].values[-1])
        price_date = orders_data['Order_Price'].values[-1]
        order.set_data(date, order_id, symbol, action, order_type, price, strength, quantity, commission, order_date,
                       price_date)
        self.data.append(order)

    def clear(self):
        self.data.clear()


class OrderOutput:
    def __init__(self):
        self.date = 0
        self.order_id = 0
        self.symbol = 0
        self.action = 0
        self.order_type = 0
        self.price = 0
        self.strength = 0
        self.quantity = 0
        self.commission = 0
        self.order_date = 0
        self.order_price = 0

    def set_data(self, date, symbol, order_id, action, order_type, price, strength, quantity, commission, order_date,
                 order_price):
        self.date = date
        self.order_id = order_id
        self.symbol = symbol
        self.action = action
        self.order_type = order_type
        self.price = price
        self.strength = strength
        self.quantity = quantity
        self.commission = commission
        self.order_date = order_date
        self.order_price = order_price

    def print_header(self):
        header = "      Date  Time    Symbol  Order_ID     Action  Type      Price  Strength  Quantity  Commission       ODate OTime      OPrice\n" \
                 "---------- -----   -------  --------  ---------  ----  ---------  --------  --------  ----------  ---------- -----   ---------\n"
        return header

    def print_data(self):
        data = "%s %9s %9s %10s %5s %10.4f %9.2f %9.3f %11.3f  %s  %10.4f\n" \
        % (self.date.strftime("%d-%m-%Y %H:%M"), self.order_id, self.symbol, self.action, self.order_type,
           self.price, self.strength, self.quantity, self.commission, self.order_date.strftime("%d-%m-%Y %H:%M"), self.order_price)
        return data

