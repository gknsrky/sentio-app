# python_scripts/scalping_indicator/top_scalping_indicator.py

import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    Trend, geri çekilme ve momentumu birleştiren gelişmiş bir scalping stratejisi.
    EMA(50) ile ana trendi, EMA(9) ile geri çekilmeyi, Stochastic ile de
    giriş momentumunu teyit eder.
    """
    if df is None or len(df) < 55:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 55 mum)."]}

    try:
        # --- Parametreler ---
        trend_ema_period = 50
        pullback_ema_period = 9
        stoch_k = 14
        stoch_d = 3
        stoch_smooth = 3

        # --- Hesaplamalar ---
        df.ta.ema(length=trend_ema_period, append=True)
        df.ta.ema(length=pullback_ema_period, append=True)
        df.ta.stoch(k=stoch_k, d=stoch_d, smooth_k=stoch_smooth, append=True)
        
        df.dropna(inplace=True)
        if len(df) < 2:
            return {"sinyal": "YOK", "sebepler": ["İndikatör hesaplaması sonrası veri kalmadı."]}

        # --- Verileri Al ---
        last = df.iloc[-1]
        prev = df.iloc[-2]

        # EMA'lar
        last_trend_ema = last[f'EMA_{trend_ema_period}']
        last_pullback_ema = last[f'EMA_{pullback_ema_period}']
        
        # Stochastic
        k_col = f'STOCHk_{stoch_k}_{stoch_d}_{stoch_smooth}'
        last_k = last[k_col]
        prev_k = prev[k_col]
        
        signal = "YOK"
        reason = "Scalping için uygun bir formasyon yok."

        # --- Sinyal Mantığı ---

        # YÜKSELİŞ Sinyali (Buy the Dip)
        # 1. Ana Trend YUKARI mı? (Fiyat > 50 EMA)
        if last['close'] > last_trend_ema:
            # 2. Fiyat 9 EMA'ya geri çekilip destek buldu mu? (Low <= 9 EMA < Close)
            if last['low'] <= last_pullback_ema and last['close'] > last_pullback_ema:
                # 3. Momentum yukarı dönüyor mu? (Stochastic yükseliyor mu?)
                if last_k > prev_k and last_k < 80: # Aşırı alımda değilken
                    signal = "YUKARI"
                    reason = "Trend YUKARI, 9 EMA'dan destek alındı ve Momentum onayladı."

        # DÜŞÜŞ Sinyali (Sell the Rally)
        # 1. Ana Trend AŞAĞI mı? (Fiyat < 50 EMA)
        elif last['close'] < last_trend_ema:
            # 2. Fiyat 9 EMA'ya yükselip direnç gördü mü? (High >= 9 EMA > Close)
            if last['high'] >= last_pullback_ema and last['close'] < last_pullback_ema:
                # 3. Momentum aşağı dönüyor mu? (Stochastic düşüyor mu?)
                if last_k < prev_k and last_k > 20: # Aşırı satımda değilken
                    signal = "AŞAĞI"
                    reason = "Trend AŞAĞI, 9 EMA'dan direnç görüldü ve Momentum onayladı."
        
        return {
            "sinyal": signal,
            "sebepler": [reason]
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"Top Scalping indikatörü hesaplanırken bir hata oluştu: {e}"]
        }