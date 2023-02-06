from trading_engine.Event import MarketEvent
from trading_engine.Event import EventType
import subprojects.misc.LowLevelFuncions as llw
from subprojects.types.Common import *
import queue
import random
import copy

logger = llw.script_logger('EVENT-DRIVEN MGR')


def event_driven_process(config, current_date, deactivated_symbols, pending_orders, events, portfolio, data_handler, ppv, risk_manager,
                         stats, data_processor, execution_handler, file_processor, active_strategies, alert_manager,
                         session_mgr, metrics_mgr):
    while True:
        try:
            fill = pending_orders.get(False)
        except queue.Empty:
            break
        else:
            if fill is not None:
                portfolio.confirm_fill_order(current_date, active_strategies, fill)

    events.put(MarketEvent())
    msg = ""
    while True:
        try:
            event = events.get(False)
        except queue.Empty:
            break
        else:
            if event is not None:
                if event.type == EventType.FILL:
                    if event.filled:
                        stats.fills += 1
                        event.commission = portfolio.calculate_commission(event.quantity, event.price)
                        portfolio.update_fill(event)
                        portfolio.update_orders_data(event, current_date)
                        data_processor.write_sequential_order_output(portfolio.orders_data)
                        if event.action == OrderType.EXIT:
                            data_processor.write_sequential_close_positions_output(portfolio.orders_data)
                    else:
                        pending_orders.put(event)

                elif event.type == EventType.MARKET:

                    portfolio.update_portfolio(current_date)

                    if config.risk_manager.limit_orders:
                        risk_manager.update_price_limits(current_date, portfolio)

                    session_mgr.calculate_exit_signals(events, current_date)

                    for strategy in active_strategies:
                        strategy.calculate_signals(event, data_handler, current_date, portfolio.orders_data, ppv)

                    if config.risk_manager.limit_orders:
                        risk_manager.calculate_limit_signals(current_date,
                                                             portfolio.current_positions)

                elif event.type == EventType.SIGNAL:

                    if random.randint(1, 100) <= config.portfolio.signal_rate or event.action == OrderType('EXIT'):
                        risk_manager.update_signal(event, current_date, portfolio)

                        stats.signals += 1
                        if event.action == OrderType.LONG:
                            stats.signals_long += 1
                        if event.action == OrderType.SHORT:
                            stats.signals_short += 1
                        if event.action == OrderType.EXIT:
                            stats.signals_exit += 1

                elif event.type == EventType.ORDER:
                    stats.orders += 1
                    execution_handler.execute_order(event, current_date, active_strategies, deactivated_symbols)
                    msg += '\nSessionID: ' + file_processor.session_id + '\nOrder filled ' + \
                           current_date.strftime('%Y/%m/%d %H:%M:%S') + '\n' + event.symbol + ' ' +\
                           event.action.value + ' ' + str(event.price) + '\n' + 'Strength: ' + str(event.strength) + \
                           '\nQuantity: ' + str(event.quantity) +\
                           '\nID: ' + event.order_id + '\n\n'

    alert_manager.send_telegram_alert(msg)

    if 'curpositi' in config.core:
        data_processor.write_sequential_current_positions_output(current_date, data_handler, portfolio)

    portfolio.close_positions_data += copy.copy(data_processor.data_output.positions_output.close_data)
    portfolio.current_positions_data = copy.copy(data_processor.data_output.positions_output.current_data)

    data_processor.write_sequential_equity_output(portfolio.all_holdings, portfolio.initial_capital)
    if config.data_handler.type == DataHandlerType.SCREENER:
        data_processor.write_screener_data(current_date, data_handler.get_screener_data())

    if metrics_mgr.enabled:
        metrics_mgr.insert_data_to_db(current_date, data_processor.data_output)

    file_processor.write_sequential_data(data_processor.data_output)

    data_processor.clear_sequential_output()
