import sys
import os
import json
from datetime import datetime

def log_to_file(message):
    log_path = os.path.join(os.path.dirname(__file__), "py_error.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")

def get_indicators():
    klasor = os.path.join(os.path.dirname(__file__), "scalping_indicator")
    liste = []
    for dosya in os.listdir(klasor):
        if dosya.endswith(".py") and not dosya.startswith("__"):
            liste.append(dosya.replace(".py", ""))
    return liste

def get_indicator_list():
    try:
        print(json.dumps(get_indicators(), ensure_ascii=False))
    except Exception as e:
        error_msg = f"İndikatör listesi alınamadı: {str(e)}"
        print(json.dumps({"error": error_msg}))
        log_to_file(error_msg)

if __name__ == "__main__":
    try:
        get_indicator_list()
    except Exception as e:
        error_msg = f"get_indicator_list ana hata: {e}"
        print(json.dumps({"error": error_msg}))
        log_to_file(error_msg)
