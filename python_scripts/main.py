import sys
import os
import json
import requests
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='ignore')

def log_to_file(message):
    log_path = os.path.join(os.path.dirname(__file__), "py_error.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")

def get_binance_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    try:
        # Önce mevcut dosyayı kontrol et
        path = os.path.join("resources", "symbols")
        file_path = os.path.join(path, "binance_symbols.json")
        
        # Eğer dosya varsa ve 1 saatten daha yeni ise, yeniden indirme
        if os.path.exists(file_path):
            file_time = os.path.getmtime(file_path)
            if (datetime.now().timestamp() - file_time) < 3600:  # 1 saat = 3600 saniye
                with open(file_path, "r", encoding="utf-8") as f:
                    symbols = json.load(f)
                print(json.dumps({"success": f"Mevcut {len(symbols)} sembol kullanıldı."}))
                return

        # Dosya yoksa veya eskiyse yeni liste indir
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        symbols = [
            item['symbol']
            for item in data['symbols']
            if item['quoteAsset'] == 'USDT' and item['status'] == 'TRADING'
        ]

        os.makedirs(path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(symbols, f, indent=2)

        print(json.dumps({"success": f"{len(symbols)} sembol kaydedildi."}))
    except Exception as e:
        error_msg = f"Binance sembolleri alınamadı: {e}"
        print(json.dumps({"error": error_msg}))
        log_to_file(error_msg)

def main():
    try:
        get_binance_symbols()
    except Exception as e:
        error_msg = f"main.py get_binance_symbols hata: {e}"
        print(json.dumps({"error": error_msg}))
        log_to_file(error_msg)

if __name__ == "__main__":
    main()
