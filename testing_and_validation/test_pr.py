import pickle
import unittest
import re
from os import listdir
import subprojects.misc.LowLevelFuncions as llw
from subprojects.parsers.ConfigParserEngine import parse_config as cf_te
import pandas as pd


logger = llw.script_logger('TESTING')


class Testing(unittest.TestCase):

    def test_configs(self):

        print('')
        logger.info('Config Test')

        files = listdir('trading_engine/configs')

        for config_file in files:
            if config_file[-4:] != '.ini':
                continue
            cf_te('trading_engine/configs/' + config_file)

        self.assertEqual(True, True)

        logger.log(5, 'OK')

    def test_backtest(self):

        print('')
        logger.info('Backtest Test')

        with open('output_backtest/backtest.dat', "rb") as f:
            pending_orders_list = pickle.load(f)
            screener_deactivated_symbols = pickle.load(f)
            session_data = pickle.load(f)

        total = round(session_data[1][-1]['total'], 3)

        equity_data = pd.read_csv('output_backtest/equity_backtest.txt', skiprows=[1], delim_whitespace=True)
        orders_data = pd.read_csv('output_backtest/orders_backtest.txt', skiprows=[1], delim_whitespace=True)
        positions_data = pd.read_csv('output_backtest/positions_backtest.txt', skiprows=[1], delim_whitespace=True)

        self.assertEqual(18102.791, total)
        self.assertEqual(18102.791, round(equity_data['Total'].values[-1], 3))
        self.assertEqual(-18.0543, round(positions_data['Profit'].values[-1], 4))
        self.assertEqual(61, len(positions_data))
        self.assertEqual(126, len(orders_data))
        self.assertEqual(1566, len(equity_data))

        logger.log(5, 'OK')

    def test_backtest_screener(self):

        print('')
        logger.info('Backtest Screener Test')

        with open('output_backtest_screener/backtest_screener.dat', "rb") as f:
            pending_orders_list = pickle.load(f)
            screener_deactivated_symbols = pickle.load(f)
            session_data = pickle.load(f)

        total = round(session_data[1][-1]['total'], 3)

        equity_data = pd.read_csv('output_backtest_screener/equity_backtest_screener.txt', skiprows=[1],
                                  delim_whitespace=True)
        orders_data = pd.read_csv('output_backtest_screener/orders_backtest_screener.txt', skiprows=[1],
                                  delim_whitespace=True)
        positions_data = pd.read_csv('output_backtest_screener/positions_backtest_screener.txt', skiprows=[1],
                                     delim_whitespace=True)

        self.assertEqual(24923.909, total)
        self.assertEqual(24923.909, round(equity_data['Total'].values[-1], 3))
        self.assertEqual(-236.2360, round(positions_data['Profit'].values[-1], 4))
        self.assertEqual(190, len(positions_data))
        self.assertEqual(383, len(orders_data))
        self.assertEqual(1566, len(equity_data))

        logger.log(5, 'OK')

    def test_post_processor(self):

        print('')
        logger.info('Post-Processor Test')

        f = open("output_backtest/postprocessor.log", "r")
        pattern1 = "ERROR"

        result = True
        for line in f:
            if re.search(pattern1, line):
                result = False

        f.close()

        self.assertEqual(True, result)

        logger.log(5, 'OK')


if __name__ == '__main__':
    logger.info('Launching Pull Request Test')

    unittest.main()
