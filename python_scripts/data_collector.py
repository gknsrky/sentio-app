# data_collector.py
# GÖREVİ: Belirlenen coin/zaman dilimleri için ham fiyat verisini çekmek ve ayrı CSV dosyalarına kaydetmek.
# YENİ ÖZELLİKLER:
# 1. Genişletilmiş ve kategorize edilmiş coin listesi.
# 2. Sabit tarih yerine, zaman dilimine göre dinamik mum sayısı hedefleme.
# 3. Kesintiye uğrayan indirmelerin kaldığı yerden devam etme yeteneği.

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# --- Konfigürasyon Alanı ---

BINANCE_API_URL = "https://api.binance.com/api/v3/klines"

# Akıllı ve çeşitlendirilmiş coin listesi (12 Adet)
# Kategoriler: Piyasa Liderleri, Büyük Platformlar, Kategori Temsilcileri, Ekstra Çeşitlilik
COIN_LIST = [
    "BTCUSDT", "ETHUSDT",       # Piyasa Temelleri
    "BNBUSDT", "SOLUSDT", "AVAXUSDT", "ADAUSDT", "XRPUSDT", "DOTUSDT", # Büyük Platform Coin'leri
    "LINKUSDT", "MATICUSDT",    # DeFi ve Layer-2 Temsilcileri
    "ARBUSDT",                  # Popüler Yeni Layer-2
    "DOGEUSDT"                  # Yüksek Volatilite / Meme Coin Temsilcisi
]

# GÜNCELLEME: Projemizde kullanacağımız zaman dilimleri listesine 1m, 3m ve 5m eklendi.
TIME_FRAMES = ["1m", "3m", "5m", "15m", "1h", "4h", "1d", "1w"]

# GÜNCELLEME: Her zaman dilimi için hedef mum sayısı. 'None' tüm veriyi çeker.
CANDLE_TARGETS = {
    "1m": 15000,   # Düşük zaman dilimleri için 15,000 mum
    "3m": 15000,
    "5m": 15000,
    "15m": 15000,
    "1h": 25000,   # Orta zaman dilimleri için 25,000 mum
    "4h": 25000,
    "1d": None,    # None, çekilebilecek en eski veriden itibaren anlamına gelir
    "1w": None
}

# GÜNCELLEME: Zaman dilimlerini milisaniyeye çevirmek için yardımcı sözlüğe yeni zaman dilimleri eklendi.
TIMEFRAME_TO_MS = {
    '1m': 1 * 60 * 1000,
    '3m': 3 * 60 * 1000,
    '5m': 5 * 60 * 1000,
    '15m': 15 * 60 * 1000,
    '1h': 60 * 60 * 1000,
    '4h': 4 * 60 * 60 * 1000,
    '1d': 24 * 60 * 60 * 1000,
    '1w': 7 * 24 * 60 * 60 * 1000
}

# --- Fonksiyonlar ---

def get_binance_data(symbol, interval, start_time_ms):
    """Belirtilen başlangıç zamanından itibaren Binance'ten veri çeker."""
    all_data = []
    startTime = start_time_ms
    
    while True:
        params = {"symbol": symbol, "interval": interval, "startTime": startTime, "limit": 1000}
        try:
            response = requests.get(BINANCE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            if not data:
                break # API'den veri gelmiyorsa döngüyü sonlandır
            
            all_data.extend(data)
            startTime = data[-1][0] + 1  # Bir sonraki isteğin başlangıç zamanını ayarla
            print(f"  -> {symbol} - {interval}: {len(all_data)} yeni mum çekildi.", end='\r')
            time.sleep(0.3) # API limitlerine takılmamak için bekle
        except requests.exceptions.RequestException as e:
            print(f"\nAPI isteği hatası: {e}")
            time.sleep(10) # Hata durumunda 10 saniye bekle ve tekrar dene
            continue
            
    return all_data

def process_and_prepare_dataframe(data_list):
    """API'den gelen listeyi işleyip, projemize uygun bir DataFrame'e dönüştürür."""
    if not data_list:
        return pd.DataFrame()
        
    columns = ["time", "open", "high", "low", "close", "volume", "close_time", "qav", "trades", "tbbav", "tbqav", "ignore"]
    df = pd.DataFrame(data_list, columns=columns)
    df = df[["time", "open", "high", "low", "close", "volume"]]
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df["time"] = pd.to_datetime(df["time"], unit='ms')
    df.set_index("time", inplace=True)
    df.dropna(inplace=True)
    return df

# --- Ana Çalışma Bloğu ---

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, 'data', 'raw_price_data')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for coin in COIN_LIST:
        for tf in TIME_FRAMES:
            file_path = os.path.join(output_dir, f"{coin}-{tf}.csv")
            start_time_ms = 0
            
            if os.path.exists(file_path):
                print(f"'{file_path}' zaten mevcut. Yeni veriler için kontrol ediliyor...")
                existing_df = pd.read_csv(file_path, index_col='time', parse_dates=True)
                if not existing_df.empty:
                    last_timestamp = existing_df.index[-1].timestamp()
                    start_time_ms = int(last_timestamp * 1000) + 1
                else:
                    # Dosya boşsa, sıfırdan veri çekme mantığına geri dön
                    # Bu blok boş bırakılarak start_time_ms'in 0 kalması ve
                    # aşağıdaki "yeni veri çekme" bloğunun tetiklenmesi sağlanır.
                    pass
                    
            if start_time_ms == 0: # Eğer dosya yoksa veya boşsa bu blok çalışır
                print(f"'{file_path}' için yeni veri çekilecek.")
                target_candle_count = CANDLE_TARGETS.get(tf)
                if target_candle_count:
                    total_ms_to_fetch = target_candle_count * TIMEFRAME_TO_MS[tf]
                    start_datetime = datetime.now() - timedelta(milliseconds=total_ms_to_fetch)
                    start_time_ms = int(start_datetime.timestamp() * 1000)
                else:
                    start_time_ms = int(datetime(2017, 1, 1).timestamp() * 1000)
            
            new_data_list = get_binance_data(coin, tf, start_time_ms)
            
            if new_data_list:
                new_df = process_and_prepare_dataframe(new_data_list)
                
                if os.path.exists(file_path) and not existing_df.empty:
                    new_df.to_csv(file_path, mode='a', header=False)
                    print(f"\n-> {len(new_df)} yeni veri '{file_path}' dosyasına eklendi.")
                else:
                    new_df.to_csv(file_path)
                    print(f"\n-> Veri '{file_path}' dosyasına kaydedildi.")
            else:
                print(f"\n{coin}-{tf} için yeni veri bulunamadı.")

    print("\n" + "="*50)
    print("TÜM HAM VERİ ÇEKME İŞLEMLERİ TAMAMLANDI!")
    print("="*50)