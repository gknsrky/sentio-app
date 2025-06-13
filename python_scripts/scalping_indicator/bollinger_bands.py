# python_scripts/scalping_indicator/bollinger_bands.py

import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    Bollinger Bantları (BBANDS) kullanarak aşırı alım/satım sinyalleri üretir.
    Mumun en yüksek/düşük değerlerinin bantlara teması kontrol edilir.
    """
    if df is None or len(df) < 20:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 20 mum)."]}

    try:
        bb_length = 20
        bb_std = 2.0

        df.ta.bbands(length=bb_length, std=bb_std, append=True)
        df.dropna(inplace=True)

        if df.empty:
            return {"sinyal": "YOK", "sebepler": ["Bollinger Bantları hesaplaması sonrası veri kalmadı."]}

        # --- Sinyal Üretimi için Gerekli Veriler ---
        # En son (güncel) muma ait tüm verileri alıyoruz.
        last_candle = df.iloc[-1]
        last_high = last_candle['high']
        last_low = last_candle['low']
        upper_band = last_candle[f'BBU_{bb_length}_{bb_std}']
        lower_band = last_candle[f'BBL_{bb_length}_{bb_std}']
        
        signal = "YOK"
        reason = "Fiyat bantların içinde."

        # ⭐ GÜNCELLENMİŞ SİNYAL MANTIĞI ⭐
        # Eğer son mumun en yüksek değeri üst banda değdiyse veya geçtiyse (aşırı alım)
        if last_high >= upper_band:
            signal = "AŞAĞI"
            reason = f"En Yüksek ({last_high:.4f}) Üst Banda ({upper_band:.4f}) ulaştı."
        
        # Eğer son mumun en düşük değeri alt banda değdiyse veya altına indiyse (aşırı satım)
        elif last_low <= lower_band:
            signal = "YUKARI"
            reason = f"En Düşük ({last_low:.4f}) Alt Banda ({lower_band:.4f}) ulaştı."

        return {
            "sinyal": signal,
            "sebepler": [reason]
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"Bollinger Bantları hesaplanırken bir hata oluştu: {e}"]
        }