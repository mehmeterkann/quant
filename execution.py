from borsa import FillEvent
class ExecutionHandler:
    def __init__(self,events,data_handler):
        self.events = events
        self.data_handler = data_handler


    def execute_order(self,event):
        if event.type != "ORDER":
            return

        bar = self.data_handler.get_latest_bar()

        fill_price = bar["close"]
        commission = max(1.0, event.quantity * 0.005)

        fill_event = FillEvent(
            timestamp=bar["timestamp"],
            symbol=event.symbol,
            direction=event.direction,
            quantity=event.quantity,
            fill_price=fill_price,
            commission=commission
        )
        self.events.put(fill_event)