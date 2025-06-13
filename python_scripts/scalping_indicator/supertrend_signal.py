# python_scripts/scalping_indicator/supertrend_signal.py

import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    Supertrend indikatörünü kullanarak mevcut ana trendin yönünü belirler.
    Bu bir "durum" indikatörüdür, sürekli olarak trendin yönünü raporlar.
    """
    if df is None or len(df) < 15:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 15 mum)."]}

    try:
        # --- Parametreler ---
        # Supertrend için standart parametreler
        atr_period = 10
        atr_multiplier = 3.0

        # --- Hesaplama ---
        # pandas-ta ile Supertrend'i hesapla.
        # Bu fonksiyon, trend yönünü belirten 'SUPERTd_...' adında bir kolon ekler.
        df.ta.supertrend(length=atr_period, multiplier=atr_multiplier, append=True)

        df.dropna(inplace=True)
        if df.empty:
            return {"sinyal": "YOK", "sebepler": ["Supertrend hesaplaması sonrası veri kalmadı."]}

        # --- Verileri Al ---
        last_candle = df.iloc[-1]
        
        # Trend yönü kolonunu alıyoruz: 1 ise Yükseliş, -1 ise Düşüş.
        direction_col = f'SUPERTd_{atr_period}_{atr_multiplier:.1f}'
        direction = last_candle[direction_col]

        # --- Sinyal Mantığı ---
        signal = "YOK"
        reason = "Supertrend yön belirtmiyor."

        if direction == 1:
            signal = "YUKARI"
            reason = f"Supertrend yükseliş trendinde."
        elif direction == -1:
            signal = "AŞAĞI"
            reason = f"Supertrend düşüş trendinde."
        
        return {
            "sinyal": signal,
            "sebepler": [reason]
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"Supertrend sinyali hesaplanırken bir hata oluştu: {e}"]
        }