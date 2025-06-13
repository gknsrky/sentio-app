# python_scripts/scalping_indicator/vwap_signal.py

import pandas as pd

def calculate(df, symbol, interval):
    """
    Fiyatın VWAP'ı kırmasını ve bu kırılımın yüksek hacimle onaylanmasını
    kontrol eden bir breakout stratejisi.
    """
    if df is None or len(df) < 25:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 25 mum)."]}

    try:
        # --- Parametreler ---
        volume_avg_period = 20
        # Hacmin, ortalamanın en az 1.5 katı olmasını istiyoruz.
        volume_multiplier = 1.5 

        # --- Hesaplamalar ---
        # 1. Günlük VWAP (Her gün sıfırlanır)
        df['TPV'] = ((df['high'] + df['low'] + df['close']) / 3) * df['volume']
        df['CumVol'] = df.groupby(df.index.date)['volume'].cumsum()
        df['CumTPV'] = df.groupby(df.index.date)['TPV'].cumsum()
        df['VWAP'] = df['CumTPV'] / df['CumVol']
        
        # 2. Ortalama Hacim
        df['Avg_Volume'] = df['volume'].rolling(window=volume_avg_period).mean()
        
        df.dropna(inplace=True)
        if len(df) < 2:
            return {"sinyal": "YOK", "sebepler": ["VWAP/Hacim hesaplaması sonrası veri kalmadı."]}

        # --- Verileri Al ---
        last = df.iloc[-1]
        prev = df.iloc[-2]

        # --- Sinyal Mantığı ---
        signal = "YOK"
        reason = "VWAP'ta hacim onaylı bir kırılım yok."

        # YÜKSELİŞ Sinyali: VWAP yukarı kırılır VE Hacim ortalamanın üzerindeyse
        if prev['close'] < prev['VWAP'] and last['close'] > last['VWAP'] and last['volume'] > (last['Avg_Volume'] * volume_multiplier):
            signal = "YUKARI"
            reason = f"Fiyat VWAP'ı yüksek hacimle ({last['volume']:.0f}) yukarı kırdı."

        # DÜŞÜŞ Sinyali: VWAP aşağı kırılır VE Hacim ortalamanın üzerindeyse
        elif prev['close'] > prev['VWAP'] and last['close'] < last['VWAP'] and last['volume'] > (last['Avg_Volume'] * volume_multiplier):
            signal = "AŞAĞI"
            reason = f"Fiyat VWAP'ı yüksek hacimle ({last['volume']:.0f}) aşağı kırdı."
            
        return {
            "sinyal": signal,
            "sebepler": [reason]
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"VWAP (Hacim Onaylı) sinyali hesaplanırken bir hata oluştu: {e}"]
        }