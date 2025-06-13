# python_scripts/_train_lstm_model/_train_lstm_model.py

import pandas as pd
import numpy as np
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Dropout
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, CSVLogger
from sklearn.preprocessing import MinMaxScaler
import os
from pathlib import Path

def prepare_sequences(df, seq_len=60):
    """Veriyi LSTM modelinin anlayacağı sıralı formatına dönüştürür."""
    features = df.drop('target', axis=1).values
    target = df['target'].values

    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(features)
    
    X, y = [], []
    for i in range(len(scaled_features) - seq_len):
        X.append(scaled_features[i:i+seq_len])
        y.append(target[i+seq_len])
        
    return np.array(X), np.array(y), scaler

def build_classification_model(input_shape):
    """Yön tahmini (sınıflandırma) için bir LSTM modeli oluşturur."""
    model = Sequential([
        LSTM(100, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train_and_save_model():
    """Veriyi yükler, hazırlar, modeli eğitir ve kaydeder."""
    try:
        # --- 1. Veri ve Kayıt Yollarını Ayarla ---
        script_path = Path(__file__).resolve()
        
        # KESİN DÜZELTME: Proje kök dizinine ulaşmak için 3 seviye yukarı çık
        # _train_lstm_model -> scalping_indicator -> python_scripts -> sentio-app
        project_root = script_path.parents[3] 
        
        data_path = project_root / 'data' / 'feature_data_for_training.csv'
        
        checkpoint_dir = script_path.parent / "model_checkpoints"
        checkpoint_dir.mkdir(exist_ok=True) 
        checkpoint_path = checkpoint_dir / "lstm_model_v3.h5"
        log_path = checkpoint_dir / "training_log.csv"

        print(f"Eğitim verisi aranıyor: {data_path}")
        if not data_path.exists():
            print(f"HATA: Eğitim verisi dosyası bulunamadı!")
            return

        print(f"Eğitim verisi okunuyor: '{data_path}'")
        df = pd.read_csv(data_path)
        
    except Exception as e:
        print(f"Dosya okunurken veya yol hesaplanırken bir hata oluştu: {e}")
        return
    
    df_features = df.drop(columns=['symbol', 'interval'])

    # --- 2. Veriyi Hazırla ---
    sequence_length = 60
    X, y, scaler = prepare_sequences(df_features, seq_len=sequence_length)
    
    if X.size == 0:
        print("HATA: Eğitim için yeterli sequence oluşturulamadı.")
        return

    print(f"Veri hazırlandı. X şekli: {X.shape}, y şekli: {y.shape}")

    # --- 3. Modeli Yükle veya Oluştur ---
    if checkpoint_path.exists():
        print(f"\nMEVCUT MODEL BULUNDU. '{checkpoint_path}' üzerinden eğitime devam edilecek...")
        model = load_model(str(checkpoint_path)) # Path'i string'e çevirerek yükle
    else:
        print("\nYeni model oluşturuluyor...")
        model = build_classification_model(input_shape=(X.shape[1], X.shape[2]))
        
    model.summary() 

    # --- 4. Callback'leri Ayarla ---
    checkpoint_callback = ModelCheckpoint(
        filepath=str(checkpoint_path),
        monitor='loss',
        save_best_only=True,
        mode='min',
        verbose=1
    )
    csv_logger = CSVLogger(str(log_path), append=True)
    
    # --- 5. Modeli Eğit ---
    print("\nModel eğitimi başlıyor...")
    model.fit(
        X, y, 
        epochs=20,
        batch_size=64,
        verbose=1,
        callbacks=[checkpoint_callback, csv_logger]
    )

    print(f"\nEğitim tamamlandı veya durduruldu. En iyi model kaydedildi: {checkpoint_path}")

if __name__ == "__main__":
    train_and_save_model()