from borsa import OrderEvent,FillEvent

class Portfolio:
    def __init__(self,events,data_handler,initial_capital=100000.0):
        self.events=events
        self.data_handler=data_handler
        self.initial_capital=initial_capital
        self.current_cash=initial_capital
        self.stock_size = 0
        self.trades = []
        self.entry_price = 0.0
        self.entry_date = None
        self.is_exiting = False
        self.highest_price = 0.0
        self.is_stop_changed = False
        self.highest_equity = self.initial_capital
        self.lowest_equity = 9999999
        self.worst_dropout = 0.0
        self.entry_atr = 0.0
        self.position_type = None
        self.lowest_price = 99999999.0


    def update_signal(self,event):
        if event.type !="SIGNAL":
            return


        if event.signal_type == "LONG" and self.stock_size==0:
            latest_bar = self.data_handler.get_latest_bar()
            if not latest_bar or latest_bar["close"] <=0:
                return
            current_atr = self.data_handler.calc_atr(14)
            if current_atr>0:


                current_price = latest_bar["close"]
                equity = (self.stock_size*current_price)+self.current_cash

                if (self.current_cash/self.initial_capital)>1.05:
                    risked_amount = equity*0.015
                else:
                    risked_amount = equity*0.01 #buradan oranı değiştir

                risk_distance = 2*current_atr

                stock_quantity = min(int(risked_amount/risk_distance),int(self.current_cash/current_price))
                
                if stock_quantity<=0:
                    return
                order = OrderEvent(symbol=event.symbol,order_type="MKT",direction="BUY",quantity=stock_quantity)
                self.events.put(order)



            else:
                current_price = latest_bar["close"]
                allocation = self.current_cash*0.2
                qty = int(allocation/current_price)
                if qty <=0:
                    return
                
                order = OrderEvent(
                    symbol=event.symbol,
                    order_type="MKT",
                    direction="BUY",
                    quantity=qty
                )
                self.events.put(order)
        elif event.signal_type == "SHORT" and self.stock_size == 0:
            latest_bar = self.data_handler.get_latest_bar()
            if not latest_bar or latest_bar["close"] <=0:
                return
            current_atr = self.data_handler.calc_atr(14)
            if current_atr>0:



                current_price = latest_bar["close"]
                equity = (self.stock_size*current_price)+self.current_cash

                if (self.current_cash/self.initial_capital)>1.05:
                    risked_amount = equity*0.015
                else:
                    risked_amount = equity*0.01

                risk_distance = 2*current_atr

                stock_quantity = min(int(risked_amount/risk_distance),int(self.current_cash/current_price))
                
                if stock_quantity<=0:
                    return
                order = OrderEvent(symbol=event.symbol,order_type="MKT",direction="SELL",quantity=stock_quantity)
                self.events.put(order)
        elif event.signal_type == "EXIT" and self.stock_size!=0 and not self.is_exiting:
            if self.stock_size>0:
                order= OrderEvent(
                    symbol=event.symbol,
                    order_type="MKT",
                    direction="SELL",
                    quantity=self.stock_size
                )
                self.events.put(order)
                self.is_exiting=True
            elif self.stock_size<0:
                order= OrderEvent(
                    symbol=event.symbol,
                    order_type="MKT",
                    direction="BUY",
                    quantity=abs(self.stock_size)
                )
                self.events.put(order)
                self.is_exiting=True                

    def update_fill(self,event):
        if event.type !="FILL":
            return

        if self.stock_size ==0:
            if event.direction == "BUY":
                cost = (event.fill_price*event.quantity)+event.commission
                self.current_cash-=cost
                self.stock_size+=event.quantity
                self.position_type = "LONG"

            elif event.direction == "SELL":
                revenue = (event.fill_price*event.quantity)-event.commission
                self.current_cash+=revenue
                self.stock_size -= event.quantity
                self.position_type = "SHORT"
                self.lowest_price = event.fill_price
            self.entry_price = event.fill_price
            self.entry_date = event.timestamp
            self.entry_atr = self.data_handler.calc_atr(14)
        else:
            if self.position_type == "LONG":
                revenue = (event.fill_price*event.quantity)-event.commission
                self.current_cash += revenue
                pnl = (event.fill_price - self.entry_price) * event.quantity - (2 * event.commission)
                pnl_percent = ((event.fill_price/self.entry_price)-1.0)*100

            elif self.position_type =="SHORT":
                cost = (event.fill_price*event.quantity)+event.commission
                self.current_cash-=cost
                pnl = (self.entry_price - event.fill_price) * event.quantity - (2 * event.commission)
                pnl_percent = ((self.entry_price - event.fill_price) / self.entry_price) * 100
                self.lowest_price = event.fill_price



            trade_record = {
                "symbol" : event.symbol,
                "entry_price" : self.entry_price,
                "exit_price"  : event.fill_price,
                "quantity"  : event.quantity,
                "pnl" : pnl,
                "pnl_percent" : pnl_percent,
                "entry_date" : self.entry_date,
                "exit_date" : event.timestamp 
            }
            self.trades.append(trade_record)
            self.entry_price = 0.0
            self.entry_date = None
            self.is_exiting = False
            self.highest_price=0.0
            self.is_stop_changed = False
            self.entry_atr = 0.0
            self.stock_size =0
            self.position_type = None
            self.lowest_price = 99999999

    def print_performance_summary(self):
        total_trades = len(self.trades)
        if total_trades == 0 :
            print("İşlem gerçekleştirilmedi")
            return
        winning_trades = [t for t in self.trades if t["pnl"]>0]
        losing_trades = [t for t in self.trades if t["pnl"]<=0]
        win_rate = (len(winning_trades)/total_trades)*100

        total_pnl = sum(t["pnl"] for t in self.trades)
        avg_win = (sum(t["pnl"] for t in winning_trades)/len(winning_trades)) if winning_trades else 0.0
        avg_loss = (sum(t["pnl"] for t in losing_trades)/len(losing_trades)) if losing_trades else 0.0
        max_loss = min(t["pnl"] for t in self.trades )
        max_win = max(t["pnl"] for t in self.trades)


        print("\n" + "="*45)
        print("          PERFORMANS RAPORU")
        print("="*45)
        print(f"Toplam İşlem Sayısı : {total_trades}")
        print(f"Kazanan İşlemler    : {len(winning_trades)}")
        print(f"Kaybeden İşlemler   : {len(losing_trades)}")
        print(f"Kazanma Oranı (Win%): {win_rate:.2f}%")
        print(f"Toplam Net Kâr/Zarar: {total_pnl:.2f} TL")
        print(f"Ortalama Kazanç     : {avg_win:.2f} TL")
        print(f"Ortalama Kayıp      : {avg_loss:.2f} TL")
        print(f"En Büyük Tekil Zarar: {max_loss:.2f} TL")
        print(f"En Büyük Tekil Kazanç: {max_win:.2f} TL")
        print(f"Kalan Nakit         : {self.current_cash:.2f} TL")
        print(f"Açık Kalan Hisse Adedi: {self.stock_size}")
        print(f"Max Dropout         :{self.worst_dropout:.2f}")
        print("="*45 + "\n")


    def update_market(self,event):
        equity = (self.stock_size*event.close)+self.current_cash

        if self.highest_equity<equity:
            self.highest_equity=equity

        dropout = ((equity-self.highest_equity)/self.highest_equity)*100
        if self.worst_dropout>dropout:
            self.worst_dropout=dropout

        if self.stock_size > 0 and not self.is_exiting:

            if self.highest_price < event.high:
                self.highest_price=event.high

            if self.entry_atr > 0:
                stop_point = max(
                    self.entry_price -(2*self.entry_atr),
                    self.highest_price-(2.5*self.entry_atr)
                )

                target_price = self.entry_price + (3.5*self.entry_atr)
            else:
                stop_point = self.entry_price * (1-0.03)
                target_price = self.entry_price *(1+0.08)

            profit_raito = (self.highest_price/self.entry_price)-1.0
            if profit_raito >=0.08:
                self.is_stop_changed = True        
            #if not self.is_stop_changed:
             #   stop_point = (self.entry_price)*(1-0.03)# yüzdeliği buradan değiştir
            #elif self.is_stop_changed:
            #   stop_point=(self.highest_price)*(1-0.10)


            if event.low <= stop_point or event.high>=target_price:
                order=OrderEvent(symbol=event.symbol,order_type="MKT",direction="SELL",quantity=self.stock_size)
                self.events.put(order)
                self.is_exiting = True
        elif self.stock_size<0 and not self.is_exiting:
            if event.low < self.lowest_price:
                self.lowest_price = event.low

            if self.entry_atr > 0:
                stop_point = min(self.entry_price +(2*self.entry_atr),self.lowest_price+(2.5*self.entry_atr))
                target_price = self.entry_price - (3.5*self.entry_atr)
            else:
                stop_point = self.entry_price * (1+0.03)
                target_price = self.entry_price * (1-0.08)

            if event.high >= stop_point or event.low <= target_price:
                order = OrderEvent(symbol=event.symbol,order_type="MKT",direction="BUY",quantity=abs(self.stock_size))
                self.events.put(order)
                self.is_exiting = True
            

