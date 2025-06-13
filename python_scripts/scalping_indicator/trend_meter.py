# python_scripts/scalping_indicator/trend_meter.py

import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    Birden fazla trend indikatörünü (EMA'lar, MACD, ADX) birleştirerek
    piyasanın genel trendi hakkında bir puanlama yapar ve 5'li sinyal üretir.
    """
    if df is None or len(df) < 210:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 210 mum)."]}

    try:
        # --- Parametreler ---
        ema_short = 20
        ema_medium = 50
        ema_long = 200

        # --- Hesaplamalar ---
        df.ta.ema(length=ema_short, append=True)
        df.ta.ema(length=ema_medium, append=True)
        df.ta.ema(length=ema_long, append=True)
        df.ta.macd(append=True)
        df.ta.adx(append=True)
        
        df.dropna(inplace=True)
        if df.empty:
            return {"sinyal": "YOK", "sebepler": ["Trend Meter hesaplaması sonrası veri kalmadı."]}

        # --- Son Mum Verilerini Al ---
        last = df.iloc[-1]
        
        # --- PUANLAMA SİSTEMİ ---
        score = 0
        reasons = []

        # 1. EMA'lar
        if last['close'] > last[f'EMA_{ema_short}']: score += 1; reasons.append("Fiyat>EMA20")
        else: score -= 1; reasons.append("Fiyat<EMA20")
        
        if last['close'] > last[f'EMA_{ema_medium}']: score += 1; reasons.append("Fiyat>EMA50")
        else: score -= 1; reasons.append("Fiyat<EMA50")
        
        if last['close'] > last[f'EMA_{ema_long}']: score += 1; reasons.append("Fiyat>EMA200")
        else: score -= 1; reasons.append("Fiyat<EMA200")

        # 2. MACD (Durum Kontrolü)
        if last['MACD_12_26_9'] > last['MACDs_12_26_9']: score += 1; reasons.append("MACD>Sinyal")
        else: score -= 1; reasons.append("MACD<Sinyal")
        
        # 3. ADX Yönü (+DI vs -DI)
        if last['DMP_14'] > last['DMN_14']: score += 1; reasons.append("+DI>-DI")
        else: score -= 1; reasons.append("-DI>+DI")
        
        # --- PUANI SİNYALE DÖNÜŞTÜR ---
        signal = "NÖTR"
        
        if score >= 4: signal = "GÜÇLÜ AL"
        elif score == 3: signal = "AL"
        elif score == -3: signal = "SAT"
        elif score <= -4: signal = "GÜÇLÜ SAT"
            
        final_reason = f"Trend Skoru: {score}/5 ({', '.join(reasons)})"

        return {
            "sinyal": signal,
            "sebepler": [final_reason]
        }
    
    # ⭐ EKSİK OLAN VE HATAYA SEBEP OLAN BLOK BURAYA EKLENDİ ⭐
    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"Trend Meter hesaplanırken bir hata oluştu: {e}"]
        }