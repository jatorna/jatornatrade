import queue
import datetime as dt
from trading_engine.strategies.Mac import MovingAverageCrossStrategy
from trading_engine.strategies.Bol import BollingerStrategy
from trading_engine.strategies.Bah import BuyAndHoldStrategy
from trading_engine.strategies.Car import CarvasBoxStrategy
from trading_engine.Portfolio import Portfolio
from trading_engine.Execution import SimulatedExecutionHandler
from trading_engine.data_handler.FixedDataHandler import FixedDataHandler
from trading_engine.data_handler.ScreenerDataHandler import ScreenerDataHandler
from trading_engine.DataProcessor import DataProcessor
from trading_engine.RiskManager import RiskManager
from trading_engine.EventDrivenManager import event_driven_process
from trading_engine.SessionManager import SessionManager
from trading_engine.MetricsManager import MetricsManager
from trading_engine.PPV import PPV
from subprojects.StatisticsManager import StatisticsManager
from subprojects.AlertManager import AlertManager
import subprojects.misc.LowLevelFuncions as llw
from subprojects.types.Common import *
from subprojects.resources.Constants import MarketCalendar
from subprojects.types.Stats import Stats
import sys

logger = llw.script_logger('BACKTEST')


class TradingEngineOffline:

    def __init__(self, config, output_path, file_processor, reset_metrics):
        self.config = config
        self.output_path = output_path
        self.file_processor = file_processor
        self.reset_metrics = reset_metrics

    def run_backtest(self):
        # Initialize variables and objects
        config = self.config
        file_processor = self.file_processor
        output_path = self.output_path
        session_id = file_processor.session_id

        logger.info('Launching backtest')
        logger.info('Session ID: ' + session_id)
        logger.info('Processing main configuration')
        logger.info(
            'Period time : ' + config.backtest.start_date.strftime(
                '%Y/%m/%d %H:%M:%S') + ' to ' + config.backtest.end_date.strftime('%Y/%m/%d %H:%M:%S'))

        if config.backtest.end_date <= config.backtest.start_date:
            logger.error('End date not valid. Program aborted')
            sys.exit()

        logger.info('Data Handler mode: ' + config.data_handler.type.value)
        logger.info('Frequency mode: ' + config.backtest.frequency.value)
        logger.info('PPV - ' + 'Interpolate: ' + str(config.ppv.interpolate) + ', Smoothing: ' +
                    str(config.ppv.smoothing))

        if config.backtest.frequency == Frequency.DAILY:

            config.backtest.start_date = config.backtest.start_date.replace(hour=0, minute=0, second=0)
            sampling_minutes = 24 * 60

        elif config.backtest.frequency == Frequency.INTRADAY:

            config.backtest.start_date = config.backtest.start_date.replace(second=0)
            sampling_minutes = config.backtest.sampling
            logger.info('Sampling epochs [min]: ' + str(sampling_minutes))

        #################
        # INITIAL STATS #
        #################
        stats = Stats()

        # Create objects

        alert_mgr = AlertManager(config, False)

        if config.data_handler.type == DataHandlerType.FIXED:
            data_handler = FixedDataHandler(config)
            logger.info('Symbols tracked: ' + str(data_handler.symbol_list))

        else:
            data_handler = ScreenerDataHandler(config.general.market,
                                               config.backtest.frequency,
                                               config.backtest.sampling,
                                               file_processor.files_data['screener_data'], config, alert_mgr)

        events = queue.Queue()
        pending_orders = queue.Queue()
        deactivated_symbols = queue.Queue()

        mac_strategy = MovingAverageCrossStrategy(data_handler.symbol_list, events, config, strategy_id='mac')
        bol_strategy = BollingerStrategy(data_handler.symbol_list, events, config, strategy_id='bol')
        bah_strategy = BuyAndHoldStrategy(data_handler.symbol_list, events, config, strategy_id='bah')
        car_strategy = CarvasBoxStrategy(data_handler.symbol_list, deactivated_symbols, events, config,
                                         alert_mgr, strategy_id='car')

        strategy_objects = [mac_strategy, bol_strategy, bah_strategy, car_strategy]
        active_strategies = []
        strategies_list = []
        for strategy in strategy_objects:
            if strategy.status:
                active_strategies.append(strategy)
                strategies_list.append(strategy.strategy_id)

        logger.info('Active strategies: ' + str(strategies_list))

        ppv = PPV(config, data_handler)
        risk_manager = RiskManager(events, data_handler.symbol_list, active_strategies, config, data_handler)
        portfolio = Portfolio(config, events, data_handler.symbol_list, strategies_list, config.backtest.start_date,
                              data_handler,
                              risk_manager, config.portfolio.initial_capital, mode=EngineMode.BACKTEST)
        execution_handler = SimulatedExecutionHandler(pending_orders, config.portfolio)
        data_processor = DataProcessor()
        session_mgr = SessionManager(config, session_id, output_path, data_handler, portfolio, active_strategies,
                                     deactivated_symbols, pending_orders, config.backtest.start_date)
        metrics_mgr = MetricsManager(session_id, config.mysqlconf, config.general.continue_session,
                                     config.general.monitoring, self.reset_metrics, portfolio)

        file_processor.write_headers(config)
        car_strategy.print_debug_header()

        data_handler.create_dataframes()

        # ppv.process()

        logger.info('Backtest started')

        current_date = config.backtest.start_date

        is_24_hours_market = True if (config.general.market == Market.FX or
                                      config.general.market == Market.CC) else False

        while current_date <= config.backtest.end_date:

            if not is_24_hours_market:
                if current_date.weekday() == 5 or current_date.weekday() == 6:
                    current_date += dt.timedelta(minutes=sampling_minutes)
                    continue

                if config.backtest.frequency == Frequency.INTRADAY:
                    open_market = MarketCalendar.MARKET_SCHEDULE[config.general.market.value]['Open']
                    close_market = MarketCalendar.MARKET_SCHEDULE[config.general.market.value]['Close']

                    if current_date.time() < open_market or current_date.time() > close_market:
                        current_date += dt.timedelta(minutes=sampling_minutes)
                        continue

            if data_handler.type is DataHandlerType.SCREENER:
                data_handler.update_symbol_list(current_date)

            event_driven_process(config, current_date, deactivated_symbols, pending_orders, events, portfolio,
                                 data_handler, ppv,
                                 risk_manager, stats, data_processor, execution_handler, file_processor,
                                 active_strategies, alert_mgr, session_mgr, metrics_mgr)

            if data_handler.type is DataHandlerType.SCREENER:
                data_handler.remove_symbols(deactivated_symbols, portfolio, strategies_list)

            current_date += dt.timedelta(minutes=sampling_minutes)

        session_mgr.save_session_data()

        logger.info("Backtest finished")

        statistics_manager = StatisticsManager(file_processor.session_id, self.output_path,
                                               file_processor.get_equity_data(),
                                               portfolio.orders_data.copy(), None)
        statistics_manager.create_equity_curve_dataframe(portfolio.all_holdings, strategies_list)
        msg = statistics_manager.output_summary_stats()
        logger.info(msg)

        logger.info('Signals: ' + str(stats.signals))
        logger.info("Orders: %s" % stats.orders)
        logger.info("Fills: %s" % stats.fills)

        logger.info('Signals long: ' + str(stats.signals_long))
        logger.info('Signals short: ' + str(stats.signals_short))
        logger.info('Signals exit: ' + str(stats.signals_exit))

        statistics_manager.generate_trading_plots()
        statistics_manager.generate_trading_report()
        statistics_manager.generate_trade_statistics()
