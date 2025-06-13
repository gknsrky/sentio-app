import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "lstm_model.h5")

def calculate(df):
    if df is None or len(df) < 50:
        return {
            "sinyal": "YOK",
            "sebepler": ["Yeterli veri yok (en az 50 mum gerek)."]
        }

    try:
        scaler = MinMaxScaler()
        scaled_close = scaler.fit_transform(df["close"].values.reshape(-1, 1))

        X = np.array([scaled_close[-50:]]).reshape((1, 50, 1))

        model = load_model(MODEL_PATH, compile=False)
        predicted_scaled = model.predict(X, verbose=0)[0][0]
        predicted_price = scaler.inverse_transform([[predicted_scaled]])[0][0]

        last_close = df["close"].iloc[-1]
        direction = "YUKARI" if predicted_price > last_close else "AŞAĞI"
        confidence = round(abs(predicted_price - last_close) / last_close * 100, 2)

        # ⭐️ DEĞİŞİKLİK: Zamanla ilgili satırlar kaldırıldı.
        return {
            "sinyal": direction,
            "sebepler": [f"AI confidence: %{confidence}", f"Tahmini fiyat: {predicted_price:.2f}"],
            "tahmini_fiyat": round(predicted_price, 2)
        }

    except Exception as e:
        return {
            "sinyal": "YOK",
            "sebepler": [f"Model yüklenemedi veya hata oluştu: {e}"]
        }