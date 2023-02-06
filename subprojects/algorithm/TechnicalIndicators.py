import numpy as np


def bollinger_bands(values, window, n_std):
    mean = np.mean(values[-window:])
    standard_deviation = np.std(values[-window:])
    down = mean - n_std * standard_deviation
    up = mean + n_std * standard_deviation
    return up, down, mean


def moving_average_con_div(values, short_window, long_window):
    short_sma = np.mean(values[-short_window:])
    long_sma = np.mean(values[-long_window:])
    return short_sma, long_sma
