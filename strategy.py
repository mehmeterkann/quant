import queue
from borsa import SignalEvent


class Strategy:
    def __init__(self,data_handler,events):
        self.data_handler = data_handler
        self.events = events

    def calculate_signals(self,event):
        pass

                

class MovingAverageCrossStrategy(Strategy):
    def __init__(self, data_handler, events,trend_window,fast_window,allow_short=False):
        super().__init__(data_handler, events)
        self.bought = False
        self.trend_window = trend_window
        self.fast_window = fast_window
        self.position_state = 0
        self.allow_short=allow_short

    def calculate_signals(self, event):
        bars=self.data_handler.get_latest_bars(self.trend_window)
        if event.type=="MARKET":
            if len(bars) < self.trend_window:
                return
            
            closes = [b["close"] for b in bars]
            sma_200 = sum(closes[-200:])/200
            highs = [b["high"] for b in bars]
            highest_20 = max(highs[-21:-1])
            lows = [b["low"] for b in bars]
            lowest_10 = min(lows[-11:-1])
            lowest_20 = min(lows[-21:-1])
            highest_5 = max(highs[-6:-1])
            if self.position_state ==0:
                if event.close > sma_200 and event.close >highest_20:
                    signal = SignalEvent(timestamp=event.timestamp,symbol=event.symbol,signal_type="LONG",strength=1.0)
                    self.events.put(signal)
                    self.position_state = 1
                elif self.allow_short and event.close < lowest_20 and event.close<sma_200:
                    signal = SignalEvent(timestamp=event.timestamp,symbol=event.symbol,signal_type="SHORT",strength=1.0)
                    self.events.put(signal)
                    self.position_state =-1
            else:
                if self.position_state ==1 and event.close <lowest_10:
                    signal = SignalEvent(timestamp=event.timestamp,symbol=event.symbol,signal_type="EXIT",strength=1.0)
                    self.events.put(signal)
                    self.position_state = 0
                elif self.position_state == -1 and  event.close> highest_5:
                    signal = SignalEvent(timestamp=event.timestamp,symbol=event.symbol,signal_type="EXIT",strength=1.0)
                    self.events.put(signal)
                    self.position_state = 0                    

           
            
