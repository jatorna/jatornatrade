import shutil
from subprojects.ReaderManager import ReaderManager
from subprojects.WriterManager import WriterManager
import subprojects.misc.LowLevelFuncions as llw


logger = llw.script_logger('FILE PROCESSOR')


class FileProcessor:
    def __init__(self, config_path, session_id, output_path):
        self.config_path = config_path
        self.session_id = session_id
        self.output_path = output_path
        self.reader_manager = ReaderManager(self.config_path, self.output_path)
        self.writer_manager = WriterManager(self.output_path)
        self.files_data = {'screener_data': {}}
        self.continue_session = False

        if self.config_path is not None:
            self.copy_config()

    def copy_config(self):
        shutil.copy(self.config_path, self.output_path)

    def parse_screener_data(self):
        self.files_data['screener_data'] = self.reader_manager.parse_screener_data_file()

        if self.files_data['screener_data']:
            logger.log(5, 'Screener data file parsed correctly')
            return True
        else:
            logger.error('Error reading screener file')
            return False

    def get_trade_engine_config(self):
        config = self.reader_manager.parse_config_trade_engine()
        return config

    def get_data_server_config(self):
        config = self.reader_manager.parse_config_data_server()
        return config

    def get_equity_data(self):
        equity_data = self.reader_manager.parse_equity_files()
        return equity_data

    def get_orders_data(self):
        orders_data = self.reader_manager.parse_orders_files()
        return orders_data

    def write_headers(self, config):
        self.continue_session = config.general.continue_session
        self.writer_manager.write_header(self.session_id, self.continue_session, config.core)

    def write_sequential_data(self, data_output):
        self.writer_manager.write_equity(self.session_id, data_output.equity_output)
        self.writer_manager.write_orders(self.session_id, data_output.orders_output)
        self.writer_manager.write_positions(self.session_id, data_output.positions_output)
        self.writer_manager.write_screener(self.session_id, data_output.screener_symbols_output)
