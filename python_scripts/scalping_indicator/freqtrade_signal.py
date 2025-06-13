# python_scripts/scalping_indicator/freqtrade_signal.py

import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    ADX ile trend gücünü filtreleyip, +DI/-DI ve StochRSI ile yön ve zamanlama
    sinyali üreten bir Freqtrade tarzı strateji.
    """
    if df is None or len(df) < 50:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 50 mum)."]}

    try:
        # --- Parametreler ---
        adx_len = 14
        adx_threshold = 25  # Güçlü trend için minimum ADX seviyesi
        
        stoch_rsi_len = 14
        stoch_rsi_k = 3
        stoch_rsi_d = 3
        stoch_rsi_oversold = 20
        stoch_rsi_overbought = 80

        # --- Hesaplamalar ---
        # ADX ve StochRSI değerlerini hesapla
        df.ta.adx(length=adx_len, append=True)
        df.ta.stochrsi(length=stoch_rsi_len, rsi_length=stoch_rsi_len, k=stoch_rsi_k, d=stoch_rsi_d, append=True)
        
        df.dropna(inplace=True)
        if df.empty:
            return {"sinyal": "YOK", "sebepler": ["İndikatör hesaplaması sonrası veri kalmadı."]}

        # --- Son Mum Verilerini Al ---
        last_candle = df.iloc[-1]
        adx = last_candle[f'ADX_{adx_len}']
        dmp = last_candle[f'DMP_{adx_len}']  # +DI çizgisi
        dmn = last_candle[f'DMN_{adx_len}']  # -DI çizgisi
        stoch_rsi_k = last_candle[f'STOCHRSIk_{stoch_rsi_len}_{stoch_rsi_len}_{stoch_rsi_k}_{stoch_rsi_d}']

        # --- Sinyal Mantığı ---
        
        # 1. ADIM: Trend Filtresi. Güçlü bir trend yoksa, sinyal üretme.
        if adx < adx_threshold:
            return {"sinyal": "NÖTR", "sebepler": [f"Trend gücü zayıf (ADX: {adx:.1f} < {adx_threshold})"]}

        # 2. ADIM: Yön ve Zamanlama Sinyalleri
        signal = "NÖTR"
        reason = "Yön belirleyici koşullar oluşmadı."

        # Yükseliş Sinyali Koşulları
        if (dmp > dmn) and (stoch_rsi_k < stoch_rsi_overbought):
            signal = "YUKARI"
            reason = f"Güçlü Trend (ADX {adx:.1f}), +DI > -DI, StochRSI ({stoch_rsi_k:.1f}) aşırı alımda değil."
        
        # Düşüş Sinyali Koşulları
        elif (dmn > dmp) and (stoch_rsi_k > stoch_rsi_oversold):
            signal = "AŞAĞI"
            reason = f"Güçlü Trend (ADX {adx:.1f}), -DI > +DI, StochRSI ({stoch_rsi_k:.1f}) aşırı satımda değil."
        
        return {
            "sinyal": signal,
            "sebepler": [reason]
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"Freqtrade sinyali hesaplanırken bir hata oluştu: {e}"]
        }