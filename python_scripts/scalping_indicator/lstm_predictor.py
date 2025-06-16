import pandas as pd
import numpy as np
from keras.models import load_model
import os
import joblib
from pathlib import Path
import pandas_ta as ta

# Hataları gizlemek için (isteğe bağlı)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
tf.get_logger().setLevel('ERROR')


# Fonksiyon adı ve parametreleri, ana script ile uyumlu olacak şekilde düzenlendi.
def calculate(df, symbol, interval, mode):
    """
    Verilen DataFrame için LSTM modelini kullanarak yön tahmini yapar.
    """
    try:
        # --- 1. Yolları Tanımla ---
        script_path = Path(__file__).resolve()
        
        model_dir = script_path.parent / '_train_lstm_model' / 'model_checkpoints'
        model_path = model_dir / 'lstm_model_v3.keras'
        scaler_path = model_dir / 'lstm_v3_scaler.gz'

        # --- 2. Model ve Scaler'ı Yükle ---
        if not model_path.exists() or not scaler_path.exists():
            return "YOK", "[HATA DETAYI]: Model veya Scaler dosyası bulunamadı."
            
        model = load_model(str(model_path))
        scaler = joblib.load(str(scaler_path))

        # --- 3. Veriyi Hazırla (Özellikleri Hesapla) ---
        seq_len = 60 # Eğitimdeki sequence length ile aynı olmalı

        # Eğitimde kullandığımız 5 ana özelliği ham veriden hesapla
        df.ta.rsi(length=14, append=True)
        df.ta.mfi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.atr(length=14, append=True)
        df.ta.ema(length=50, append=True)
        df['atr_percent'] = (df['ATRr_14'] / df['close']) * 100
        # DÜZELTME: Yazım hatası düzeltildi.
        df['ema_percent_diff'] = ((df['close'] - df['EMA_50']) / df['EMA_50']) * 100
        df.dropna(inplace=True)

        # Eğitimdekiyle birebir aynı kolon isimlerini ve sırasını kullan
        feature_columns = ['RSI_14', 'MFI_14', 'MACDh_12_26_9', 'atr_percent', 'ema_percent_diff']
        
        if len(df) < seq_len:
            return "YOK", f"[HATA DETAYI]: Tahmin için yeterli veri yok ({len(df)}/{seq_len})."

        # Tahmin için son 'seq_len' kadar veriyi al
        features_to_predict = df[feature_columns].tail(seq_len).values

        # --- 4. Veriyi Ölçekle ve Şekillendir ---
        # Veriyi, eğitimde kullanılan scaler ile ölçekle
        scaled_features = scaler.transform(features_to_predict)
        
        # Ölçeklenmiş veriyi LSTM'in beklediği 3D formata çevir: (1, 60, 5)
        X_pred = np.reshape(scaled_features, (1, seq_len, len(feature_columns)))

        # --- 5. Tahmin Yap ---
        prediction_probability = model.predict(X_pred, verbose=0)[0][0]

        # --- 6. Sonucu Yorumla ---
        if prediction_probability > 0.55: # Yükseliş ihtimali %55'ten fazlaysa
            signal = "YUKARI"
        elif prediction_probability < 0.45: # Düşüş ihtimali %55'ten fazlaysa (1 - 0.45)
            signal = "AŞAĞI"
        else:
            signal = "KARARSIZ"
        
        detail = f"Tahmin Olasılığı: {prediction_probability:.2%}"

        return signal, detail

    except Exception as e:
        # Hata ayıklama için hatanın tamamını yazdır
        import traceback
        error_details = f"[HATA DETAYI - lstm_predictor]: {e}\n{traceback.format_exc()}"
        return "HATA", error_details