class Event:

    def __init__(self,type):

        self.type = type

       

   



class MarketEvent(Event):

    def __init__(self,timestamp,symbol,open,high,low,close,volume,true_range):

        super().__init__("MARKET")

        self.timestamp=timestamp

        self.symbol=symbol

        self.open=open

        self.high=high

        self.low=low

        self.close = close

        self.volume = volume

        self.true_range = true_range





class SignalEvent(Event):

    def __init__(self,timestamp,symbol,signal_type,strength):

        super().__init__("SIGNAL")

        self.timestamp = timestamp

        self.symbol = symbol

        self.signal_type = signal_type

        self.strength = strength



class OrderEvent(Event):

    def __init__(self,symbol,order_type,direction,quantity):

        super().__init__("ORDER")

        self.symbol = symbol

        self.order_type=order_type

        self.direction=direction

        self.quantity=quantity



class FillEvent(Event):

    def __init__(self,timestamp,symbol,direction,quantity,fill_price,commission):

        super().__init__("FILL")

        self.timestamp = timestamp

        self.symbol = symbol

        self.direction = direction

        self.quantity = quantity

        self.fill_price=fill_price

        self.commission= commission

