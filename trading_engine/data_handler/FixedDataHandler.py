from trading_engine.data_handler.DataHandler import DataHandler
import MySQLdb as mdb
from subprojects.misc import LowLevelFuncions as llw
from subprojects.types.Common import *
from subprojects.StockDataWrappers import *
from subprojects.parsers.ConfigParserEngine import Config
import pandas as pd
import numpy as np
import copy

logger = llw.script_logger('FIXED DH')


class FixedDataHandler(DataHandler):

    def __init__(self, config: Config):
        self.config = config
        self.type = DataHandlerType.FIXED
        self.market = config.general.market
        self.symbol_list = copy.copy(config.symbol_list)
        self.frequency = config.backtest.frequency
        self.sampling = config.backtest.sampling
        if config.data_handler.source == DataHandlerSource.DATABASE:
            self.mysql_connection = mdb.connect(host=config.mysqlconf.db_host,
                                                user=config.mysqlconf.db_user,
                                                passwd=config.mysqlconf.db_pass,
                                                port=config.mysqlconf.db_port,
                                                db=config.mysqlconf.db_name)
        self.symbol_data = {}
        self.continue_backtest = True
        self.bar_index = 0

    def reset_mysql_connection(self, mysql_config):
        self.mysql_connection = mdb.connect(host=mysql_config.db_host,
                                            user=mysql_config.db_user,
                                            passwd=mysql_config.db_pass,
                                            port=mysql_config.db_port,
                                            db=mysql_config.db_name)

    def create_dataframes(self):
        if self.config.data_handler.source == DataHandlerSource.DATABASE:
            data_sql = self.load_symbols_data_from_database()
            for s in self.symbol_list:
                self.symbol_data[s] = pd.DataFrame()
                self.symbol_data[s]['date'] = data_sql[data_sql['symbol'] == s]['date']
                self.symbol_data[s]['open'] = data_sql[data_sql['symbol'] == s]['open']
                self.symbol_data[s]['high'] = data_sql[data_sql['symbol'] == s]['high']
                self.symbol_data[s]['low'] = data_sql[data_sql['symbol'] == s]['low']
                self.symbol_data[s]['close'] = data_sql[data_sql['symbol'] == s]['close']
                self.symbol_data[s]['volume'] = data_sql[data_sql['symbol'] == s]['volume']
                self.symbol_data[s] = self.symbol_data[s].set_index('date')

                if self.frequency == Frequency.INTRADAY:
                    resample_str = str(self.sampling) + 'T'
                    self.symbol_data[s] = (self.symbol_data[s].resample(resample_str, label='right', closed='right')
                                           .agg({'open': 'first', 'close': 'last',
                                                 'high': np.max, 'low': np.min,
                                                 'volume': np.sum})
                                           )
                    self.symbol_data[s] = self.symbol_data[s].dropna()
        elif self.config.data_handler.source == DataHandlerSource.PROVIDER:
            self.load_symbols_data_from_data_provider(self.config.general.market)
        elif self.config.data_handler.source == DataHandlerSource.CSV:
            self.load_symbols_data_from_csv(self.config.general.market)

    def has_current_price(self, symbol, current_date):
        try:
            data = self.symbol_data[symbol].loc[current_date:current_date]
            if len(data) > 0:
                return True

            else:
                return False

        except:
            # logger.error('No data for ticker ' + symbol + ' at date ' + current_time.strftime('%Y-%m-%d'))
            return False

    def get_current_tick(self, symbol, current_date, price_type):
        try:
            data = self.symbol_data[symbol].loc[current_date:current_date]
            if len(data) > 1:
                logger.warning('Duplicated data for ticker ' + symbol + ' at date ' + current_date.strftime('%Y-%m-%d'))
            return data[price_type].values[-1]

        except:
            # logger.error('No data for ticker ' + symbol + ' at date ' + current_time.strftime('%Y-%m-%d'))
            return

    def get_last_price(self, symbol, current_date):
        try:
            data = self.symbol_data[symbol].loc[:current_date]
            return data['close'].values[-1]

        except:
            # logger.error('No data for ticker ' + symbol + ' at date ' + current_time.strftime('%Y-%m-%d'))
            return

    def get_current_data(self, symbol, start_date, current_date):
        data = self.symbol_data[symbol].loc[start_date:current_date]
        return data
        # else:
        #     logger.error('No data for ticker '+symbol+ ' at date '+current_time.strftime('%Y-%m-%d'))

    def valid_close_price(self, symbol, current_date):
        data = self.symbol_data[symbol].loc[current_date:current_date]
        index_range = range(data.index[0] - 10, data.index[0] + 10)
        symbol_data = self.symbol_data[symbol]
        symbol_data = symbol_data[symbol_data.index.isin(index_range)]
        mean_value = np.mean(symbol_data['close'].values)

        if data['close'].values[0] / mean_value > 1.4 or data['close'].values[0] / mean_value < 0.5:
            return False
        else:
            return True

    def load_market_data(self):
        sql_str = """SELECT * FROM intraday_price WHERE exchange = '%s';""" % self.market
        data_sql = pd.read_sql_query(sql_str, con=self.mysql_connection)
        return data_sql

    def load_symbols_data_from_database(self):
        logger.info('Loading symbols data from database')

        s_list = []
        for s in self.symbol_list:
            s_list.append(str("'" + s + "'"))

        s = ', '.join(s_list)

        if self.frequency == Frequency.DAILY:
            table = 'daily_price'
        if self.frequency == Frequency.INTRADAY:
            table = 'intraday_price'

        sql_str = """SELECT * FROM %s WHERE symbol IN (%s);""" % (table, s)
        data_sql = pd.read_sql_query(sql_str, con=self.mysql_connection)
        logger.log(5, 'Historical data load succesfully')
        return data_sql

    def load_symbols_data_from_data_provider(self, market: Market):
        if self.config.data_handler.provider == DataProviderSource.YAHOO:
            logger.info('Downloading data from yahoo')
            for s in self.symbol_list:
                self.symbol_data[s] = download_from_yahoo(s, Frequency.DAILY, market)

        if self.config.data_handler.provider == DataProviderSource.FINNHUB:
            logger.info('Downloading data from finnhub')
            for s in self.symbol_list:
                self.symbol_data[s] = download_from_fhub(self.config.data_handler.finnhub_key, s,
                                                         Frequency.DAILY, Market.US)

    def load_symbols_data_from_csv(self, market: Market):
        logger.info('Downloading data from csv')
        for s in self.symbol_list:
            try:
                data = pd.read_csv(
                    self.config.data_handler.csv_db_path + '/historical/daily/' + market.value + '/' + s + '.csv',
                    delimiter='\t')

                data.date = pd.to_datetime(data.date)
                data = data.set_index('date')
                self.symbol_data[s] = data
            except Exception as e:
                logger.warning('No data for symbol ' + s)

    def update_dataframes(self, today_symbol_data):

        if self.frequency == Frequency.INTRADAY:
            for symbol in today_symbol_data:
                if symbol in self.symbol_list:
                    try:
                        today_symbol_data[symbol] = today_symbol_data[symbol].set_index('date')
                        resample_str = str(self.sampling) + 'T'
                        today_symbol_data[symbol] = (
                            today_symbol_data[symbol].resample(resample_str, label='right', closed='right').agg(
                                {'open': 'first', 'close': 'last', 'high': np.max, 'low': np.min, 'volume': np.sum}))
                        today_symbol_data[symbol] = today_symbol_data[symbol].dropna()

                        self.symbol_data[symbol] = self.symbol_data[symbol].dropna()
                        self.symbol_data[symbol] = self.symbol_data[symbol].append(today_symbol_data[symbol], sort=True)
                        self.symbol_data[symbol] = self.symbol_data[symbol][::-1]
                        self.symbol_data[symbol] = self.symbol_data[symbol].iloc[
                            np.unique(self.symbol_data[symbol].index.values, return_index=True)[1]]

                    except:
                        pass

        # if self.frequency == 'daily':
        #     current_date = dt.datetime(dt.datetime.now().year, dt.datetime.now().month, dt.datetime.now().day)
        #     for symbol in tick_dict:
        #         if symbol in self.symbol_list:
        #
        #             self.symbol_data[symbol].loc[current_date] = [tick_dict[symbol].price, tick_dict[symbol].price,\
        #                                                           tick_dict[symbol].price, tick_dict[symbol].price,
        #                                                           tick_dict[symbol].volume]
