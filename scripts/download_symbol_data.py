from subprojects.StockDataWrappers import *

symbols = ['AAPL', 'META', 'AMZN', 'MSFT', 'NFLX']
output = 'outputpath'

for s in symbols:
    data = download_from_yahoo(s, Frequency.DAILY, Market.US)
    data.to_csv(output + '/' + s + '.csv',
                sep='\t', float_format='%.4f', mode='w', header=True, date_format='%Y-%m-%d')
