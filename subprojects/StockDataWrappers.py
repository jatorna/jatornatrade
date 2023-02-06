from subprojects.types.Common import *
import subprojects.misc.LowLevelFuncions as llw
import sys
from fhub import Session
import datetime as dt
import yfinance as yf

logger = llw.script_logger('STOCK DATA WRAPPER')


def download_from_yahoo(symbol, frequency, market):
    if market == Market.FX:
        symbol = symbol + '=X'

    if frequency == Frequency.DAILY:

        start = dt.datetime(2000, 1, 1)
        data = yf.download(symbol, start=start, end=dt.date.today(), progress=False, auto_adjust=True)
        data.index = data.index.normalize()
        data.index = data.index.tz_localize(None)
        data.index.names = ['date']
        # adjust_factor = (data['Adj Close'] / data['Close']).values
        # data['Close'] = data['Adj Close']
        # del data['Adj Close']
        data.columns = ['high', 'low', 'open', 'close', 'volume']
        data = data.sort_values(['date'], ascending=[True])
        data = data[['open', 'high', 'low', 'close', 'volume']]
        # data['open'] = data['open'] * adjust_factor
        # data['high'] = data['high'] * adjust_factor
        # data['low'] = data['low'] * adjust_factor
        if market != Market.FX:
            data = data[data['volume'] > 0]
        data = data.sort_values(['date'], ascending=[True])

        return data
    else:
        logger.error('No intraday data source implement for yahoo')
        logger.info('Program aborted')
        sys.exit()


def download_from_fhub(finnhub_key, symbol, frequency, market):
    hub = Session(finnhub_key)
    if market == Market.FX:
        symbol = symbol + '=X'

    if frequency == Frequency.DAILY:
        # 2 attempts
        for attempt in range(2):
            try:
                data = hub.candle(symbol, end=(dt.datetime.today() + dt.timedelta(days=1)).strftime(format='%Y-%m-%d'))
                data.index = data.index.normalize()
                data.index = data.index.tz_localize(None)
                data.index.names = ['date']
                data = data[['open', 'high', 'low', 'close', 'volume']]
                if market != Market.FX:
                    data = data[data['volume'] > 0]
                data = data.sort_values(['date'], ascending=[True])

                return data

            except:
                pass
        return None
