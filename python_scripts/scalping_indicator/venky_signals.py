# python_scripts/scalping_indicator/venky_signals.py

import pandas as pd
import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    Gün içi en önemli seviyelerden olan VWAP'ı trend filtresi olarak,
    Stochastic RSI'ı ise giriş tetiği olarak kullanan bir strateji.
    """
    if df is None or len(df) < 30:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 30 mum)."]}

    try:
        # --- Parametreler ---
        stoch_rsi_len = 14
        oversold_level = 20
        overbought_level = 80

        # --- Hesaplamalar ---
        # 1. Stochastic RSI
        df.ta.stochrsi(length=stoch_rsi_len, append=True)
        
        # 2. Günlük VWAP (Manuel Hesaplama)
        # Her gün için kümülatif değerleri hesaplamak üzere günleri grupla
        df['TPV'] = ((df['high'] + df['low'] + df['close']) / 3) * df['volume']
        df['CumVol'] = df.groupby(df.index.date)['volume'].cumsum()
        df['CumTPV'] = df.groupby(df.index.date)['TPV'].cumsum()
        df['VWAP'] = df['CumTPV'] / df['CumVol']
        
        df.dropna(inplace=True)
        if len(df) < 2:
            return {"sinyal": "YOK", "sebepler": ["İndikatör hesaplaması sonrası veri kalmadı."]}

        # --- Verileri Al ---
        last = df.iloc[-1]
        prev = df.iloc[-2]

        # VWAP
        last_close = last['close']
        last_vwap = last['VWAP']

        # StochRSI
        k_col = f'STOCHRSIk_{stoch_rsi_len}_{stoch_rsi_len}_3_3'
        d_col = f'STOCHRSId_{stoch_rsi_len}_{stoch_rsi_len}_3_3'
        last_k = last[k_col]
        prev_k = prev[d_col]

        signal = "YOK"
        reason = "VWAP stratejisi için uygun koşullar yok."

        # --- Sinyal Mantığı ---
        
        # YÜKSELİŞ Sinyali
        # Fiyat VWAP üstünde VE StochRSI aşırı satımdan yeni çıkmışsa
        if last_close > last_vwap and prev_k < oversold_level and last_k > oversold_level:
            signal = "YUKARI"
            reason = f"Fiyat VWAP üzerinde ve StochRSI aşırı satımdan çıktı."

        # DÜŞÜŞ Sinyali
        # Fiyat VWAP altında VE StochRSI aşırı alımdan yeni çıkmışsa
        elif last_close < last_vwap and prev_k > overbought_level and last_k < overbought_level:
            signal = "AŞAĞI"
            reason = f"Fiyat VWAP altında ve StochRSI aşırı alımdan çıktı."
            
        return {
            "sinyal": signal,
            "sebepler": [reason]
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"Venky/VWAP sinyali hesaplanırken bir hata oluştu: {e}"]
        }