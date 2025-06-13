# python_scripts/verify_predictions.py

import os
import sys
import json
from datetime import datetime, timezone
import requests
import pandas as pd

# Proje ana dizinini doğru şekilde bul
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE_PATH = os.path.join(project_root, "data", "prediction_log.json")

def get_actual_candle(symbol, interval, start_time_ms):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&startTime={start_time_ms}&limit=1"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data: return data[0]
        return None
    except Exception as e:
        print(f"[HATA] {symbol} için mum verisi çekilemedi: {e}", file=sys.stderr)
        return None

def verify_predictions():
    if not os.path.exists(LOG_FILE_PATH):
        print("Tahmin günlüğü dosyası (prediction_log.json) bulunamadı.")
        return

    try:
        with open(LOG_FILE_PATH, "r+", encoding="utf-8") as f:
            # Dosyanın boş olup olmadığını kontrol et
            content = f.read()
            if not content:
                print("Tahmin günlüğü boş, doğrulanacak bir şey yok.")
                return
            f.seek(0)
            log_entries = json.loads(content)
            
            now_utc = datetime.now(timezone.utc)
            verified_count = 0

            for entry in log_entries:
                if entry.get("status") == "PENDING":
                    close_time_from_log = datetime.fromisoformat(entry["target_candle_close_time"])
                    
                    if close_time_from_log.tzinfo is None:
                        close_time_from_log = close_time_from_log.replace(tzinfo=timezone.utc)

                    if now_utc > close_time_from_log:
                        print(f"Doğrulanıyor: {entry['prediction_id']}...")
                        
                        open_time_from_log = datetime.fromisoformat(entry["target_candle_open_time"])
                        if open_time_from_log.tzinfo is None:
                            open_time_from_log = open_time_from_log.replace(tzinfo=timezone.utc)

                        open_time_ms = int(open_time_from_log.timestamp() * 1000)
                        actual_candle_data = get_actual_candle(entry["symbol"], entry["interval"], open_time_ms)
                        
                        if actual_candle_data:
                            actual_close_price = float(actual_candle_data[4])
                            entry["status"] = "VERIFIED"
                            entry["verification_results"]["actual_close_price"] = actual_close_price
                            
                            # MAPE HESAPLAMASI
                            predicted_price = entry["predictions_at_analysis"].get("lstm_predicted_price")
                            if predicted_price is not None and actual_close_price > 0:
                                mape = 100 * (abs(actual_close_price - predicted_price) / actual_close_price)
                                entry["verification_results"]["lstm_price_mape_percent"] = round(mape, 2)
                            
                            real_outcome_up = actual_close_price > entry["target_candle_open_price"]
                            
                            # LSTM SİNYAL BAŞARISI
                            lstm_signal = entry["predictions_at_analysis"].get("lstm_signal")
                            entry["verification_results"]["lstm_signal_success"] = None
                            if lstm_signal in ["YUKARI", "AŞAĞI"]:
                                entry["verification_results"]["lstm_signal_success"] = (lstm_signal == "YUKARI") == real_outcome_up
                            
                            # ⭐ DÜZELTME: NİHAİ KARAR BAŞARISI
                            verdict = entry["predictions_at_analysis"]["final_verdict"].get("verdict")
                            entry["verification_results"]["final_verdict_success"] = None # Varsayılan olarak None ata
                            if verdict and "ALIM" in verdict:
                                entry["verification_results"]["final_verdict_success"] = real_outcome_up
                            elif verdict and "SATIM" in verdict:
                                entry["verification_results"]["final_verdict_success"] = not real_outcome_up
                            
                            verified_count += 1
                        else:
                            print(f"    └── Veri alınamadı, bir sonraki kontrole bırakıldı.")

            f.seek(0)
            json.dump(log_entries, f, indent=2, ensure_ascii=False)
            f.truncate()
            
            print(f"\nİşlem tamamlandı. {verified_count} adet yeni tahmin doğrulandı.")

    except json.JSONDecodeError:
        print("HATA: prediction_log.json dosyası bozuk veya boş. Lütfen dosyayı silin, uygulama yeniden oluşturacaktır.")
    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}")

if __name__ == "__main__":
    verify_predictions()