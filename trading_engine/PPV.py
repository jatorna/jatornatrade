from subprojects.misc import LowLevelFuncions as llw
import pandas as pd
from pykalman import KalmanFilter

logger = llw.script_logger('PPV')


class PPV:

    def __init__(self, config, data_handler):
        self.config = config
        self.data_handler = data_handler
        self.ppv_data = {}

    def process(self):

        logger.info('Starting pre-processing data')

        kf = KalmanFilter(transition_matrices=[1], observation_matrices=[1], initial_state_mean=0,
                          initial_state_covariance=1, observation_covariance=1, transition_covariance=.05)

        for symbol in self.data_handler.symbol_data:

            if not len(self.data_handler.symbol_data[symbol]):
                continue

            start_time = self.data_handler.symbol_data[symbol].index[0]
            end_time = self.data_handler.symbol_data[symbol].index[-1]
            days = pd.date_range(start_time, end_time)
            self.ppv_data[symbol] = self.data_handler.symbol_data[symbol][['close']].copy()

            if self.config.ppv.interpolate:
                self.ppv_data[symbol] = self.ppv_data[symbol].reindex(days).interpolate(method='time')

            if self.config.ppv.smoothing:
                state_means, _ = kf.filter(self.ppv_data[symbol].close)
                self.ppv_data[symbol]['close'] = state_means

        logger.log(5, 'Pre-processing data finished correctly')

    def get_current_data(self, symbol, start_date, current_date):
        data = self.ppv_data[symbol].loc[start_date:current_date]
        return data
