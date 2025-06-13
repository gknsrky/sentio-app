# python_scripts/scalping_indicator/liquidity_zones.py
import pandas as pd

def calculate(df, symbol, interval):
    if df is None or len(df) < 25:
        return {"sinyal": "YOK"}

    try:
        lookback_period = 20
        df['upper_zone'] = df['high'].rolling(window=lookback_period).max().shift(1)
        df['lower_zone'] = df['low'].rolling(window=lookback_period).min().shift(1)
        df.dropna(inplace=True)
        if df.empty:
            return {"sinyal": "YOK"}

        last_candle = df.iloc[-1]
        last_high = last_candle['high']
        last_low = last_candle['low']
        last_close = last_candle['close']
        upper_zone = last_candle['upper_zone']
        lower_zone = last_candle['lower_zone']
        
        signal = "YOK"
        reason = "Belirgin bir likidite avı yok."
        
        # Sinyal mantığı aynı kalıyor
        if last_low < lower_zone and last_close > lower_zone:
            signal = "YUKARI"
            reason = f"Alt likidite ({lower_zone:.4f}) temizlendi ve geri döndü."
        elif last_high > upper_zone and last_close < upper_zone:
            signal = "AŞAĞI"
            reason = f"Üst likidite ({upper_zone:.4f}) temizlendi ve geri döndü."

        # ⭐ YENİ: Her durumda en güncel bölgeleri data olarak döndür
        data = {
            "upper_liquidity_zone": round(upper_zone, 4),
            "lower_liquidity_zone": round(lower_zone, 4)
        }

        return {
            "sinyal": signal,
            "sebepler": [reason],
            "data": data
        }
    except Exception as e:
        return {"sinyal": "HATA", "sebepler": [f"Likidite bölgesi hesaplanırken bir hata oluştu: {e}"]}