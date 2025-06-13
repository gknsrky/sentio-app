# python_scripts/scalping_indicator/macd_signal.py

import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    MACD indikatörünü kullanarak momentum ve potansiyel trend dönüşü sinyalleri üretir.
    Hem MACD/Sinyal çizgisi kesişimini hem de o anki histogram değerini döndürür.
    """
    if df is None or len(df) < 35: # Yavaş periyot + sinyal periyodu + biraz marj
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 35 mum)."], "value": None}

    try:
        # --- Parametreler ---
        fast_period = 12
        slow_period = 26
        signal_period = 9

        # --- Hesaplama ---
        df.ta.macd(fast=fast_period, slow=slow_period, signal=signal_period, append=True)
        df.dropna(inplace=True)

        if len(df) < 2:
            return {"sinyal": "YOK", "sebepler": ["MACD hesaplaması sonrası veri kalmadı."], "value": None}

        # --- Verileri Al ---
        last_candle = df.iloc[-1]
        previous_candle = df.iloc[-2]

        # Kolon adlarını tanımla
        macd_line_col = f'MACD_{fast_period}_{slow_period}_{signal_period}'
        signal_line_col = f'MACDs_{fast_period}_{slow_period}_{signal_period}'
        histogram_col = f'MACDh_{fast_period}_{slow_period}_{signal_period}' # ⭐ YENİ

        # Son iki mumdaki değerleri al
        last_macd = last_candle[macd_line_col]
        last_signal = last_candle[signal_line_col]
        prev_macd = previous_candle[macd_line_col]
        prev_signal = previous_candle[signal_line_col]
        
        # ⭐ YENİ: Histogram değerini al ve yuvarla
        last_histogram = last_candle[histogram_col]
        numeric_value = round(last_histogram, 5) # Histogram küçük değerler alabilir, hassasiyet önemli.


        # --- Sinyal Mantığı (MACD/Sinyal Çizgisi Kesişimi) ---
        signal = "YOK"
        reason = f"MACD ve Sinyal çizgileri arasında bir kesişim yok. Histogram: {numeric_value}"

        if prev_macd < prev_signal and last_macd > last_signal:
            signal = "YUKARI"
            reason = "MACD çizgisi, Sinyal çizgisini yukarı yönlü kesti (Bullish Crossover)."

        elif prev_macd > prev_signal and last_macd < last_signal:
            signal = "AŞAĞI"
            reason = "MACD çizgisi, Sinyal çizgisini aşağı yönlü kesti (Bearish Crossover)."

        # --- ⭐ GÜNCELLENMİŞ ÇIKTI ---
        return {
            "sinyal": signal,
            "sebepler": [reason],
            "value": numeric_value # Sayısal değer olarak histogramı ekliyoruz
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"MACD sinyali hesaplanırken bir hata oluştu: {e}"],
            "value": None
        }