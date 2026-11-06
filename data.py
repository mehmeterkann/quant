from borsa import MarketEvent,SignalEvent,OrderEvent,FillEvent
import pandas as pd 

class HistoricDataHandler:
    def __init__(self,events,csv_path,symbol="THYAO"):
        self.events=events
        self.symbol = symbol
        self.latest_data=[]
        self.current_index=0
        self.continue_backtest=True
        self.entry_atr = 0
        df = pd.read_csv(csv_path)
        rename_map = {
            'Tarih' : 'timestamp',
            'Şimdi' : 'close',
            'Açılış' : 'open',
            'Yüksek' : 'high',
            'Düşük' : 'low',
            'Hac.' : 'volume'
        }
        df = df.rename(columns=rename_map)

        price_cols = ['open','high','low','close']
        for col in price_cols:
            if df[col].dtype == object:
                df[col] = df[col].str.replace('.','',regex=False).str.replace(',','.',regex=False).astype(float)
        if 'volume' not in df.columns:
            df['volume'] =0
        
        df['symbol'] = self.symbol
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['atr']=self.entry_atr
        df = df.sort_values('timestamp').reset_index(drop=True)
        self.bar_data = df[['timestamp','symbol','open','high','low','close','volume']].to_dict('records')
        self.current_index = 0
        self.bars = []
        self.continue_backtest = True
    def update_bars(self):
        if self.current_index < len(self.bar_data):
            bar = self.bar_data[self.current_index]
            if self.current_index ==0:
                true_range = bar['high']-bar['low']
            else:
                true_range = max((bar['high']-bar['low']),abs(bar['high']-self.bar_data[self.current_index-1]['close']),abs(bar['low']-self.bar_data[self.current_index-1]['close']))
            bar['true_range'] = true_range
            self.latest_data.append(bar)
            market = MarketEvent(bar["timestamp"],bar["symbol"],bar["open"],bar["high"],bar["low"],bar["close"],bar["volume"],bar['true_range'])
            self.events.put(market)
            self.current_index+=1
        else:
            self.continue_backtest=False


    def get_latest_bar(self):
        if self.latest_data:
            return self.latest_data[-1]
        return None

    def get_latest_bars(self,N=1):
        if self.latest_data:
            return self.latest_data[-N:]
        return []

    def calc_atr(self,N=14):
        if self.latest_data and len(self.latest_data)>=N:
            recent_bars = self.latest_data[-N:]
            true_range = sum(b['true_range'] for b in recent_bars)
            return true_range/N
        else:
            return 0.0
