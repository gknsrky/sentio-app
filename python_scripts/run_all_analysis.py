import os
import sys
import json
import importlib.util
import traceback
import pandas as pd
import requests
from datetime import datetime
import inspect
from final_decision_maker import get_final_verdict

# stdout ve stderr UTF-8
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def log_to_file(message):
    log_path = os.path.join(os.path.dirname(__file__), "py_error.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")

def load_data(symbol, interval, limit=1000):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        # DÜZELTME 1: Güvenli SSL bağlantısı için 'verify=False' kaldırıldı.
        # Sistemdeki sertifikaların doğru kullanılmasını sağlıyoruz.
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        log_to_file(f"[HATA] Binance API hatası: {e}")
        return None

    try:
        df = pd.DataFrame(data, columns=[
            "time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades", "tbbav", "tbqav", "ignore"
        ])
        df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
        df["time"] = pd.to_datetime(df["time"], unit='ms', utc=True)
        df.set_index("time", inplace=True)
        return df[["open", "high", "low", "close", "volume"]]
    except Exception as e:
        log_to_file(f"[HATA] DataFrame dönüşüm hatası: {e}")
        return None

def save_prediction_log(log_data):
    # Bu fonksiyona dokunulmadı.
    try:
        log_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "prediction_log.json")
        )
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        log_entries = []
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    # Dosyanın boş olup olmadığını kontrol et
                    content = f.read()
                    if content.strip():
                        f.seek(0)
                        log_entries = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                log_entries = []

        log_entries.append(log_data)

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_entries, f, indent=2, ensure_ascii=False)

    except Exception as e:
        log_to_file(f"[ERROR] Tahmin günlüğüne kaydetme hatası: {e}")

def run_all_analysis(symbol, interval, mode): # DÜZELTME: 'mode' parametresi eklendi
    df = load_data(symbol, interval)
    if df is None:
        raise Exception("Veri alınamadı")

    indicators_dir = os.path.join(os.path.dirname(__file__), "scalping_indicator")
    results = []

    for file in os.listdir(indicators_dir):
        if not file.endswith(".py") or file.startswith("_"):
            continue

        module_name = file[:-3]
        file_path = os.path.join(indicators_dir, file)
        print(f"[INFO] Yükleniyor: {module_name}", file=sys.stderr)

        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if not hasattr(module, "calculate"):
                continue
            
            # --- DÜZELTME 2: AKILLI ve ESNEK FONKSİYON ÇAĞIRMA MANTIĞI ---
            sig = inspect.signature(module.calculate)
            params = sig.parameters
            
            # Çağrılacak argümanları bir sözlükte toplayalım
            call_args = {'df': df.copy()}
            if 'symbol' in params:
                call_args['symbol'] = symbol
            if 'interval' in params:
                call_args['interval'] = interval
            if 'mode' in params:
                call_args['mode'] = mode

            # Fonksiyonu, sadece kabul ettiği parametrelerle çağır
            raw_result = module.calculate(**call_args)

            # Farklı indikatörlerden gelebilecek farklı dönüş tiplerini yönetelim
            result = {}
            if isinstance(raw_result, dict):
                result = raw_result # Eğer sözlük döndürüyorsa direkt kullan
            elif isinstance(raw_result, tuple) and len(raw_result) == 2:
                # Eğer (sinyal, detay) şeklinde tuple döndürüyorsa sözlüğe çevir
                result = {'sinyal': raw_result[0], 'sebepler': [raw_result[1]] if raw_result[1] else []}
            else:
                # Eğer sadece string bir sinyal döndürüyorsa sözlüğe çevir
                result = {'sinyal': str(raw_result), 'sebepler': []}
            # --- DÜZELTME BİTİŞİ ---
            
            signal_result = result.get('sinyal', 'YOK')
            
            # Senin orijinal 'results.append' satırın korunuyor
            results.append({
                "indikator": module_name,
                "sinyal": signal_result,
                "sebepler": result.get("sebepler", []),
                "tahmini_fiyat": result.get("tahmini_fiyat"),
                "data": result.get("data")
            })

            print(f"[OK] Tamamlandı: {module_name} -> {signal_result}", file=sys.stderr)

            if signal_result == "HATA":
                error_reasons = result.get('sebepler', ['Sebep bulunamadı.'])
                print(f"     └── [HATA DETAYI - {module_name}]: {error_reasons[0]}", file=sys.stderr)

        except Exception as e:
            log_to_file(f"{module_name} HATA: {e}")
            traceback.print_exc(file=sys.stderr)
    
    return df, results

if __name__ == "__main__":
    # Bu __main__ bloğuna dokunulmadı, sadece mode parametresi eklendi.
    try:
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Eksik parametreler: python run_all_analysis.py <symbol> <interval> <mode>"}))
            sys.exit(1)

        symbol = sys.argv[1]
        interval = sys.argv[2]
        mode = sys.argv[3]
        
        print(f"[INFO] Analiz başlatılıyor: {symbol} - {interval}", file=sys.stderr)
        df, results = run_all_analysis(symbol, interval, mode)

        final = {"analysis_results": results}
        
        lstm_result = next((r for r in results if r["indikator"] == "lstm_predictor"), None)
        onay_modeli_result = next((r for r in results if r["indikator"] == "crypto_prediction_model"), None)
        
        final_verdict_data = get_final_verdict(results, interval)
        
        if lstm_result:
            final["sinyal"] = lstm_result.get("sinyal")
            final["mumKapanis"] = lstm_result.get("tahmini_fiyat")
        
        last_open_price = df["open"].iloc[-1]
        final["mumAcilis"] = last_open_price
        last_candle_open_time = df.index[-1]
        interval_duration = df.index[-1] - df.index[-2]
        last_candle_close_time = last_candle_open_time + interval_duration
        final["openTime"] = last_candle_open_time.isoformat()
        final["closeTime"] = last_candle_close_time.isoformat()
        
        if onay_modeli_result:
            final["onay_sinyali"] = {"sinyal": onay_modeli_result.get("sinyal"), "sebep": onay_modeli_result.get("sebepler", [""])[0]}
        
        liquidity_result = next((r for r in results if r["indikator"] == "liquidity_zones"), None)
        if liquidity_result and liquidity_result.get("data"):
            final["liquidity_levels"] = {"upper": liquidity_result["data"].get("upper_liquidity_zone"), "lower": liquidity_result["data"].get("lower_liquidity_zone")}
        
        final["final_verdict"] = final_verdict_data

        prediction_log_entry = {
            "prediction_id": f"{symbol}-{interval}-{int(last_candle_close_time.timestamp())}",
            "analysis_timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "interval": interval,
            "target_candle_open_time": last_candle_open_time.isoformat(),
            "target_candle_open_price": last_open_price,
            "target_candle_close_time": last_candle_close_time.isoformat(),
            "status": "PENDING",
            "predictions_at_analysis": {
                "lstm_predicted_price": lstm_result.get("tahmini_fiyat") if lstm_result else None,
                "lstm_signal": lstm_result.get("sinyal") if lstm_result else "YOK",
                "confirmation_signal": onay_modeli_result.get("sinyal") if onay_modeli_result else "YOK",
                "final_verdict": final_verdict_data,
                "all_indicator_signals": {res["indikator"]: res["sinyal"] for res in results}
            },
            "verification_results": {}
        }
        save_prediction_log(prediction_log_entry)
        
        print("-" * 40, file=sys.stderr)
        print(f"[NİHAİ KARAR] -> SKOR: {final_verdict_data.get('score')}, TAVSİYE: {final_verdict_data.get('verdict')}", file=sys.stderr)
        print(f"     └── Pozitif Sinyaller: {final_verdict_data.get('positive_signals')}, Negatif Sinyaller: {final_verdict_data.get('negative_signals')}", file=sys.stderr)
        print("-" * 40, file=sys.stderr)

        with open("last_analysis.json", "w", encoding="utf-8") as f:
            json.dump(final, f, ensure_ascii=False, indent=2)

        print(json.dumps(final, ensure_ascii=False))
        sys.stdout.flush()

    except Exception as e:
        msg = f"CLI hatası: {e}"
        log_to_file(msg)
        print(json.dumps({"error": msg}))
        sys.stdout.flush()