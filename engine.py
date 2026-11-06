from borsa import MarketEvent,SignalEvent,OrderEvent,FillEvent
import queue
class BacktestEngine:
    def __init__(self,events,data_handler,strategy,portfolio,execution_handler):
        self.events=events
        self.data=data_handler
        self.strategy = strategy
        self.portfolio=portfolio
        self.execution_handler=execution_handler

    def run(self):
        while self.data.continue_backtest:
            self.data.update_bars()
            while not self.events.empty():
                event = self.events.get()

                if event.type == "MARKET":
                    self.strategy.calculate_signals(event)
                    self.portfolio.update_market(event)
                elif event.type == "SIGNAL":
                    self.portfolio.update_signal(event)
                elif event.type == "ORDER":
                    self.execution_handler.execute_order(event)
                elif event.type == "FILL":
                    self.portfolio.update_fill(event)
        if self.portfolio.stock_size != 0:
            latest_bar = self.data.get_latest_bar()
            if latest_bar:
                signal = SignalEvent(timestamp=latest_bar["timestamp"],
                                     symbol=latest_bar["symbol"] if "symbol" in latest_bar else "QQQ",
                                     signal_type="EXIT",
                                     strength=1.0)
                self.events.put(signal)

                while not self.events.empty():
                    event = self.events.get()
                    if event.type == "SIGNAL":
                        self.portfolio.update_signal(event)
                    elif event.type == "ORDER":
                        self.execution_handler.execute_order(event)
                    elif event.type == "FILL":
                        self.portfolio.update_fill(event)
                        
        
