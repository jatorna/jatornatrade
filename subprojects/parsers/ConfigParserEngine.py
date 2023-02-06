import configparser
import sys
import datetime as dt
import subprojects.misc.LowLevelFuncions as llf
from subprojects.types.Common import *
from subprojects.resources.Constants import SymbolsResources
import traceback

logger = llf.script_logger('TE CONFIG PARSER')


#################
# CONFIG PARSER #
#################


def parse_config(config_path):
    config_file = configparser.ConfigParser()
    config_file.read(config_path)

    config = Config()

    try:
        config.general.mode = EngineMode(config_file['GENERAL']['Mode'].upper())
        config.general.market = Market(config_file['GENERAL']['Market'].upper())
        config.general.continue_session = config_file.getboolean('GENERAL', 'ContinueSession')
        config.general.tgm_alerts = config_file.getboolean('GENERAL', 'TelegramAlerts')
        config.general.alerts_bot_group = config_file['GENERAL']['AlertsBotGroup']
        config.general.alerts_bot_token = config_file['GENERAL']['AlertsBotToken']
        config.general.monitoring = config_file.getboolean('GENERAL', 'Monitoring')

        config.data_handler.type = DataHandlerType(config_file['DATA_HANDLER']['Type'].upper())
        config.data_handler.source = DataHandlerSource(config_file['DATA_HANDLER']['Source'].upper())
        config.data_handler.provider = DataProviderSource(config_file['DATA_HANDLER']['Provider'].upper())
        config.data_handler.csv_db_path = config_file.get('DATA_HANDLER', 'DataCSV')
        config.data_handler.screener_db_path = config_file.get('DATA_HANDLER', 'ScreenerDB')
        config.data_handler.finnhub_key = config_file.get('DATA_HANDLER', 'FhbKey')
        config.data_handler.alpha_key = config_file.get('DATA_HANDLER', 'AlphaKey')

        config.screener.provider = ScreenerProvider(config_file['SCREENER']['Provider'].upper())
        config.screener.yahoo_user = config_file.get('SCREENER', 'YahooUser')
        config.screener.yahoo_pass = config_file.get('SCREENER', 'YahooPass')
        config.screener.yahoo_screener_id = config_file.get('SCREENER', 'YahooScreenerID')

        config.mysqlconf.db_host = config_file['MYSQL']['Hostname']
        config.mysqlconf.db_port = config_file.getint('MYSQL', 'Port')
        config.mysqlconf.db_user = config_file['MYSQL']['User']
        config.mysqlconf.db_pass = config_file['MYSQL']['Password']
        config.mysqlconf.db_name = config_file['MYSQL']['DbName']

        config.backtest.start_date = dt.datetime.strptime(config_file['BACKTEST']['StartDate'] + ' ' +
                                                          config_file['BACKTEST']['StartTime'], '%d/%m/%Y %H:%M:%S')
        config.backtest.end_date = dt.datetime.strptime(config_file['BACKTEST']['EndDate'] + ' ' +
                                                        config_file['BACKTEST']['EndTime'], '%d/%m/%Y %H:%M:%S')
        config.backtest.frequency = Frequency(config_file['BACKTEST']['Frequency'].upper())
        config.backtest.sampling = config_file.getint('BACKTEST', 'MinuteSampling')

        config.realtime.mode = RTMode(config_file['REALTIME']['Mode'].upper())
        config.realtime.frequency = Frequency(config_file['REALTIME']['Frequency'].upper())
        config.realtime.sampling = config_file.getint('REALTIME', 'MinuteSampling')
        config.realtime.daily_exec_time = dt.time.fromisoformat(config_file['REALTIME']['DailyExecTime'])
        config.realtime.hostname = config_file['REALTIME']['DataHostname']
        config.realtime.port = config_file.getint('REALTIME', 'DataPort')

        config.portfolio.initial_capital = config_file.getfloat('PORTFOLIO', 'InitialCapital')
        config.portfolio.commiss_model = ComissModel(config_file['PORTFOLIO']['CommissModel'].upper())
        config.portfolio.commission = config_file.getfloat('PORTFOLIO', 'Commission')
        config.portfolio.max_commission = config_file.getfloat('PORTFOLIO', 'MaxCommission')
        config.portfolio.min_commission = config_file.getfloat('PORTFOLIO', 'MinCommission')
        config.portfolio.spread = config_file.getfloat('PORTFOLIO', 'Spread')
        config.portfolio.slippage = config_file.getfloat('PORTFOLIO', 'Slippage')
        config.portfolio.swap = config_file.getfloat('PORTFOLIO', 'Swap')
        config.portfolio.signal_rate = config_file.getint('PORTFOLIO', 'SignalRate')

        config.ppv.interpolate = config_file.getboolean('PPV', 'Interpolate')
        config.ppv.smoothing = config_file.getboolean('PPV', 'Smoothing')

        config.risk_manager.index_check = config_file.getboolean('RISK_MANAGER', 'IndexCheck')
        config.risk_manager.order_invest = config_file.getfloat('RISK_MANAGER', 'OrderInvest')
        config.risk_manager.limit_orders = config_file.getboolean('RISK_MANAGER', 'LimitOrders')
        config.risk_manager.comm_in_limits = config_file.getboolean('RISK_MANAGER', 'CommInLimits')

        config.mac_strategy.long_window = config_file.getint('MAC', 'LongWindow')
        config.mac_strategy.short_window = config_file.getint('MAC', 'ShortWindow')
        config.mac_strategy.long_window = config_file.getint('MAC', 'LongWindow')
        config.mac_strategy.limit_orders = config_file.getboolean('MAC', 'LimitOrders')
        config.mac_strategy.stop_loss = config_file.getfloat('MAC', 'StopLoss')
        config.mac_strategy.take_profit = config_file.getfloat('MAC', 'TakeProfit')
        config.mac_strategy.trailing_stop = config_file.getboolean('MAC', 'TrailingStop')
        config.mac_strategy.enable_debug_file = config_file.getboolean('MAC', 'DebugFile')

        config.bol_strategy.allowed_signals = AllowedSignals(config_file['BOL']['AllowedSignals'].upper())
        config.bol_strategy.window = config_file.getint('BOL', 'Window')
        config.bol_strategy.n_std = config_file.getint('BOL', 'NStd')
        config.bol_strategy.limit_orders = config_file.getboolean('BOL', 'LimitOrders')
        config.bol_strategy.stop_loss = config_file.getfloat('BOL', 'StopLoss')
        config.bol_strategy.take_profit = config_file.getfloat('BOL', 'TakeProfit')
        config.bol_strategy.trailing_stop = config_file.getboolean('BOL', 'TrailingStop')
        config.car_strategy.enable_debug_file = config_file.getboolean('BOL', 'DebugFile')

        config.car_strategy.limit_orders = config_file.getboolean('CAR', 'LimitOrders')
        config.car_strategy.stop_loss = config_file.getfloat('CAR', 'StopLoss')
        config.car_strategy.take_profit = config_file.getfloat('CAR', 'TakeProfit')
        config.car_strategy.trailing_stop = config_file.getboolean('CAR', 'TrailingStop')
        config.car_strategy.enable_debug_file = config_file.getboolean('CAR', 'DebugFile')

    except Exception as e:
        logger.error('Error parsing config')
        logger.error('Program interrumped')
        logger.error(traceback.format_exc())
        sys.exit()

    # TODO: Save these information in a dictionary
    if config.general.market == Market('MC'):
        market_symbol_list = SymbolsResources.MC_SYMBOLS
    elif config.general.market == Market('DE'):
        market_symbol_list = SymbolsResources.DE_SYMBOLS
    elif config.general.market == Market('FX'):
        market_symbol_list = SymbolsResources.FX_SYMBOLS
    elif config.general.market == Market('CC'):
        market_symbol_list = SymbolsResources.CC_SYMBOLS
    elif config.general.market == Market('US'):
        market_symbol_list = SymbolsResources.US_SYMBOLS

    # TODO: Improve better data check
    for symbol in config_file.items('SYMBOLS'):
        if symbol[1] == 'true' and symbol[0].upper() in market_symbol_list:
            config.symbol_list.append(symbol[0].upper())
        elif symbol[1] == 'true' and symbol[0].upper() not in market_symbol_list:
            logger.warning(symbol[0] + ' not in ' + config.general.market.value + ' market. Symbol discarded.')

    for strategy in config_file.items('STRATEGIES'):
        if config_file.getboolean('STRATEGIES', strategy[0]):
            config.strategies.append(strategy[0])

    for output_file in config_file.items('CORE'):
        if config_file.getboolean('CORE', output_file[0]):
            config.core.append(output_file[0])

    logger.log(5, 'Config parsed correctly')

    return config


class ConfigGeneral:
    mode: EngineMode
    market: Market
    continue_session: bool
    tgm_alerts: bool
    alerts_bot_group: str
    alerts_bot_token: str
    monitoring: bool
    output_path: str
    session_id: str


class ConfigDataHandler:
    type: DataHandlerType
    screener_db_path: str
    csv_db_path: str
    source: DataHandlerSource
    provider: DataProviderSource
    finnhub_key: str
    alpha_key: str


class ConfigScreener:
    source: ScreenerProvider
    yahoo_user: str
    yahoo_pass: str
    yahoo_screener_id: str


class ConfigMysql:
    db_host: str
    db_port: int
    db_user: str
    db_pass: str
    db_name: str


class ConfigBacktest:
    start_date: str
    end_date: str
    frequency: Frequency
    sampling: int


class ConfigPortfolio:
    initial_capital: int
    commiss_model: ComissModel
    commission: int
    max_commission: int
    min_commission: int
    spread: int
    slippage: int
    swap: int
    signal_rate: int


class ConfigPPV:
    interpolate: bool
    smoothing: bool


class ConfigRiskManager:
    index_check: bool
    limit_orders: bool
    comm_in_limits: bool
    order_invest: int


class ConfigRealtime:
    frequency: Frequency
    sampling: int
    daily_exec_time: str
    hostname: str
    port: int


class ConfigMAC:
    allowed_signals: AllowedSignals
    long_window: int
    short_window: int
    limit_orders: bool
    stop_loss: int
    take_profit: int
    trailing_stop: bool
    enable_debug_file: bool


class ConfigBOL:
    allowed_signals: AllowedSignals
    window: int
    n_std: int
    limit_orders: bool
    stop_loss: int
    take_profit: int
    trailing_stop: bool
    enable_debug_file: bool


class ConfigCAR:
    limit_orders: bool
    stop_loss: int
    take_profit: int
    trailing_stop: bool
    enable_debug_file: bool


class Config:
    general = ConfigGeneral()
    data_handler = ConfigDataHandler()
    screener = ConfigScreener()
    mysqlconf = ConfigMysql()
    backtest = ConfigBacktest()
    realtime = ConfigRealtime()
    portfolio = ConfigPortfolio()
    ppv = ConfigPPV()
    risk_manager = ConfigRiskManager()
    mac_strategy = ConfigMAC()
    bol_strategy = ConfigBOL()
    car_strategy = ConfigCAR()
    core = []
    strategies = []
    symbol_list = []
