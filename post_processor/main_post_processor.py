import datetime as dt
import sys
import os
import logging
import argparse
import subprojects.misc.LowLevelFuncions as llw
from subprojects.FileProcessor import FileProcessor
from subprojects.StatisticsManager import StatisticsManager

logger = llw.script_logger('POST-PROCESSOR')


class ProgramData:

    def __init__(self, program_name, program_version):
        self.program_name = program_name
        self.program_version = program_version
        self.reference_timestamp = str(dt.datetime.now().strftime("%y%m%d_%H%M%S"))
        self.trade_path = None
        self.benchmark_path = None

    def parse_command_line_arguments(self):
        global args
        parser = argparse.ArgumentParser(description='Trading Post Processor Program')
        parser.add_argument("-i", "--input", help="Input trade folder", required=True)
        parser.add_argument("-b", "--benchmark", help="Benchmark trade folder", required=False)
        parser.add_argument("-g", "--log_level", help="Log level", default='INFO', choices=['INFO', 'DEBUG'])
        args = parser.parse_args()

        self.trade_path = args.input
        self.trade_benchmark_path = args.benchmark

        if args.log_level == 'DEBUG':
            logger.setLevel(logging.DEBUG)


program_data = ProgramData('Post-Processor ', 'v0')

program_data.parse_command_line_arguments()

try:
    os.stat(program_data.trade_path)
except:
    logger.error('No trading folder found. Program aborted')
    sys.exit()

if program_data.trade_benchmark_path:
    try:
        os.stat(program_data.trade_benchmark_path)
    except:
        logger.error('No benchmark trading folder found. Program aborted')
        sys.exit()

logging.basicConfig(filename=program_data.trade_path + '/postprocessor.log', filemode='a',
                    format='%(asctime)s [%(levelname)-8s] [%(name)-17s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger.info('##### PROGRAM %s ( VERSION: %s ) started #####' % (program_data.program_name,
                                                                program_data.program_version))


file_processor = FileProcessor(None, None, program_data.trade_path)

if program_data.trade_benchmark_path:
    file_processor_benchmark = FileProcessor(None, None, program_data.trade_benchmark_path)
    equity_data_benchmark = file_processor_benchmark.get_equity_data()
else:
    equity_data_benchmark = None

equity_data = file_processor.get_equity_data()
orders_data = file_processor.get_orders_data()

statistics_manager = StatisticsManager('', program_data.trade_path, equity_data, orders_data, equity_data_benchmark)

try:
    statistics_manager.generate_trading_plots()
except Exception as e:
    logger.error('Error generating trading plots')
    logger.error(e)

try:
    statistics_manager.generate_trading_report()
except Exception as e:
    logger.error('Error generating trading report')
    logger.error(e)

try:
    statistics_manager.generate_trade_statistics()
except Exception as e:
    logger.error('Error generating trade estatistics')
    logger.error(e)

logger.info('### PROGRAM FINISHED ###')
