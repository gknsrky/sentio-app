# python_scripts/scalping_indicator/mfi_signal.py

import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    MFI (Money Flow Index) kullanarak aşırı alım/satım bölgelerinden çıkışları
    tespit ederek potansiyel tersine dönüş sinyalleri üretir.
    Hem sinyali hem de o anki MFI değerini döndürür.
    """
    if df is None or len(df) < 20:
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 20 mum)."], "value": None}

    try:
        # --- Parametreler ---
        mfi_period = 14
        oversold_level = 20
        overbought_level = 80

        # --- Hesaplama ---
        df.ta.mfi(length=mfi_period, append=True)

        df.dropna(inplace=True)
        if len(df) < 2:
            return {"sinyal": "YOK", "sebepler": ["MFI hesaplaması sonrası veri kalmadı."], "value": None}

        # --- Verileri Al ---
        last_mfi = df[f'MFI_{mfi_period}'].iloc[-1]
        prev_mfi = df[f'MFI_{mfi_period}'].iloc[-2]

        # ⭐ YENİ: Sayısal değeri yapay zeka için hazırla
        numeric_value = round(last_mfi, 2)


        # --- Sinyal Mantığı (DEĞİŞTİRİLMEDİ) ---
        signal = "YOK"
        reason = f"MFI ({numeric_value:.1f}) orta bölgede, belirgin bir sinyal yok."

        # YÜKSELİŞ Sinyali: MFI, aşırı satım bölgesinden yukarı çıkarsa
        if prev_mfi < oversold_level and last_mfi > oversold_level:
            signal = "YUKARI"
            reason = f"MFI ({numeric_value:.1f}) aşırı satım bölgesinden ({oversold_level}) çıktı."

        # DÜŞÜŞ Sinyali: MFI, aşırı alım bölgesinden aşağı inerse
        elif prev_mfi > overbought_level and last_mfi < overbought_level:
            signal = "AŞAĞI"
            reason = f"MFI ({numeric_value:.1f}) aşırı alım bölgesinden ({overbought_level}) çıktı."

        # --- ⭐ GÜNCELLENMİŞ ÇIKTI ---
        return {
            "sinyal": signal,
            "sebepler": [reason],
            "value": numeric_value # Sayısal değer olarak o anki MFI değerini ekliyoruz
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"MFI sinyali hesaplanırken bir hata oluştu: {e}"],
            "value": None
        }