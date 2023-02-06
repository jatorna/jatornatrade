import copy
from subprojects.StockDataWrappers import *
from subprojects.ScreenerWrappers import *
from subprojects.misc import LowLevelFuncions as llw
from subprojects.parsers.ConfigParserEngine import *
from trading_engine.data_handler.DataHandler import DataHandler
import pandas as pd
import numpy as np
import queue

logger = llw.script_logger('SCREENER DH')


class ScreenerDataHandler(DataHandler):

    def __init__(self, market, frequency, sampling, screener_data, config: Config, alert_mgr):

        self.type = DataHandlerType.SCREENER
        self.market = market
        self.frequency = frequency
        self.sampling = sampling

        if config.general.mode == EngineMode.BACKTEST:
            self.screener_data = screener_data
        else:
            self.screener_data = {}

        self.config = config

        self.symbol_list = set()
        self.symbol_data = {}
        self.continue_backtest = True
        self.bar_index = 0
        self.alert_mgr = alert_mgr

    def update_symbol_list(self, current_date):

        if self.config.general.mode == EngineMode.BACKTEST:

            if current_date not in self.screener_data:
                logger.warning('No screener data for epoch: ' + current_date.strftime('%Y/%m/%d %H:%M:%S'))
                return

            symbols_screener = self.screener_data[current_date]

        if self.config.general.mode == EngineMode.REALTIME:
            symbols_screener = self.parse_screener_realtime()
            self.screener_data[current_date] = copy.copy(symbols_screener)

        for symbol in symbols_screener:
            self.symbol_list.add(symbol)

        msg = current_date.strftime('%Y/%m/%d %H:%M:%S') + '\n''Symbols tracked:\n' + str(self.symbol_list)
        self.alert_mgr.send_telegram_alert(msg)

    def create_dataframes(self):

        if self.config.risk_manager.index_check:
            self.symbol_data = {'QQQ': download_from_fhub(self.config.data_handler.finnhub_key, 'QQQ', Frequency.DAILY,
                                                          Market.US),
                                'SPY': download_from_fhub(self.config.data_handler.finnhub_key, 'SPY', Frequency.DAILY,
                                                          Market.US)}

        if self.config.general.mode == EngineMode.BACKTEST:

            logger.info('Loading symbols from screener database')

            all_symbols = set()
            for epoch in self.screener_data:
                for s in self.screener_data[epoch]:
                    all_symbols.add(s)

            for s in all_symbols:
                try:
                    data = pd.read_csv(self.config.data_handler.screener_db_path + '/symbols_data/' + s + '.csv',
                                       delimiter='\t')

                    data.date = pd.to_datetime(data.date)
                    data = data.set_index('date')

                except:
                    logger.error('Not found ' + s + ' data')
                    continue
                self.symbol_data[s] = data

        if self.config.general.mode == EngineMode.REALTIME:
            # TODO: Configure for intraday

            logger.info('Loading symbols data')

            current_date = dt.datetime(dt.datetime.now().year, dt.datetime.now().month,
                                       dt.datetime.now().day)

            for s in self.symbol_list:
                self.symbol_data[s] = download_from_fhub(self.config.data_handler.finnhub_key, s, Frequency.DAILY,
                                                         Market.US)

                if not self.has_current_price(s, current_date):
                    try:
                        self.symbol_data[s] = download_from_yahoo(s, Frequency.DAILY, Market.US)

                        if not self.has_current_price(s, current_date):
                            logger.error('No ' + s + ' data for today')

                    except:
                        logger.error('No ' + s + ' data for today')

    def remove_symbols(self, deactivated_symbols, portfolio, strategies_list):
        msg_header = 'Symbols removed:\n'
        msg = ''
        pending_symbols = set()
        while True:
            try:
                symbol = deactivated_symbols.get(False)
            except queue.Empty:
                break
            else:
                if symbol is not None:
                    for strategy in strategies_list:
                        if portfolio.current_positions[strategy][symbol].shares_qty == 0:
                            msg += symbol + ' '
                            self.symbol_list.remove(symbol)

                            if self.config.general.mode != EngineMode.BACKTEST and symbol in self.symbol_data:
                                del self.symbol_data[symbol]

                        else:
                            pending_symbols.add(symbol)

        for symbol in pending_symbols:
            deactivated_symbols.put(symbol)

        if msg != '':
            self.alert_mgr.send_telegram_alert(msg_header + msg)

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

    def update_dataframes(self, today_symbol_data):
        pass

    def parse_screener_realtime(self):

        if self.config.screener.source == ScreenerProvider.YAHOO:
            symbols = yahoo_screener(self.config.screener.yahoo_user, self.config.screener.yahoo_pass,
                                     self.config.screener.yahoo_screener_id)
        elif self.config.screener.source == ScreenerProvider.FINVIZ:
            symbols = finviz_screener()

        if not len(symbols):
            logger.warning('No screener symbols detected')

        # symbols = finviz_screener()
        return symbols

    def get_screener_data(self):
        return self.screener_data
