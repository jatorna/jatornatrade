import queue
import datetime as dt
import sys
from trading_engine.strategies.Mac import MovingAverageCrossStrategy
from trading_engine.strategies.Bol import BollingerStrategy
from trading_engine.strategies.Bah import BuyAndHoldStrategy
from trading_engine.strategies.Car import CarvasBoxStrategy
from trading_engine.Portfolio import Portfolio
from trading_engine.Execution import SimulatedExecutionHandler
from trading_engine.data_handler.FixedDataHandler import FixedDataHandler
from trading_engine.data_handler.ScreenerDataHandler import ScreenerDataHandler
from trading_engine.PPV import PPV
from trading_engine.DataProcessor import DataProcessor
from trading_engine.RiskManager import RiskManager
from trading_engine.SessionManager import SessionManager
from trading_engine.EventDrivenManager import event_driven_process
from trading_engine.MetricsManager import MetricsManager
from subprojects.resources.Constants import MarketCalendar
from subprojects.misc.LowLevelFuncions import next_monday_9am
from subprojects.misc.LowLevelFuncions import next_monday
from subprojects.CommManager import CommManager
from subprojects.types.Stats import Stats
from subprojects.AlertManager import AlertManager
from subprojects.StatisticsManager import StatisticsManager
import subprojects.misc.LowLevelFuncions as llw
from subprojects.types.Common import *
import time

logger = llw.script_logger('TE REALTIME')


class TradingEngineRT:

    def __init__(self, config, output_path, file_processor, reset_metrics):
        self.config = config
        self.output_path = output_path
        self.file_processor = file_processor
        self.reset_metrics = reset_metrics

    def run_trading_engine(self):

        # Initialize objects

        config = self.config
        file_processor = self.file_processor
        session_id = file_processor.session_id

        open_market = MarketCalendar.MARKET_SCHEDULE[config.general.market.value]['Open']
        close_market = MarketCalendar.MARKET_SCHEDULE[config.general.market.value]['Close']

        logger.info('Launching trading engine')
        logger.info('Session ID: ' + file_processor.session_id)
        logger.info('Processing main configuration')
        logger.info('Data Handler mode: ' + config.data_handler.type.value)
        logger.info('Frequency mode: ' + config.realtime.frequency.value)
        logger.info('PPV - ' + 'Interpolate: ' + str(config.ppv.interpolate) + ', Smoothing: ' +
                    str(config.ppv.smoothing))
        logger.info('Monitoring: ' + str(config.general.monitoring))
        logger.info('Alerts: ' + str(config.general.tgm_alerts))

        if config.realtime.frequency == Frequency.INTRADAY:
            sampling_minutes = config.realtime.sampling
            logger.info('Sampling epochs [min]: ' + str(sampling_minutes))

        #################
        # INITIAL STATS #
        #################

        stats = Stats()

        symbol_list = config.symbol_list

        # Create objects

        alert_mgr = AlertManager(config, False)

        if config.data_handler.type == DataHandlerType.FIXED:
            data_handler = FixedDataHandler(config.symbol_list,
                                            config.general.market,
                                            config.backtest.frequency,
                                            config.backtest.sampling,
                                            config.mysqlconf)
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
        car_strategy = CarvasBoxStrategy(data_handler.symbol_list, deactivated_symbols, events, config, alert_mgr,
                                         strategy_id='car')

        strategies_objects = [mac_strategy, bol_strategy, bah_strategy, car_strategy]
        active_strategies = []
        strategies_list = []
        for strategy in strategies_objects:
            if strategy.status:
                active_strategies.append(strategy)
                strategies_list.append(strategy.strategy_id)

        logger.info('Active strategies: ' + str(strategies_list))

        ppv = PPV(config, data_handler)
        risk_manager = RiskManager(events, data_handler.symbol_list, active_strategies, config, data_handler)
        portfolio = Portfolio(config, events, data_handler.symbol_list, strategies_list, config.backtest.start_date,
                              data_handler,
                              risk_manager, config.portfolio.initial_capital, mode=EngineMode.REALTIME)
        execution_handler = SimulatedExecutionHandler(pending_orders, config.portfolio)
        data_processor = DataProcessor()
        session_mgr = SessionManager(config, session_id, self.output_path, data_handler, portfolio, active_strategies,
                                     deactivated_symbols, pending_orders, dt.datetime.now())
        metrics_mgr = MetricsManager(session_id, config.mysqlconf, config.general.continue_session,
                                     config.general.monitoring, self.reset_metrics, portfolio)

        file_processor.write_headers(config)
        car_strategy.print_debug_header()

        data_handler.create_dataframes()
        # ppv.process()

        if config.realtime.frequency == Frequency.INTRADAY:
            comm_mgr = CommManager(config.realtime)
            comm_mgr.connect_with_server()
            if not comm_mgr.client_connected:
                logger.error('Error with data server connection. Program aborted')
                sys.exit()

        logger.info('Trading Engine started')

        is_24_hours_market = config.general.market == Market.CC or config.general.market == Market.FX

        try:
            while True:
                if config.realtime.frequency == Frequency.INTRADAY:
                    week_day = dt.datetime.now().weekday()
                    if week_day == 5 or week_day == 6 or dt.datetime.now().time() > close_market and \
                            not is_24_hours_market:
                        logger.info('Market closed')
                        if week_day == 4 or week_day == 5 or week_day == 6:
                            next_trade_date = next_monday_9am()
                        else:
                            next_trade_date = dt.datetime(dt.datetime.now().year, dt.datetime.now().month,
                                                          dt.datetime.now().day,
                                                          open_market.hour, open_market.minute,
                                                          open_market.second) + dt.timedelta(days=1)

                        logger.info('Trade will start at: ' + next_trade_date.strftime('%Y-%m-%d %H:%M:%S'))
                        time.sleep((next_trade_date - dt.datetime.now()).total_seconds() - 300)

                        # Reload symbol data
                        metrics_mgr.reset_mysql_connection()
                        data_handler.reset_mysql_connection(config.mysqlconf)
                        data_handler.create_dataframes()
                        # ppv.process()

                    elif dt.datetime.now().time() < open_market and not is_24_hours_market:
                        logger.info('Market closed')
                        next_trade_date = dt.datetime(dt.datetime.now().year, dt.datetime.now().month,
                                                      dt.datetime.now().day,
                                                      open_market.hour, open_market.minute,
                                                      open_market.second)
                        logger.info('Trade will start at: ' + next_trade_date.strftime('%Y-%m-%d %H:%M:%S'))
                        time.sleep((next_trade_date - dt.datetime.now()).total_seconds() - 300)

                        # Reload symbol data
                        metrics_mgr.reset_mysql_connection()
                        data_handler.reset_mysql_connection(config.mysqlconf)
                        data_handler.create_dataframes()
                        # ppv.process()

                    else:
                        next_trade_date = dt.datetime(dt.datetime.now().year, dt.datetime.now().month,
                                                      dt.datetime.now().day,
                                                      dt.datetime.now().hour, dt.datetime.now().minute) + dt.timedelta(
                            seconds=60)
                        logger.info('Trade will start at: ' + next_trade_date.strftime('%Y-%m-%d %H:%M:%S'))

                if config.realtime.frequency == Frequency.DAILY:
                    week_day = dt.datetime.now().weekday()
                    if week_day == 5 or week_day == 6 or dt.datetime.now().time() > config.realtime.daily_exec_time:
                        if week_day == 4 or week_day == 5 or week_day == 6:
                            next_trade_date = next_monday() + dt.timedelta(hours=config.realtime.daily_exec_time.hour,
                                                                           minutes=config.realtime.daily_exec_time.
                                                                           minute, seconds=config.realtime.
                                                                           daily_exec_time.second)
                        else:
                            next_trade_date = dt.datetime(dt.datetime.now().year, dt.datetime.now().month,
                                                          dt.datetime.now().day,
                                                          config.realtime.daily_exec_time.hour,
                                                          config.realtime.daily_exec_time.minute,
                                                          config.realtime.daily_exec_time.second) + dt.timedelta(days=1)

                        logger.info('Next trade will be at: ' + next_trade_date.strftime('%Y-%m-%d %H:%M:%S'))
                        time.sleep((next_trade_date - dt.datetime.now()).total_seconds())

                        # # Reload symbol data

                        if data_handler.type is DataHandlerType.SCREENER:
                            # Empty epoch is passed, is realtime screener update
                            data_handler.update_symbol_list(dt.datetime(dt.datetime.now().year, dt.datetime.now().month,
                                                                        dt.datetime.now().day))

                        metrics_mgr.reset_mysql_connection()

                        if config.data_handler.type == DataHandlerType.FIXED:
                            data_handler.reset_mysql_connection(config.mysqlconf)

                        data_handler.create_dataframes()
                        # ppv.process()

                    else:
                        next_trade_date = dt.datetime(dt.datetime.now().year, dt.datetime.now().month,
                                                      dt.datetime.now().day,
                                                      config.realtime.daily_exec_time.hour,
                                                      config.realtime.daily_exec_time.minute,
                                                      config.realtime.daily_exec_time.second)
                        logger.info('Next trade will be at: ' + next_trade_date.strftime('%Y-%m-%d %H:%M:%S'))
                        time.sleep((next_trade_date - dt.datetime.now()).total_seconds())

                        # Reload symbol data

                        if data_handler.type is DataHandlerType.SCREENER:
                            # Empty epoch is passed, is realtime screener update
                            data_handler.update_symbol_list(dt.datetime(dt.datetime.now().year, dt.datetime.now().month,
                                                                        dt.datetime.now().day))

                        metrics_mgr.reset_mysql_connection()

                        if config.data_handler.type == DataHandlerType.FIXED:
                            data_handler.reset_mysql_connection(config.mysqlconf)

                        data_handler.create_dataframes()
                        # ppv.process()

                while close_market > dt.datetime.now().time() or is_24_hours_market or \
                        config.realtime.frequency == Frequency.DAILY:

                    if config.realtime.frequency == Frequency.INTRADAY:

                        try:
                            today_symbol_data = comm_mgr.recv_market_data_msg()
                        except:
                            logger.error('No message received in less than 120 seconds')
                            continue

                        if len(today_symbol_data) == 0:
                            logger.warning('No ticks received')
                            continue
                        try:
                            data_handler.update_dataframes(today_symbol_data)
                            # ppv.process()
                        except Exception as e:
                            logger.error(e)
                            logger.warning('Error updating symbol data')
                            continue

                        current_date = dt.datetime(dt.datetime.now().year, dt.datetime.now().month,
                                                   dt.datetime.now().day, dt.datetime.now().hour,
                                                   dt.datetime.now().minute)

                        if dt.datetime.now().minute % config.realtime.sampling != 0:
                            continue

                    if config.realtime.frequency == Frequency.DAILY:
                        current_date = dt.datetime(dt.datetime.now().year, dt.datetime.now().month,
                                                   dt.datetime.now().day)

                    if current_date == portfolio.all_holdings[-1]['datetime']:
                        logger.warning('Current date already processed.')

                        if config.realtime.frequency == Frequency.DAILY:
                            break
                        else:
                            continue

                    logger.info('Symbol list: ' + str(data_handler.symbol_list))

                    event_driven_process(config, current_date, deactivated_symbols, pending_orders, events, portfolio,
                                         data_handler, ppv,
                                         risk_manager, stats, data_processor, execution_handler, file_processor,
                                         active_strategies, alert_mgr, session_mgr, metrics_mgr)

                    if data_handler.type is DataHandlerType.SCREENER:
                        data_handler.remove_symbols(deactivated_symbols, portfolio, strategies_list)

                    session_mgr.save_session_data()

                    if (close_market < dt.datetime.now().time() and not is_24_hours_market) or \
                            config.realtime.frequency == Frequency.DAILY:
                        statistics_manager = StatisticsManager(file_processor.session_id, self.output_path, None,
                                                               portfolio.orders_data, None)
                        statistics_manager.create_equity_curve_dataframe(portfolio.all_holdings, strategies_list)
                        msg = statistics_manager.output_summary_stats()
                        logger.info(msg)
                        alert_mgr.send_telegram_alert(msg)

                        #TODO: Is a patch. Fix this important
                        if config.realtime.frequency == Frequency.DAILY:
                            time.sleep(60)

                        break

        finally:
            if config.realtime.frequency == Frequency.INTRADAY:
                logger.info('Closing socket')
                logger.info('Exiting')
                comm_mgr.sock.close()
