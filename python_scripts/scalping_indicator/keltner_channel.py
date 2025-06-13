# python_scripts/scalping_indicator/keltner_channel.py

import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    Keltner Kanallarını kullanarak daha hassas kırılım sinyalleri üretir.
    Mumun en yüksek/düşük değerlerinin kanala teması kontrol edilir.
    """
    if df is None or len(df) < 21:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 21 mum)."]}

    try:
        # --- Parametreler ---
        ema_period = 20
        atr_period = 10
        atr_multiplier = 2.0

        # --- Hesaplama ---
        df.ta.kc(length=ema_period, atr_length=atr_period, scalar=atr_multiplier, append=True)
        df.dropna(inplace=True)

        if df.empty:
            return {"sinyal": "YOK", "sebepler": ["Keltner Channel hesaplaması sonrası veri kalmadı."]}

        # --- Sinyal Üretimi için Verileri Al ---
        last_candle = df.iloc[-1]
        last_high = last_candle['high']
        last_low = last_candle['low']
        upper_channel = last_candle[f'KCUe_{ema_period}_{atr_multiplier}']
        lower_channel = last_candle[f'KCLe_{ema_period}_{atr_multiplier}']

        signal = "YOK"
        reason = "Fiyat kanal içinde."

        # ⭐ GÜNCELLENMİŞ SİNYAL MANTIĞI ⭐
        # YÜKSELİŞ Sinyali: Mumun en yüksek fiyatı üst kanala değerse veya geçerse
        if last_high >= upper_channel:
            signal = "YUKARI"
            reason = f"En Yüksek ({last_high:.4f}) üst kanala ({upper_channel:.4f}) ulaştı."
        
        # DÜŞÜŞ Sinyali: Mumun en düşük fiyatı alt kanala değerse veya altına inerse
        elif last_low <= lower_channel:
            signal = "AŞAĞI"
            reason = f"En Düşük ({last_low:.4f}) alt kanala ({lower_channel:.4f}) ulaştı."

        return {
            "sinyal": signal,
            "sebepler": [reason]
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"Keltner Channel hesaplanırken bir hata oluştu: {e}"]
        }