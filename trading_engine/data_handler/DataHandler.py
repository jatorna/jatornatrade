from abc import ABCMeta, abstractmethod


class DataHandler(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def create_dataframes(self):
        raise NotImplementedError("Should implement create_dataframes()")

    @abstractmethod
    def has_current_price(self, symbol, current_date):
        raise NotImplementedError("Should implement has_current_price()")

    @abstractmethod
    def get_current_tick(self, symbol, current_date, price_type):
        raise NotImplementedError("Should implement get_current_tick()")

    @abstractmethod
    def get_last_price(self, symbol, current_date):
        raise NotImplementedError("Should implement get_last_price()")

    @abstractmethod
    def get_current_data(self, symbol, start_date, current_date):
        raise NotImplementedError("Should implement get_current_data()")

    @abstractmethod
    def valid_close_price(self, symbol, current_date):
        raise NotImplementedError("Should implement valid_close_price()")