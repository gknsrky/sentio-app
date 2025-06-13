# python_scripts/scalping_indicator/ema_signal.py

import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    Fiyatın tek bir Üstel Hareketli Ortalama'ya (EMA) göre konumunu belirler.
    Hem kategorik trend sinyalini hem de fiyatın EMA'dan yüzdesel sapmasını döndürür.
    """
    if df is None or len(df) < 50:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 50 mum)."], "value": None}

    try:
        # --- Parametreler ---
        ema_period = 50

        # --- Hesaplama ---
        df.ta.ema(length=ema_period, append=True)
        df.dropna(inplace=True)

        if df.empty:
            return {"sinyal": "YOK", "sebepler": ["EMA hesaplaması sonrası veri kalmadı."], "value": None}

        # --- Verileri Al ---
        last_close = df['close'].iloc[-1]
        last_ema = df[f'EMA_{ema_period}'].iloc[-1]
        
        # ⭐ YENİ: Fiyatın EMA'dan yüzdesel sapmasını hesapla
        if last_ema > 0:
            percentage_diff = ((last_close - last_ema) / last_ema) * 100
            numeric_value = round(percentage_diff, 4)
        else:
            numeric_value = 0


        # --- Sinyal Üretimi (DEĞİŞTİRİLMEDİ) ---
        signal = "YOK"
        reason = f"Fiyat ({last_close:.4f}) EMA'ya ({last_ema:.4f}) çok yakın."

        if last_close > last_ema:
            signal = "YUKARI"
            reason = f"Fiyat ({last_close:.4f}) EMA({ema_period})'nın ({last_ema:.4f}) üzerinde."
        
        elif last_close < last_ema:
            signal = "AŞAĞI"
            reason = f"Fiyat ({last_close:.4f}) EMA({ema_period})'nın ({last_ema:.4f}) altında."

        # --- ⭐ GÜNCELLENMİŞ ÇIKTI ---
        return {
            "sinyal": signal,
            "sebepler": [reason],
            "value": numeric_value # Yüzdesel sapmayı sayısal değer olarak ekliyoruz
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"EMA sinyali hesaplanırken bir hata oluştu: {e}"],
            "value": None
        }