# python_scripts/scalping_indicator/pivot_points.py

import pandas as pd

def calculate(df, symbol, interval):
    """
    Geçmiş N periyottaki en yüksek ve en düşük seviyeleri dinamik destek/direnç
    olarak belirler. Fiyat bu seviyelere yaklaştığında bir uyarı sinyali üretir.
    """
    if df is None or len(df) < 55:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 55 mum)."]}

    try:
        # --- Parametreler ---
        # Destek/Direnç seviyelerini belirlemek için geriye dönük bakılacak mum sayısı
        lookback_period = 50
        # Fiyatın seviyeye ne kadar yakın olması gerektiğini belirten yüzde
        # Örneğin 1, fiyatın toplam aralığın %1'i kadar yakın olması demektir.
        proximity_percent_threshold = 1.0

        # --- Hesaplama ---
        # Son 'lookback_period' mumun en yüksek ve en düşük değerlerini hesapla
        df['support_level'] = df['low'].rolling(window=lookback_period).min()
        df['resistance_level'] = df['high'].rolling(window=lookback_period).max()

        df.dropna(inplace=True)
        if df.empty:
            return {"sinyal": "YOK", "sebepler": ["Destek/Direnç hesaplaması sonrası veri kalmadı."]}

        # --- Verileri Al ---
        last_candle = df.iloc[-1]
        last_close = last_candle['close']
        support = last_candle['support_level']
        resistance = last_candle['resistance_level']
        
        signal = "YOK"
        reason = "Fiyat, önemli destek/direnç bölgelerinden uzakta."

        # --- Sinyal Mantığı ---
        total_range = resistance - support
        # Sıfıra bölme hatasını önle
        if total_range == 0:
            return {"sinyal": "YOK", "sebepler": ["Piyasa aralığı sıfır."]}

        # YÜKSELİŞ Uyarısı: Fiyat, desteğe çok yaklaştı mı?
        if ((last_close - support) / total_range * 100) < proximity_percent_threshold:
            signal = "YUKARI"
            reason = f"Fiyat ({last_close:.4f}) destek seviyesine ({support:.4f}) çok yakın (Potansiyel Sıçrama)."
        
        # DÜŞÜŞ Uyarısı: Fiyat, dirence çok yaklaştı mı?
        elif ((resistance - last_close) / total_range * 100) < proximity_percent_threshold:
            signal = "AŞAĞI"
            reason = f"Fiyat ({last_close:.4f}) direnç seviyesine ({resistance:.4f}) çok yakın (Potansiyel Geri Çekilme)."

        return {
            "sinyal": signal,
            "sebepler": [reason]
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"Pivot/Destek-Direnç hesaplanırken bir hata oluştu: {e}"]
        }