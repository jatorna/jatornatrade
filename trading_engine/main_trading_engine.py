import datetime as dt
import sys
import os
from subprojects.FileProcessor import FileProcessor
from trading_engine.TradingEngineOffline import TradingEngineOffline
from trading_engine.TradingEngineRT import TradingEngineRT
import subprojects.misc.LowLevelFuncions as llw
from subprojects.types.Common import *
import logging

logger = llw.script_logger('TRADING ENGINE')

# Global variables
config_path = ''
session_id = ''
output_path = ''
reset_metrics = False


class ProgramData:

    def __init__(self, program_name, program_version):
        self.program_name = program_name
        self.program_version = program_version
        self.reference_timestamp = str(dt.datetime.now().strftime("%y%m%d_%H%M%S"))

    def log_header_line(self):
        logger.info('##### PROGRAM %s ( VERSION: %s ) started #####' % (self.program_name, self.program_version))

    def log_version_line_and_exit(self):
        print('%s (version: %s)' % (self.program_name, self.program_version))
        exit(0)

    def log_man_page_and_exit(self):
        print('##### PROGRAM %s ( VERSION: %s ) #####' % (self.program_name, self.program_version))
        print('Usage: python3 %s [compulsory inputs] {optional inputs}' % sys.argv[0])
        print('Usage: python3 %s [config file] [session ID] [output dir] {optional inputs}' %
              sys.argv[0].split('/')[-1])
        print()
        print('Allowed options:                                                                     \n'
              '                                                                                     \n'
              'General options:                                                                     \n' 
              '  --help                                     Produce help message                    \n'
              '  --version                                  Output the version                      \n'
              '                                                                                     \n'
              'Monitoring options:                                                                  \n'
              '  --reset_metrics                            Reset monitoring metrics in database    \n'
              '                                                                                     \n')
        exit(0)

    def detect_standard_inputs(self, argv):

        if '--help' in argv:
            self.log_man_page_and_exit()
        elif '--version' in argv:
            self.log_version_line_and_exit()

    def get_compulsory_inputs(self):
        if len(sys.argv) < 4:
            logger.error('Wrong number of inputs received')
            self.log_man_page_and_exit()

        else:
            global config_path, session_id, output_path
            config_path = sys.argv[1]
            session_id = sys.argv[2]
            output_path = sys.argv[3]

    def get_optional_inputs(self):
        global reset_metrics
        reset_metrics = llw.check_input_tag('--reset_metrics', sys.argv, True, False)


##################################################
#  INITIAL OPS  ##################################
##################################################

program_data = ProgramData('Trading Engine ', 'v0')

# INPUT COMPULSORY DATA ###
#####################

program_data.detect_standard_inputs(sys.argv)

program_data.get_compulsory_inputs()

try:
    os.stat(output_path)
except:
    os.mkdir(output_path)

logging.basicConfig(filename=output_path+'/'+session_id+'.log', filemode='a',
                        format='%(asctime)s [%(levelname)-8s] [%(name)-17s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger.info('##### PROGRAM %s ( VERSION: %s ) started #####' % (program_data.program_name,
                                                                program_data.program_version))

# INPUT OPTIONAL DATA ###
#####################

program_data.get_optional_inputs()

##################################################
#  PROCESS LAUNCHING  ############################
##################################################

file_processor = FileProcessor(config_path, session_id, output_path)

config = file_processor.get_trade_engine_config()
config.general.output_path = output_path
config.general.session_id = session_id

# Read input config files
if config.data_handler.type == DataHandlerType.SCREENER and config.general.mode == EngineMode.BACKTEST:
    file_processor.reader_manager.set_screener_data_file_path(config.data_handler.screener_db_path + '/screener_data'
                                                                                                     '.txt')
    if not file_processor.parse_screener_data():
        logger.error('Screener data file incorrect : ' + config.data_handler.screener_db_path)
        logger.info('Aborting Program')
        sys.exit()


logger.info('Mode: %s', config.general.mode.value)
logger.info('Continue session: ' + str(config.general.continue_session))

if config.general.mode == EngineMode.BACKTEST:
    backtest = TradingEngineOffline(config, output_path, file_processor, reset_metrics)
    backtest.run_backtest()

if config.general.mode == EngineMode.REALTIME:
    trading_engine = TradingEngineRT(config, output_path, file_processor, reset_metrics)
    trading_engine.run_trading_engine()

logger.info('### PROGRAM FINISHED ###')
