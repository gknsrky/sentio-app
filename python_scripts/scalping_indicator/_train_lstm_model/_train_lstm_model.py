# python_scripts/_train_lstm_model/_train_lstm_model.py

import pandas as pd
import numpy as np
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Dropout
from keras.optimizers import Adam
# GÜNCELLEME: Yeni callback'i import et
from keras.callbacks import ModelCheckpoint, CSVLogger, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler
import os
from pathlib import Path
import joblib

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
    
    # GÜNCELLEME: Optimizer'a gradient kırpma (clipnorm) eklendi.
    optimizer = Adam(learning_rate=0.001, clipnorm=1.0)
    
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train_and_save_model():
    """Veriyi yükler, hazırlar, modeli eğitir ve kaydeder."""
    try:
        script_path = Path(__file__).resolve()
        project_root = script_path.parents[3] 
        data_path = project_root / 'data' / 'feature_data_for_training.csv'
        
        checkpoint_dir = script_path.parent / "model_checkpoints"
        checkpoint_dir.mkdir(exist_ok=True) 
        checkpoint_path = checkpoint_dir / "lstm_model_v3.keras" # .keras formatını kullanmaya devam ediyoruz
        log_path = checkpoint_dir / "training_log.csv"
        scaler_path = checkpoint_dir / "lstm_v3_scaler.gz"

        print(f"Eğitim verisi okunuyor: '{data_path}'")
        df = pd.read_csv(data_path)
        
    except Exception as e:
        print(f"Dosya okunurken veya yol hesaplanırken bir hata oluştu: {e}")
        return
    
    df_features = df.drop(columns=['symbol', 'interval'])
    sequence_length = 60
    X, y, scaler = prepare_sequences(df_features, seq_len=sequence_length)
    
    if X.size == 0:
        print("HATA: Eğitim için yeterli sequence oluşturulamadı.")
        return

    print(f"Veri hazırlandı. X şekli: {X.shape}, y şekli: {y.shape}")
    print(f"Scaler objesi kaydediliyor -> {scaler_path}")
    joblib.dump(scaler, str(scaler_path))
    
    if checkpoint_path.exists():
        print(f"\nMEVCUT MODEL BULUNDU. '{checkpoint_path}' üzerinden eğitime devam edilecek...")
        model = load_model(str(checkpoint_path))
    else:
        print("\nYeni model oluşturuluyor...")
        model = build_classification_model(input_shape=(X.shape[1], X.shape[2]))
        
    model.summary() 

    # --- Callback'leri Ayarla ---
    checkpoint_callback = ModelCheckpoint(
        filepath=str(checkpoint_path),
        monitor='loss',
        save_best_only=True,
        mode='min',
        verbose=1
    )
    csv_logger = CSVLogger(str(log_path), append=True)
    
    # GÜNCELLEME: Dinamik öğrenme oranı için yeni callback
    reduce_lr_callback = ReduceLROnPlateau(
        monitor='loss',
        factor=0.2,    # Öğrenme oranını 5'te 1'ine düşür
        patience=3,    # 3 epoch boyunca loss iyileşmezse düşür
        min_lr=0.00001, # Öğrenme oranının inebileceği minimum seviye
        verbose=1
    )
    
    # --- Modeli Eğit ---
    print("\nModel eğitimi başlıyor...")
    model.fit(
        X, y, 
        epochs=20,
        batch_size=64,
        verbose=1,
        # GÜNCELLEME: Artık 3 callback kullanıyoruz
        callbacks=[checkpoint_callback, csv_logger, reduce_lr_callback] 
    )

    print(f"\nEğitim tamamlandı veya durduruldu. En iyi model kaydedildi: {checkpoint_path}")

if __name__ == "__main__":
    train_and_save_model()