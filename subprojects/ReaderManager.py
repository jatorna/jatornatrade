from subprojects.parsers import ConfigParserEngine, ConfigParserDataServer, ScreenerDataParser
import subprojects.misc.LowLevelFuncions as llw
import pandas as pd
import glob

logger = llw.script_logger('READER MGR')


class ReaderManager:
    def __init__(self, config_path, output_path):
        self.config_path = config_path
        self.output_path = output_path
        self.screener_data_file_path = ''

    def set_screener_data_file_path(self, screener_data_file):
        self.screener_data_file_path = screener_data_file

    def parse_screener_data_file(self):
        return ScreenerDataParser.parse_screener_file(self.screener_data_file_path)

    def parse_config_trade_engine(self):
        return ConfigParserEngine.parse_config(self.config_path)

    def parse_config_data_server(self):
        return ConfigParserDataServer.parse_config(self.config_path)

    def parse_equity_files(self):
        equity_files = glob.glob(self.output_path+'/equity_*')
        equity_files.sort()
        equity_data = pd.DataFrame()

        for file in equity_files:
            logger.info('Loading equity file: '+file)
            equity_data_tmp = pd.read_csv(file, delim_whitespace=True)
            equity_data_tmp = equity_data_tmp.drop(index=0)

            if len(equity_data_tmp) < 1:
                continue

            equity_data_tmp['Date'] = pd.to_datetime(equity_data_tmp['Date'] +
                                                     equity_data_tmp['Time'], format='%d-%m-%Y%H:%M')
            equity_data_tmp['Equity'] = pd.to_numeric(equity_data_tmp['Equity'])
            equity_data_tmp['Drawndown'] = pd.to_numeric(equity_data_tmp['Drawndown'])
            equity_data_tmp['Total'] = pd.to_numeric(equity_data_tmp['Total'])
            equity_data = equity_data.append(equity_data_tmp)

        del equity_data['Time']
        return equity_data

    def parse_orders_files(self):
        orders_files = glob.glob(self.output_path + '/orders_*')
        orders_data = pd.DataFrame()
        for file in orders_files:
            logger.info('Loading order file: '+file)
            orders_data_tmp = pd.read_csv(file, delim_whitespace=True)
            orders_data_tmp = orders_data_tmp.drop(index=0)
            if len(orders_data_tmp) < 0:
                continue
            orders_data_tmp['Date'] = pd.to_datetime(orders_data_tmp['Date'] +
                                                     orders_data_tmp['Time'], format='%d-%m-%Y%H:%M')
            orders_data = orders_data.append(orders_data_tmp)

        del orders_data['Time']
        return orders_data
