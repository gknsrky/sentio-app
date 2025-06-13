# python_scripts/scalping_indicator/rsi_signal.py

import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    RSI (Göreceli Güç Endeksi) kullanarak kademeli momentum sinyalleri üretir.
    Hem sinyali (AL/SAT) hem de o anki sayısal RSI değerini döndürür.
    """
    if df is None or len(df) < 20:
        # Hata veya yetersiz veri durumunda 'value' None olarak döndürülür
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 20 mum)."], "value": None}

    try:
        # --- Parametreler ---
        rsi_period = 14
        oversold_level = 30
        overbought_level = 70
        mid_level_upper = 55
        mid_level_lower = 45

        # --- Hesaplama ---
        df.ta.rsi(length=rsi_period, append=True)
        df.dropna(inplace=True)
        
        if len(df) < 2:
            return {"sinyal": "YOK", "sebepler": ["RSI hesaplaması sonrası veri kalmadı."], "value": None}

        # --- Verileri Al ---
        last_rsi = df[f'RSI_{rsi_period}'].iloc[-1]
        prev_rsi = df[f'RSI_{rsi_period}'].iloc[-2]
        
        # Sayısal değeri yuvarlayarak hazırlayalım
        numeric_value = round(last_rsi, 2)

        signal = "NÖTR"
        reason = f"RSI ({numeric_value}) orta bölgede ({mid_level_lower}-{mid_level_upper})."

        # --- Sinyal Mantığı ---

        # 1. ÖNCELİK: Güçlü Tersine Dönüş Sinyalleri
        if prev_rsi < oversold_level and last_rsi > oversold_level:
            signal = "GÜÇLÜ AL"
            reason = f"RSI ({numeric_value}) aşırı satım bölgesinden ({oversold_level}) çıktı."
        
        elif prev_rsi > overbought_level and last_rsi < overbought_level:
            signal = "GÜÇLÜ SAT"
            reason = f"RSI ({numeric_value}) aşırı alım bölgesinden ({overbought_level}) çıktı."
        
        # 2. ÖNCELİK: Trend Devam Sinyalleri
        else:
            if last_rsi > mid_level_upper:
                signal = "AL"
                reason = f"RSI ({numeric_value}) yükseliş momentumu bölgesinde (> {mid_level_upper})."
            elif last_rsi < mid_level_lower:
                signal = "SAT"
                reason = f"RSI ({numeric_value}) düşüş momentumu bölgesinde (< {mid_level_lower})."
        
        # --- ⭐ GÜNCELLENMİŞ ÇIKTI ---
        # Çıktı sözlüğüne 'value' anahtarı eklendi.
        return {
            "sinyal": signal,
            "sebepler": [reason],
            "value": numeric_value
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"RSI sinyali hesaplanırken bir hata oluştu: {e}"],
            "value": None
        }