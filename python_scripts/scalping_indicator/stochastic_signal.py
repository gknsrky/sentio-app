# python_scripts/scalping_indicator/stochastic_signal.py

import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    Stochastic Osilatörünü kullanarak aşırı alım/satım bölgelerindeki
    kesişimleri tespit ederek yüksek olasılıklı tersine dönüş sinyalleri üretir.
    """
    if df is None or len(df) < 20:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 20 mum)."]}

    try:
        # --- Parametreler ---
        # Stochastic için standart parametreler
        k_period = 14
        d_period = 3
        smooth_k = 3
        oversold_level = 20
        overbought_level = 80

        # --- Hesaplama ---
        # pandas-ta ile Stochastic'i hesapla. STOCHk ve STOCHd kolonlarını ekler.
        df.ta.stoch(k=k_period, d=d_period, smooth_k=smooth_k, append=True)
        
        df.dropna(inplace=True)
        if len(df) < 2:
            return {"sinyal": "YOK", "sebepler": ["Stochastic hesaplaması sonrası veri kalmadı."]}

        # --- Verileri Al ---
        last_candle = df.iloc[-1]
        previous_candle = df.iloc[-2]

        # pandas-ta'nın kullandığı kolon adları
        k_col = f'STOCHk_{k_period}_{d_period}_{smooth_k}'
        d_col = f'STOCHd_{k_period}_{d_period}_{smooth_k}'

        last_k = last_candle[k_col]
        last_d = last_candle[d_col]
        prev_k = previous_candle[k_col]
        prev_d = previous_candle[d_col]

        # --- Sinyal Mantığı ---
        signal = "YOK"
        reason = "Stochastic'te belirgin bir sinyal yok."

        # YÜKSELİŞ Sinyali: Aşırı satım bölgesinde yukarı yönlü kesişim
        # Önceki mumda K, D'nin altındayken ve D aşırı satımdayken, şimdiki mumda K, D'nin üstüne çıkmışsa
        if prev_k < prev_d and last_k > last_d and prev_d < oversold_level:
            signal = "YUKARI"
            reason = f"Stochastic aşırı satım bölgesinde ({oversold_level}) yukarı kesti."
        
        # DÜŞÜŞ Sinyali: Aşırı alım bölgesinde aşağı yönlü kesişim
        # Önceki mumda K, D'nin üstündeyken ve D aşırı alımdaysa, şimdiki mumda K, D'nin altına inmişse
        elif prev_k > prev_d and last_k < last_d and prev_d > overbought_level:
            signal = "AŞAĞI"
            reason = f"Stochastic aşırı alım bölgesinde ({overbought_level}) aşağı kesti."
        
        return {
            "sinyal": signal,
            "sebepler": [reason]
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"Stochastic sinyali hesaplanırken bir hata oluştu: {e}"]
        }