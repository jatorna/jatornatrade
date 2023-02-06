import subprojects.recorders.EquitityWriter
import subprojects.recorders.OrdersWriter
import subprojects.recorders.PositionsWriter
import subprojects.recorders.ScreenerWriter
import subprojects.misc.LowLevelFuncions as llw
import os.path

logger = llw.script_logger('WRITER MANAGER')


class WriterManager:
    def __init__(self, output_path):
        self.output_path = output_path
        self.output_files = []

    def write_header(self, session_id, continue_session, output_files):
        self.output_files = output_files

        if "equity" in self.output_files:
            if not (continue_session and os.path.isfile(self.output_path + '/equity_' + session_id + '.txt')):
                subprojects.recorders.EquitityWriter.print_header(session_id, self.output_path)
                logger.info('File ' + self.output_path + '/equity_' + session_id + '.txt opened')

        if "orders" in self.output_files:
            if not (continue_session and os.path.isfile(self.output_path + '/orders_' + session_id + '.txt')):
                subprojects.recorders.OrdersWriter.print_header(session_id, self.output_path)
                logger.info('File ' + self.output_path + '/orders_' + session_id + '.txt opened')

        if "positions" in self.output_files:
            if not (continue_session and os.path.isfile(self.output_path + '/positions_' + session_id + '.txt')):
                subprojects.recorders.PositionsWriter.print_header(True, session_id, self.output_path)
                logger.info('File ' + self.output_path + '/positions_' + session_id + '.txt opened')

        if "screener" in self.output_files:
            if not (continue_session and os.path.isfile(self.output_path + '/screener_data_' + session_id + '.txt')):
                subprojects.recorders.ScreenerWriter.print_header(session_id, self.output_path)
                logger.info('File ' + self.output_path + '/screener_data_' + session_id + '.txt opened')

        if "curpositi" in self.output_files:
            subprojects.recorders.PositionsWriter.print_header(False, session_id, self.output_path)
            logger.info('File ' + self.output_path + '/curpositi_' + session_id + '.txt opened')

    def write_equity(self, session_id, equity_output):
        if "equity" in self.output_files:
            subprojects.recorders.EquitityWriter.print_data(session_id, self.output_path, equity_output)

    def write_orders(self, session_id, orders_output):
        if "orders" in self.output_files:
            subprojects.recorders.OrdersWriter.print_data(session_id, self.output_path, orders_output)

    def write_positions(self, session_id, positions_output):
        if "positions" in self.output_files:
            subprojects.recorders.PositionsWriter.print_data(True, session_id, self.output_path, positions_output)
        if "curpositi" in self.output_files:
            subprojects.recorders.PositionsWriter.print_data(False, session_id, self.output_path, positions_output)

    def write_screener(self, session_id, screener_output):
        if "screener" in self.output_files:
            subprojects.recorders.ScreenerWriter.print_data(session_id, self.output_path, screener_output)
