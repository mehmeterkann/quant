import yfinance as yf
import pandas as pd

# 1. Sembol ve parametreler
symbol = "QQQ"
interval = "15m"
period = "60d"  # Yahoo'nun 15m için izin verdiği maksimum geçmiş

print(f"{symbol} için son {period} 15m verisi indiriliyor...")

# 2. Veriyi çek
data = yf.download(tickers=symbol, period=period, interval=interval, auto_adjust=True)

# 3. Yfinance bazen çoklu indeks (MultiIndex) döner, sütunları düzeltelim
if isinstance(data.columns, pd.MultiIndex):
    data.columns = [col[0].lower() for col in data.columns]
else:
    data.columns = [col.lower() for col in data.columns]

# 4. İndeks adını timestamp yapalım ve boş satırları temizleyelim
data.index.name = "timestamp"
data.dropna(inplace=True)

# 5. CSV olarak kaydet
filename = "qqq_15m.csv"
data.to_csv(filename)
print(f"Başarılı! Veri '{filename}' dosyasına kaydedildi. Toplam bar sayısı: {len(data)}")