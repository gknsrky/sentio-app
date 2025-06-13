# python_scripts/scalping_indicator/atr_signal.py

import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    ATR (Average True Range) kullanarak piyasa volatilitesini ölçer.
    Hem kategorik sinyali (VOLATİL/DURGUN) hem de sayısal volatilite yüzdesini döndürür.
    """
    if df is None or len(df) < 20:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 20 mum)."], "value": None}

    try:
        # --- Parametreler ---
        atr_length = 14
        volatility_threshold_percent = 0.4

        # --- Hesaplama ---
        df.ta.atr(length=atr_length, append=True)
        
        df.dropna(inplace=True)
        if df.empty:
            return {"sinyal": "YOK", "sebepler": ["ATR hesaplaması sonrası veri kalmadı."], "value": None}

        latest_atr = df[f'ATRr_{atr_length}'].iloc[-1]
        last_close_price = df['close'].iloc[-1]
        
        # ATR değerini fiyata göre normalize et (yüzdeye çevir).
        atr_as_percentage = (latest_atr / last_close_price) * 100
        
        # ⭐ YENİ: Sayısal değeri yapay zeka için hazırla
        numeric_value = round(atr_as_percentage, 4)

        # --- Sinyal Üretme ---
        if atr_as_percentage > volatility_threshold_percent:
            signal = "VOLATİL"
            reason = f"Piyasa hareketli. ATR: {numeric_value:.2f}% (Eşik: >{volatility_threshold_percent}%)"
        else:
            signal = "DURGUN"
            reason = f"Piyasa durgun. ATR: {numeric_value:.2f}% (Eşik: <={volatility_threshold_percent}%)"
            
        # --- ⭐ GÜNCELLENMİŞ ÇIKTI ---
        return {
            "sinyal": signal,
            "sebepler": [reason],
            "value": numeric_value # Normalize edilmiş ATR yüzdesini ekliyoruz
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"ATR hesaplanırken bir hata oluştu: {e}"],
            "value": None
        }