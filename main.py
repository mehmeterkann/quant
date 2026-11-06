import queue

from data import HistoricDataHandler
from strategy import MovingAverageCrossStrategy
from portfolio import Portfolio
from execution import ExecutionHandler
from engine import BacktestEngine

q = queue.Queue()



data = HistoricDataHandler(q,"qqq_15m.csv","QQQ")
strategy = MovingAverageCrossStrategy(data,q,trend_window=200,fast_window=20,allow_short=False)
portfolio = Portfolio(q,data,initial_capital=100000)
execution = ExecutionHandler(q,data)
engine = BacktestEngine(q,data,strategy,portfolio,execution)
engine.run()

print(f"Kalan Nakit: {portfolio.current_cash}")

print(f"Kalan Hisse: {portfolio.stock_size}")
portfolio.print_performance_summary()

worst_trade = min(portfolio.trades, key=lambda t: t["pnl"])
print("\n--- EN BÜYÜK ZARARIN DETAYI ---")
print(f"Giriş Tarihi : {worst_trade['entry_date']} | Fiyat: {worst_trade['entry_price']}")
print(f"Çıkış Tarihi : {worst_trade['exit_date']} | Fiyat: {worst_trade['exit_price']}")
print(f"Yüzdesel Kayıp : %{worst_trade['pnl_percent']:.2f}")
print(f"Miktar (Lot)   : {worst_trade['quantity']}")
print(f"Zarar Tutarı   : {worst_trade['pnl']:.2f} TL")