# python_scripts/scalping_indicator/crypto_prediction_model.py

import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    EMA'ların mevcut durumuna (trend takibi) ve RSI seviyelerine dayalı 5'li bir sinyal sistemi
    (GÜÇLÜ AL, AL, NÖTR, SAT, GÜÇLÜ SAT) üretir.
    """
    if df is None or len(df) < 50:
        return {"sinyal": "NÖTR", "sebepler": ["Yeterli veri yok (en az 50 mum)."]}

    try:
        # --- Parametreler ---
        fast_ema_period = 9
        slow_ema_period = 21
        rsi_period = 14
        
        rsi_strong_buy_threshold = 60
        rsi_buy_threshold = 50
        rsi_strong_sell_threshold = 40
        rsi_sell_threshold = 50

        # --- Hesaplamalar ---
        df.ta.ema(length=fast_ema_period, append=True)
        df.ta.ema(length=slow_ema_period, append=True)
        df.ta.rsi(length=rsi_period, append=True)
        df.dropna(inplace=True)
        
        if df.empty:
            return {"sinyal": "NÖTR", "sebepler": ["İndikatör hesaplaması sonrası veri kalmadı."]}

        # --- Son Mumun Verilerini Al ---
        last_candle = df.iloc[-1]
        last_fast_ema = last_candle[f'EMA_{fast_ema_period}']
        last_slow_ema = last_candle[f'EMA_{slow_ema_period}']
        last_rsi = last_candle[f'RSI_{rsi_period}']

        signal = "NÖTR"
        reason = "EMA'lar birbirine çok yakın veya momentum zayıf."

        # ⭐ YENİ MANTIK: KESİŞİM YERİNE MEVCUT DURUM KONTROLÜ ⭐

        # 1. Yükseliş Trendi Durumu (Hızlı EMA > Yavaş EMA)
        if last_fast_ema > last_slow_ema:
            if last_rsi > rsi_strong_buy_threshold:
                signal = "GÜÇLÜ AL"
                reason = f"Yükseliş Trendi (EMA {fast_ema_period}>{slow_ema_period}) + Güçlü RSI ({last_rsi:.1f})"
            elif last_rsi > rsi_buy_threshold:
                signal = "AL"
                reason = f"Yükseliş Trendi (EMA {fast_ema_period}>{slow_ema_period}) + RSI ({last_rsi:.1f})"
            else:
                reason = f"Yükseliş Trendi var ama RSI momentumu zayıf ({last_rsi:.1f})."

        # 2. Düşüş Trendi Durumu (Hızlı EMA < Yavaş EMA)
        elif last_fast_ema < last_slow_ema:
            if last_rsi < rsi_strong_sell_threshold:
                signal = "GÜÇLÜ SAT"
                reason = f"Düşüş Trendi (EMA {fast_ema_period}<{slow_ema_period}) + Güçlü RSI ({last_rsi:.1f})"
            elif last_rsi < rsi_sell_threshold:
                signal = "SAT"
                reason = f"Düşüş Trendi (EMA {fast_ema_period}<{slow_ema_period}) + RSI ({last_rsi:.1f})"
            else:
                reason = f"Düşüş Trendi var ama RSI momentumu zayıf ({last_rsi:.1f})."
        
        return {
            "sinyal": signal,
            "sebepler": [reason]
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"5'li modelde hata oluştu: {e}"]
        }