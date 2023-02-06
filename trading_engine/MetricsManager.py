import subprojects.misc.LowLevelFuncions as llw
from subprojects.misc.LowLevelFuncions import datetime64_to_datetime
from subprojects.types.Orders import OrderOutput
import MySQLdb as mdb
from MySQLdb._exceptions import DatabaseError
import copy
import sys
import pytz

logger = llw.script_logger('METRICS MGR')


class MetricsManager:

    def __init__(self, session_id, mysql_config, continue_session, enabled, reset, portfolio):
        self.session_id = session_id
        self.mysql_config = copy.deepcopy(mysql_config)
        self.mysql_config.db_name = session_id + '_metrics'
        self.mysql_connection = ''
        self.continue_session = continue_session
        self.enabled = enabled
        self.portfolio = portfolio

        if self.enabled:
            self.create_trading_metrics_db()

        if self.enabled and reset and len(self.portfolio.all_holdings) > 1:
            logger.info('Reseting database metrics')
            self.reset_trading_metrics_db()

    def create_trading_metrics_db(self):

        try:
            self.mysql_connection = mdb.connect(host=self.mysql_config.db_host, user=self.mysql_config.db_user,
                                                passwd=self.mysql_config.db_pass, port=self.mysql_config.db_port,
                                                db=self.mysql_config.db_name)

            if not self.continue_session:
                logger.error('Database metrics already exist. Please, erase it and restart the program: ' +
                             self.mysql_config.db_name)
                logger.info('Aborting program')
                sys.exit()

            else:
                logger.info('Database metrics: ' + self.mysql_config.db_name)

        except DatabaseError:

            logger.info('Creating metrics database: ' + self.mysql_config.db_name)

            self.mysql_connection = mdb.connect(host=self.mysql_config.db_host, user=self.mysql_config.db_user,
                                                passwd=self.mysql_config.db_pass, port=self.mysql_config.db_port)

            cursor = self.mysql_connection.cursor()
            cursor.execute("CREATE DATABASE " + self.mysql_config.db_name)

            self.mysql_connection = mdb.connect(host=self.mysql_config.db_host, user=self.mysql_config.db_user,
                                                passwd=self.mysql_config.db_pass, port=self.mysql_config.db_port,
                                                db=self.mysql_config.db_name)

            cursor = self.mysql_connection.cursor()

            cursor.execute("CREATE TABLE equity (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, date DATETIME, "
                           "invested DECIMAL(19,4), cash DECIMAL(19,4), commission DECIMAL(19,4),"
                           "curr_commission DECIMAL(19,4), total DECIMAL(19,4))")

            cursor.execute("CREATE TABLE orders (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, date DATETIME, "
                           "symbol VARCHAR(45), order_id VARCHAR(45), action VARCHAR(45), type VARCHAR(45), "
                           "price DECIMAL(19,4), quantity DECIMAL(19,4), commission DECIMAL(19,4))")

            cursor.execute("CREATE TABLE open_positions (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                           "symbol VARCHAR(45), order_id VARCHAR(45), action VARCHAR(45), o_date DATETIME, "
                           "quantity DECIMAL(19,4), o_price DECIMAL(19,4), o_commission DECIMAL(19,4), "
                           "cost DECIMAL(19,4), c_date DATETIME, c_price DECIMAL(19,4), c_commission DECIMAL(19,4), "
                           "paying DECIMAL(19,4), profit DECIMAL(19,4), profit_per DECIMAL(19,4))")

            cursor.execute("CREATE TABLE close_positions (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                           "symbol VARCHAR(45), order_id VARCHAR(45), action VARCHAR(45), o_date DATETIME, "
                           "quantity DECIMAL(19,4), o_price DECIMAL(19,4), o_commission DECIMAL(19,4), "
                           "cost DECIMAL(19,4), c_date DATETIME, c_price DECIMAL(19,4), c_commission DECIMAL(19,4), "
                           "paying DECIMAL(19,4), profit DECIMAL(19,4), profit_per DECIMAL(19,4))")

    def reset_mysql_connection(self):
        if self.enabled:
            self.mysql_connection = mdb.connect(host=self.mysql_config.db_host, user=self.mysql_config.db_user,
                                                passwd=self.mysql_config.db_pass, port=self.mysql_config.db_port,
                                                db=self.mysql_config.db_name)

    def insert_equity_data_to_db(self, date, holding):

        if self.enabled:

            table = 'equity'
            column_str = "date, invested, cash, commission, curr_commission, total"
            data = []

            # tz = pytz.timezone('Europe/Madrid')
            # date = tz.localize(date)
            # date = date.astimezone(pytz.utc)

            row_data = (date, holding['invested'], holding['cash'], holding['commission'], holding['curr_comm'],
                        holding['total'])

            data.append(row_data)

            insert_str = ("%s, " * len(row_data))[:-2]
            final_str = ("INSERT INTO %s (%s) VALUES (%s)" % (table, column_str, insert_str))
            cursor = self.mysql_connection.cursor()
            cursor.executemany(final_str, data)
            self.mysql_connection.commit()

    def insert_order_data_to_db(self, order):

        if self.enabled:

            table = 'orders'
            column_str = "date, symbol, order_id, action, type, price, quantity, commission"
            data = []

            # tz = pytz.timezone('Europe/Madrid')
            # date = tz.localize(order.date)
            # date = date.astimezone(pytz.utc)

            row_data = (order.date, order.order_id, order.symbol, order.action, order.order_type,
                        order.price,order.quantity, order.commission)

            data.append(row_data)

            insert_str = ("%s, " * len(row_data))[:-2]
            final_str = ("INSERT INTO %s (%s) VALUES (%s)" % (table, column_str, insert_str))
            cursor = self.mysql_connection.cursor()
            cursor.executemany(final_str, data)
            self.mysql_connection.commit()

    def insert_position_data_to_db(self, position, table):

        if self.enabled:

            table = table

            column_str = "symbol, order_id, action, o_date, quantity, o_price, o_commission, cost, c_date, c_price, " \
                         "c_commission, paying, profit, profit_per"
            data = []

            # tz = pytz.timezone('Europe/Madrid')
            # date = tz.localize(order.date)
            # date = date.astimezone(pytz.utc)

            row_data = (position.symbol, position.id, position.action, position.open_dt, position.shares_qty,
                        position.open_price, position.open_comm, position.cost, position.close_dt, position.close_price,
                        position.close_comm, position.paying, position.profit, position.profit_per)

            data.append(row_data)

            insert_str = ("%s, " * len(row_data))[:-2]
            final_str = ("INSERT INTO %s (%s) VALUES (%s)" % (table, column_str, insert_str))
            cursor = self.mysql_connection.cursor()
            cursor.executemany(final_str, data)
            self.mysql_connection.commit()

    def reset_trading_metrics_db(self):

        cursor = self.mysql_connection.cursor()

        cursor.execute("TRUNCATE TABLE equity ")
        cursor.execute("TRUNCATE TABLE orders ")
        cursor.execute("TRUNCATE TABLE open_positions ")
        cursor.execute("TRUNCATE TABLE close_positions ")

        for i in range(len(self.portfolio.all_holdings)):
            if i == 0:
                continue

            date = self.portfolio.all_holdings[i]['datetime']
            self.insert_equity_data_to_db(date, self.portfolio.all_holdings[i])

        for i in range(len(self.portfolio.orders_data)):
            order = OrderOutput()
            date = datetime64_to_datetime(self.portfolio.orders_data['Date'].values[i])
            order_id = self.portfolio.orders_data['Order_ID'].values[i]
            symbol = self.portfolio.orders_data['Symbol'].values[i]
            action = self.portfolio.orders_data['Action'].values[i]
            order_type = self.portfolio.orders_data['Type'].values[i]
            price = self.portfolio.orders_data['Price'].values[i]
            strength = self.portfolio.orders_data['Strength'].values[i]
            quantity = self.portfolio.orders_data['Quantity'].values[i]
            commission = self.portfolio.orders_data['Commission'].values[i]
            order_date = datetime64_to_datetime(self.portfolio.orders_data['Order_Date'].values[i])
            price_date = self.portfolio.orders_data['Order_Price'].values[i]
            order.set_data(date, order_id, symbol, action, order_type, price, strength, quantity, commission,
                           order_date, price_date)

            self.insert_order_data_to_db(order)

        for position in self.portfolio.close_positions_data:
            self.insert_position_data_to_db(position, table='close_positions')

        for position in self.portfolio.current_positions_data:
            self.insert_position_data_to_db(position, table='open_positions')

        logger.log(5, 'Database metrics reset succesfully')

    def insert_data_to_db(self, current_date, data_output):

        self.insert_equity_data_to_db(current_date, self.portfolio.all_holdings[-1])
        for order in data_output.orders_output.data:
            self.insert_order_data_to_db(order)
        for position in data_output.positions_output.close_data:
            self.insert_position_data_to_db(position, table='close_positions')

        cursor = self.mysql_connection.cursor()
        cursor.execute("TRUNCATE TABLE open_positions ")

        for position in data_output.positions_output.current_data:
            self.insert_position_data_to_db(position, table='open_positions')
