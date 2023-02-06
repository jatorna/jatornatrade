from enum import Enum


class EngineMode(Enum):
    BACKTEST = 'BACKTEST'
    REALTIME = 'REALTIME'


class DataServerMode(Enum):
    HISTORICAL = 'HISTORICAL'
    REALTIME = 'REALTIME'


class RTMode(Enum):
    DEMO = 'DEMO'


class Frequency(Enum):
    DAILY = 'DAILY'
    INTRADAY = 'INTRADAY'


class ComissModel(Enum):
    NONE = 'NONE'
    FIXED = 'FIXED'
    COMBINED = 'COMBINED'
    VARIABLE = 'VARIABLE'
    DEGIRO = 'DEGIRO'


class Market(Enum):
    MC = 'MC'
    US = 'US'
    FX = 'FX'
    CC = 'CC'
    DE = 'DE'


class Exchange(Enum):
    NYSE = 'NYSE'
    NASDAQ = 'NASDAQ'


class AllowedSignals(Enum):
    SHORT = 'SHORT'
    LONG = 'LONG'
    ALL = 'ALL'


class OrderType(Enum):
    SHORT = 'SHORT'
    LONG = 'LONG'
    EXIT = 'EXIT'


class OrderDirection(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class SignalType(Enum):
    MKT = 'MKT'
    LMT = 'LMT'
    USR = 'USR'
    STL = 'STL'
    TKP = 'TKP'


class PositionStatus(Enum):
    OUT = 'OUT'
    LONG = 'LONG'
    SHORT = 'SHORT'
    STAND_BY = 'STAND-BY'


class DataProviderSource(Enum):
    ALPHA = 'ALPHA'
    YAHOO = 'YAHOO'
    FINNHUB = 'FINNHUB'
    BOLSAMANIA = 'BOLSAMANIA'
    REPLAY = 'REPLAY'


class DataHandlerType(Enum):
    FIXED = 'FIXED'
    SCREENER = 'SCREENER'


class DataHandlerSource(Enum):
    PROVIDER = 'PROVIDER'
    DATABASE = 'DATABASE'
    CSV = 'CSV'


class ScreenerProvider(Enum):
    YAHOO = 'YAHOO'
    FINVIZ = 'FINVIZ'
