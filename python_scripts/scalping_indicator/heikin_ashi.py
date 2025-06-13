# python_scripts/scalping_indicator/heikin_ashi.py

import pandas as pd
import pandas_ta as ta

def calculate(df, symbol, interval):
    """
    Heikin-Ashi sinyallerini, bir EMA trend filtresinden geçirerek daha güvenilir
    ve akıllı hale getiren versiyon.
    """
    if df is None or len(df) < 50: # EMA periyodu kadar veri olmalı
        return {"sinyal": "YOK", "sebepler": ["Yeterli veri yok (en az 50 mum)."]}

    try:
        # --- MANUEL HEIKIN-ASHI HESAPLAMASI ---
        ha_df = df.copy()
        ha_df['HA_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
        ha_df.at[ha_df.index[0], 'HA_open'] = (df['open'].iloc[0] + df['close'].iloc[0]) / 2
        for i in range(1, len(ha_df)):
            ha_df.at[ha_df.index[i], 'HA_open'] = (ha_df.at[ha_df.index[i-1], 'HA_open'] + ha_df.at[ha_df.index[i-1], 'HA_close']) / 2
        ha_df['HA_high'] = ha_df[['HA_open', 'HA_close', 'high']].max(axis=1)
        ha_df['HA_low'] = ha_df[['HA_open', 'HA_close', 'low']].min(axis=1)

        # --- YENİ: TREND FİLTRESİ İÇİN EMA HESAPLAMASI ---
        ema_period = 50
        ha_df.ta.ema(length=ema_period, append=True)

        # Tüm hesaplamalardan sonra boş satırları temizle
        ha_df.dropna(inplace=True)
        if ha_df.empty:
            return {"sinyal": "YOK", "sebepler": ["İndikatör hesaplamaları sonrası veri kalmadı."]}

        # --- Gerekli Verileri Al ---
        last_candle = ha_df.iloc[-1]
        ha_open = last_candle['HA_open']
        ha_close = last_candle['HA_close']
        ha_high = last_candle['HA_high']
        ha_low = last_candle['HA_low']
        last_close_price = last_candle['close'] # Gerçek kapanış fiyatı
        last_ema = last_candle[f'EMA_{ema_period}']

        signal = "NÖTR"
        reason = "Ana trend ile uyumlu bir HA sinyali yok."

        # --- Sinyal Mantığı (EMA FİLTRELİ) ---
        
        # 1. Heikin-Ashi Yükseliş Sinyali (Yeşil Mum)
        if ha_close > ha_open:
            # FİLTRE: Fiyat, ana trendin (EMA) de üzerinde mi?
            if last_close_price > last_ema:
                if ha_open == ha_low:
                    signal = "GÜÇLÜ AL"
                    reason = "Güçlü HA Yükseliş + Ana Trend Onayı."
                else:
                    signal = "AL"
                    reason = "HA Yükseliş + Ana Trend Onayı."
            else:
                reason = f"HA 'AL' sinyali verdi ama fiyat EMA({ema_period}) altında. Sinyal filtrelendi."

        # 2. Heikin-Ashi Düşüş Sinyali (Kırmızı Mum)
        elif ha_close < ha_open:
            # FİLTRE: Fiyat, ana trendin (EMA) de altında mı?
            if last_close_price < last_ema:
                if ha_open == ha_high:
                    signal = "GÜÇLÜ SAT"
                    reason = "Güçlü HA Düşüş + Ana Trend Onayı."
                else:
                    signal = "SAT"
                    reason = "HA Düşüş + Ana Trend Onayı."
            else:
                reason = f"HA 'SAT' sinyali verdi ama fiyat EMA({ema_period}) üstünde. Sinyal filtrelendi."
        else: # HA Doji ise
            reason = "Kararsız piyasa (HA Doji)."
            
        return {
            "sinyal": signal,
            "sebepler": [reason]
        }

    except Exception as e:
        return {
            "sinyal": "HATA",
            "sebepler": [f"Heikin Ashi (filtrelenmiş) hesaplanırken bir hata oluştu: {e}"]
        }