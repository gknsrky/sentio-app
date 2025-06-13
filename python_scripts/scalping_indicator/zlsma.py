# python_scripts/scalping_indicator/zlsma.py

import pandas as pd
import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    ZLSMA'yı (Sıfır Gecikmeli Yumuşatılmış Hareketli Ortalama) manuel olarak
    hesaplayarak fiyat hareketlerine en hızlı tepki veren trend sinyalini üretir.
    """
    if df is None or len(df) < 30:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 30 mum)."]}

    try:
        # --- Parametreler ---
        zlsma_period = 21

        # --- MANUEL ZLSMA HESAPLAMASI ---
        # Gecikmeyi hesapla
        lag = (zlsma_period - 1) // 2
        # Gecikmesi azaltılmış kaynak veriyi oluştur
        source_data = 2 * df['close'] - df['close'].shift(lag)
        
        # Bu yeni kaynak veri üzerinden EMA alarak ZLSMA'yı elde et
        zlsma_series = ta.ema(source_data, length=zlsma_period)
        
        # Eğer hesaplama başarısız olursa (veri yetersizliği vb.)
        if zlsma_series is None:
            return {"sinyal": "YOK", "sebepler": ["ZLSMA manuel hesaplanamadı."]}

        df['ZLSMA_MANUAL'] = zlsma_series
        df.dropna(inplace=True)
        
        if df.empty:
            return {"sinyal": "YOK", "sebepler": ["ZLSMA hesaplaması sonrası veri kalmadı."]}

        # --- Verileri Al ---
        last_candle = df.iloc[-1]
        last_close = last_candle['close']
        last_zlsma = last_candle['ZLSMA_MANUAL']

        # --- Sinyal Mantığı ---
        signal = "YOK"
        reason = f"Fiyat ({last_close:.4f}) ZLSMA'ya ({last_zlsma:.4f}) çok yakın."

        if last_close > last_zlsma:
            signal = "YUKARI"
            reason = f"Fiyat ({last_close:.4f}) ZLSMA({zlsma_period})'nın ({last_zlsma:.4f}) üzerinde."
        elif last_close < last_zlsma:
            signal = "AŞAĞI"
            reason = f"Fiyat ({last_close:.4f}) ZLSMA({zlsma_period})'nın ({last_zlsma:.4f}) altında."

        return {
            "sinyal": signal,
            "sebepler": [reason]
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"ZLSMA (manuel) sinyali hesaplanırken bir hata oluştu: {e}"]
        }