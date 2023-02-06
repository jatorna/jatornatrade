import subprojects.misc.LowLevelFuncions as llw
from enum import Enum

logger = llw.script_logger('EVENT')


class EventType(Enum):
    MARKET = 'MARKET'
    SIGNAL = 'SIGNAL'
    ORDER = 'ORDER'
    FILL = 'FILL'


class Event(object):
    """
    Event is base class providing an interface for all subsequent 
    (inherited) events, that will trigger further events in the 
    trading infrastructure.   
    """
    pass


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with 
    corresponding bars.
    """

    def __init__(self):
        """
        Initialises the MarketEvent.
        """
        self.type = EventType.MARKET


class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """
    
    def __init__(self, signal_id, signal_type, symbol, datetime, action, strength):
        """
        Initialises the SignalEvent.

        Parameters:
        strategy_id - The unique ID of the strategy sending the signal.
        symbol - The ticker symbol, e.g. 'GOOG'.
        datetime - The timestamp at which the signal was generated.
        signal_type - MKT or S/L or T/P
        action - 'LONG',  'SHORT' otr 'EXIT'.
        strength - An adjustment factor "suggestion" used to scale 
            quantity at the portfolio level. Useful for pairs strategies.
        """
        self.type = EventType.SIGNAL
        self.strategy_id = signal_id
        self.signal_type = signal_type
        self.symbol = symbol
        self.datetime = datetime
        self.action = action
        self.strength = strength


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """

    def __init__(self, symbol, order_id, order_type, quantity, price, action, direction, strength):
        """
        Initialises the order type, setting whether it is
        a Market order ('MKT') or Limit order ('LMT'), has
        a quantity (integral) and its direction ('BUY' or
        'SELL').

        Parameters:
        symbol - The instrument to trade.
        strategy_id - The unique ID of the strategy sending the order.
        order_type - 'MKT' or 'LMT' for Market or Limits.
        quantity - Market quantity.
        signal_direction - The direction of signal ('LONG', 'SHORT' or 'EXIT')
        direction - 'BUY' or 'SELL' .
        """
        self.type = EventType.ORDER
        self.symbol = symbol
        self.order_id = order_id
        self.order_type = order_type
        self.quantity = self._check_set_quantity_positive(quantity)
        self.price = price
        self.action = action
        self.direction = direction
        self.strength = strength

    def _check_set_quantity_positive(self, quantity):
        """
        Checks that quantity is a positive integer.
        """
#        if not isinstance(quantity, int) or quantity <= 0:
        if quantity <= 0:
            raise ValueError("Order event quantity is not a positive number")
        return quantity

    def print_order(self):
        """
        Outputs the values within the Order.
        """
        logger.info(
            "Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" % 
            (self.symbol, self.order_type, self.quantity, self.direction)
        )


class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(self, timeindex, symbol, order_id, exchange, order_type, strength, quantity,
                 action, direction, order_price):
        """
        Initialises the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional 
        commission.

        If commission is not provided, the Fill object will
        calculate it based on the trade size and Interactive
        Brokers fees.

        Parameters:
        timeindex - The bar-resolution when the order was filled.
        symbol - The instrument which was filled.
        strategy_id - The unique ID of the strategy sending the fill.
        exchange - The exchange where the order was filled.
        quantity - The filled quantity in market quantity.
        action - The direction of signal ('LONG', 'SHORT' or 'EXIT')
        direction - The direction of fill ('BUY' or 'SELL')
        price - The price value when the order is filled.
        commission - An optional commission sent from IB.
        """
        self.type = EventType.FILL
        self.order_timeindex = timeindex
        self.symbol = symbol
        self.order_id = order_id
        self.exchange = exchange
        self.fill_type = order_type
        self.strength = strength
        self.quantity = quantity
        self.action = action
        self.direction = direction
        self.order_price = order_price
        self.filled = False
        self.timeindex = ''
        self.price = 0
        self.commission = 0