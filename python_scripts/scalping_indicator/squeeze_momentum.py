# python_scripts/scalping_indicator/squeeze_momentum.py

import pandas_ta as ta
import pandas as pd
import sys

def calculate(df, symbol, interval):
    """
    Squeeze Momentum indikatörünü kullanarak piyasadaki sıkışmaları (düşük volatilite)
    ve ardından gelen momentum patlamalarını tespit eder. (Tüm hataları düzeltilmiş nihai versiyon)
    """
    if df is None or len(df) < 25:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 25 mum)."]}

    try:
        # --- Parametreler ---
        bb_len = 20
        bb_std = 2.0
        kc_len = 20
        kc_scalar = 1.5
        use_pro_tr = True 

        # --- Hesaplama ---
        squeeze_df = df.ta.squeeze_pro(bb_length=bb_len, bb_std=bb_std, kc_length=kc_len, kc_scalar=kc_scalar, use_tr=use_pro_tr)
        df = pd.concat([df, squeeze_df], axis=1)
        
        df.dropna(inplace=True)
        if df.empty:
            return {"sinyal": "YOK", "sebepler": ["Squeeze Pro hesaplaması sonrası veri kalmadı."]}

        # --- Son Mum Verilerini Al ---
        last_candle = df.iloc[-1]
        
        # Debug çıktısından gelen DOĞRU kolon adları
        squeeze_on_col = 'SQZPRO_ON_WIDE'
        momentum_col = f'SQZPRO_{bb_len}_{bb_std}_{kc_len}_{"2" if use_pro_tr else ""}_{kc_scalar}_1'

        squeeze_on = last_candle[squeeze_on_col]
        momentum_value = last_candle[momentum_col]
        
        # --- Sinyal Mantığı ---
        signal = "YOK"
        reason = "Momentum sıfır veya sıkışma durumu yok."

        if squeeze_on == 1:
            signal = "SIKIŞMA"
            reason = "Piyasa sıkışıyor, volatilite patlaması bekleniyor."
        else:
            if momentum_value > 0:
                signal = "YUKARI"
                reason = f"Yükseliş momentumu aktif (Değer: {momentum_value:.2f})."
            elif momentum_value < 0:
                signal = "AŞAĞI"
                reason = f"Düşüş momentumu aktif (Değer: {momentum_value:.2f})."
                
        return {
            "sinyal": signal,
            "sebepler": [reason]
        }

    # ⭐ EKSİK OLAN VE HATAYA SEBEP OLAN BLOK BURAYA EKLENDİ ⭐
    except Exception as e:
        import traceback
        return {"sinyal": "HATA", "sebepler": [f"Squeeze Momentum hatası: {e}", traceback.format_exc()]}