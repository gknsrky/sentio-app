# python_scripts/scalping_indicator/qqe_mod.py

import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    QQE Mod indikatörünü kullanarak kesişim ve sıfır çizgisi filtresiyle
    derecelendirilmiş momentum sinyalleri üretir.
    """
    if df is None or len(df) < 30:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 30 mum)."]}

    try:
        # --- Parametreler ---
        # QQE Mod için standart parametreler
        qqe_len = 14      # RSI Periyodu
        qqe_smooth = 5    # RSI Yumuşatma
        qqe_fast_factor = 5
        qqe_slow_factor = 3
        qqe_level = 50      # Sıfır çizgisi seviyesi

        # --- Hesaplama ---
        # pandas-ta ile QQE'yi hesapla
        df.ta.qqe(length=qqe_len, smooth=qqe_smooth, factor=qqe_fast_factor, qqe_l=qqe_slow_factor, append=True)
        
        df.dropna(inplace=True)
        if len(df) < 2:
            return {"sinyal": "YOK", "sebepler": ["QQE hesaplaması sonrası veri kalmadı."]}

        # --- Verileri Al ---
        # Kesişimi tespit etmek için son iki mumun verilerini al
        last_candle = df.iloc[-1]
        previous_candle = df.iloc[-2]

        # pandas-ta'nın oluşturduğu kolon adları
        qqe_fast_col = f'QQE_{qqe_len}_{qqe_smooth}_{qqe_fast_factor:.1f}'
        qqe_slow_col = f'QQEl_{qqe_len}_{qqe_smooth}_{qqe_slow_factor:.1f}'

        last_fast = last_candle[qqe_fast_col]
        last_slow = last_candle[qqe_slow_col]
        prev_fast = previous_candle[qqe_fast_col]
        prev_slow = previous_candle[qqe_slow_col]
        
        signal = "YOK"
        reason = "QQE çizgileri arasında bir kesişim yok."

        # --- Sinyal Mantığı ---
        
        # YÜKSELİŞ KESİŞİMİ
        if prev_fast < prev_slow and last_fast > last_slow:
            # GÜÇLÜ mü? Kesişim 50 seviyesinin üstünde mi?
            if last_fast > qqe_level:
                signal = "GÜÇLÜ AL"
                reason = f"QQE yukarı kesti (Güçlü - {qqe_level} seviyesi üzeri)."
            else:
                signal = "AL"
                reason = f"QQE yukarı kesti ({qqe_level} seviyesi altı)."
        
        # DÜŞÜŞ KESİŞİMİ
        elif prev_fast > prev_slow and last_fast < last_slow:
            # GÜÇLÜ mü? Kesişim 50 seviyesinin altında mı?
            if last_fast < qqe_level:
                signal = "GÜÇLÜ SAT"
                reason = f"QQE aşağı kesti (Güçlü - {qqe_level} seviyesi altı)."
            else:
                signal = "SAT"
                reason = f"QQE aşağı kesti ({qqe_level} seviyesi üzeri)."

        return {
            "sinyal": signal,
            "sebepler": [reason]
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"QQE Mod sinyali hesaplanırken bir hata oluştu: {e}"]
        }