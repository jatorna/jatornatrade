import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as plt_dates
import subprojects.misc.LowLevelFuncions as llw
from subprojects.types.Common import *
import quantstats as qs
import pandas as pd
import numpy as np
import copy
matplotlib.use('Agg')


logger = llw.script_logger('STATS MGR')


######################
# MONITOR
######################

class StatisticsManager:
    def __init__(self, session_id, trade_path, equity_data, orders_data, equity_data_benchmark):
        self.session_id = session_id
        self.trade_path = trade_path
        self.equity_data = equity_data
        self.orders_data = orders_data
        self.equity_data_benchmark = equity_data_benchmark
        self.trades_data = self.orders_data_analysis()

    def generate_trading_plots(self):
        logger.info('Starting Backtest Data Plotting')
        logger.debug('Figures to be saved in %s' % self.trade_path)

        # READING DATA

        date_list = self.equity_data['Date'].values
        equity_list = self.equity_data['Equity'].values
        returns_list = pd.to_numeric(self.equity_data['Returns'].values)
        drawndown_list = self.equity_data['Drawndown'].values

        logger.info('Plotting equity chart')
        plot_formatter = plt_dates.DateFormatter('%d/%m\n%Y')
        fig_header = self.trade_path

        fig_gss = fig_header + '/backtest_stats.png'

        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, sharex=True, sharey=False, figsize=(20, 12), dpi=300,
                                            facecolor='w')

        ax1.xaxis.set_major_formatter(plot_formatter)
        ax1.autoscale(enable=True, axis='x', tight=True)
        ax1.minorticks_on()
        ax1.grid(which='major', color='silver', linestyle='--', linewidth=1, zorder=1)
        ax1.grid(which='minor', color='silver', linestyle=':', linewidth=0.5, zorder=1)
        ax1.plot(date_list, equity_list, linestyle='-', linewidth=3, color='blue')
        ax1.set_title('Backtest Stats', fontsize=20)
        ax1.set_ylabel('Equity', fontsize=16)
        ax1.tick_params(axis='both', labelsize=12)

        ax2.xaxis.set_major_formatter(plot_formatter)
        ax2.autoscale(enable=True, axis='x', tight=True)
        ax2.minorticks_on()
        ax2.grid(which='major', color='silver', linestyle='--', linewidth=1, zorder=1)
        ax2.grid(which='minor', color='silver', linestyle=':', linewidth=0.5, zorder=1)
        ax2.plot(date_list, returns_list, linestyle='-', linewidth=3, color='black')
        ax2.set_ylabel('Returns', fontsize=16)
        ax2.tick_params(axis='both', labelsize=12)

        ax3.xaxis.set_major_formatter(plot_formatter)
        ax3.autoscale(enable=True, axis='x', tight=True)
        ax3.autoscale(enable=True, axis='y', tight=True)
        ax3.minorticks_on()
        ax3.grid(which='major', color='silver', linestyle='--', linewidth=1, zorder=1)
        ax3.grid(which='minor', color='silver', linestyle=':', linewidth=0.5, zorder=1)
        ax3.plot(date_list, drawndown_list, linestyle='-', linewidth=3, color='red')
        ax3.set_ylabel('Drawdown', fontsize=16)
        ax3.tick_params(axis='y', labelsize=12)
        ax3.tick_params(axis='x', labelsize=16)
        plt.tight_layout()
        fig.savefig(fig_gss)

        plt.close(fig)

    def generate_trading_report(self):
        logger.info('Starting Backtest Data Report Generator')
        logger.debug('Reports to be saved in %s' % self.trade_path)

        qs.extend_pandas()

        ts = pd.Series(self.equity_data['Total'].values, index=self.equity_data['Date'])

        if self.equity_data_benchmark is not None:
            ts_benchmark = pd.Series(self.equity_data_benchmark['Total'].values,
                                     index=self.equity_data_benchmark['Date'])
            qs.reports.html(ts, benchmark=ts_benchmark, output=self.trade_path + '/backtest_report.html')

        else:
            qs.reports.html(ts, output=self.trade_path + '/backtest_report.html')

    def orders_data_analysis(self):
        trades_data = pd.DataFrame(columns=['Position_ID', 'Symbol', 'Open_dt', 'Open_dir', 'Open_price',
                                            'Open_quant', 'Open_commission', 'Close_dt', 'Close_price',
                                            'Close_quant', 'Close_commission'])
        for order in self.orders_data['Order_ID'].unique():
            order_df = self.orders_data[self.orders_data['Order_ID'] == order]
            try:
                try:
                    trades_data.loc[len(trades_data)] = [order, order_df['Symbol'].values[0],
                                                         order_df['Date'].values[0], order_df['Action'].values[0],
                                                         order_df['Price'].values[0],
                                                         order_df['Quantity'].values[0],
                                                         order_df['Commission'].values[0],
                                                         order_df['Date'].values[1],
                                                         order_df['Price'].values[1],
                                                         order_df['Quantity'].values[1],
                                                         order_df['Commission'].values[1]]
                except:
                    trades_data.loc[len(trades_data)] = [order, order_df['Symbol'].values[0],
                                                         order_df['Date'].values[0], order_df['Action'].values[0],
                                                         order_df['Price'].values[0],
                                                         order_df['Quantity'].values[0],
                                                         order_df['Commission'].values[0], None,
                                                         None, None, None]
            except:
                pass

        trades_data['Open_price'] = pd.to_numeric(trades_data['Open_price'])
        trades_data['Open_quant'] = pd.to_numeric(trades_data['Open_quant'])
        trades_data['Open_commission'] = pd.to_numeric(trades_data['Open_commission'])
        trades_data['Close_price'] = pd.to_numeric(trades_data['Close_price'])
        trades_data['Close_quant'] = pd.to_numeric(trades_data['Close_quant'])
        trades_data['Close_commission'] = pd.to_numeric(trades_data['Close_commission'])

        # trades_data = trades_data.dropna()
        trade_profit_list = []
        trade_profit_per_list = []
        strategy_list = []

        for i in range(len(trades_data)):
            if trades_data['Open_dir'].values[i] == OrderType.LONG.value:
                profit = (trades_data['Close_price'].values[i] * trades_data['Close_quant'].values[i]) - \
                         (trades_data['Open_price'].values[i] * trades_data['Open_quant'].values[i] ) - \
                trades_data['Open_commission'].values[i] - trades_data['Close_commission'].values[i]

                trade_profit_list.append(profit)
                trade_profit_per_list.append(profit / (trades_data['Open_price'].values[i] *
                                                       trades_data['Open_quant'].values[i]))

            elif trades_data['Open_dir'].values[i] == OrderType.SHORT.value:
                profit = - (trades_data['Close_price'].values[i] * trades_data['Close_quant'].values[i]) + \
                         (trades_data['Open_price'].values[i] * trades_data['Open_quant'].values[i]) - \
                         trades_data['Open_commission'].values[i] - trades_data['Close_commission'].values[i]

                trade_profit_list.append(profit)
                trade_profit_per_list.append(profit / (trades_data['Open_price'].values[i] *
                                                       trades_data['Open_quant'].values[i]))

            strategy_list.append(trades_data['Position_ID'].values[i][0:3])

        trades_data['Strategy'] = strategy_list
        trades_data['Profit'] = trade_profit_list
        trades_data['%Profit'] = trade_profit_per_list

        return trades_data

    def create_equity_curve_dataframe(self, all_holdings, strategy_list):

        all_holdings = copy.deepcopy(all_holdings)
        i = 0
        for hold in all_holdings:
            for strategy in strategy_list:
                all_holdings[i][strategy] = hold[strategy][1]
            i += 1
        curve = pd.DataFrame(all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0 + curve['returns']).cumprod()
        self.equity_curve = curve

    @staticmethod
    def create_sharpe_ratio(returns, periods=252):

        return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)

    @staticmethod
    def create_drawdowns(pnl):

        # Calculate the cumulative returns curve
        # and set up the High Water Mark
        hwm = [0]

        # Create the drawdown and duration series
        idx = pnl.index
        drawdown = pd.Series(index=idx)
        duration = pd.Series(index=idx)

        # Loop over the index range
        for t in range(1, len(idx)):
            hwm.append(max(hwm[t - 1], pnl[t]))
            drawdown[t] = (hwm[t] - pnl[t])
            duration[t] = (0 if drawdown[t] == 0 else duration[t - 1] + 1)
        return drawdown, drawdown.max(), duration.max()

    def output_summary_stats(self):

        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = self.create_sharpe_ratio(returns)
        drawdown, max_dd, dd_duration = self.create_drawdowns(pnl)
        self.equity_curve['drawdown'] = drawdown

        orders_closed = len(self.trades_data.dropna())
        if orders_closed < 1:
            win_rate = 0
            win_average = 0
            lost_average = 0
            expected_value = 0
        else:
            win_rate = len(self.trades_data[self.trades_data['Profit'] > 0]) / orders_closed
            win_average = np.mean(self.trades_data[self.trades_data['Profit'] > 0]['Profit'])
            lost_average = np.mean(self.trades_data[self.trades_data['Profit'] < 0]['Profit'])
            expected_value = win_rate * win_average + lost_average * (1-win_rate)

        stats = "Statistics %s:\n" % self.session_id

        stats += "Total Return:      %7.2f%%\n" \
                 "Sharpe Ratio:      %7.2f\n" \
                 "Max Drawdown:      %7.2f%%\n" \
                 "Drawdown Duration: %7d\n" \
                 % ((total_return - 1.0) * 100.0, sharpe_ratio, (max_dd * 100.0), dd_duration)
        stats += "Trades win:        %7.2f%%\n" % (win_rate * 100.0)
        stats += "Average win:       %7.2f\n" % win_average
        stats += "Average lost:      %7.2f\n" % lost_average
        stats += "Expected value:    %7.2f\n" % expected_value

        return stats

    def generate_trade_statistics(self):
        logger.info('Starting Backtest Data Trade Statistics')
        logger.debug('Statistics to be saved in %s' % self.trade_path)

        self.trades_data.to_csv(self.trade_path+'/trade_data.csv')
