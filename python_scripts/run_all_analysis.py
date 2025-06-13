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
        # ⭐ DÜZELTME: Zaman damgalarını UTC-aware (saat dilimi bilgisine sahip) olarak oluşturuyoruz
        df["time"] = pd.to_datetime(df["time"], unit='ms', utc=True)
        df.set_index("time", inplace=True)
        return df[["open", "high", "low", "close", "volume"]]
    except Exception as e:
        log_to_file(f"[HATA] DataFrame dönüşüm hatası: {e}")
        return None

def save_prediction_log(log_data):
    try:
        log_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "prediction_log.json")
        )
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        log_entries = []
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    log_entries = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                log_entries = []

        log_entries.append(log_data)

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_entries, f, indent=2, ensure_ascii=False)

    except Exception as e:
        log_to_file(f"[ERROR] Tahmin günlüğüne kaydetme hatası: {e}")

def run_all_analysis(symbol, interval):
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
                raise AttributeError(f"calculate fonksiyonu eksik: {module_name}")
            
            sig = inspect.signature(module.calculate)
            num_params = len(sig.parameters)

            if num_params == 3:
                result = module.calculate(df.copy(), symbol=symbol, interval=interval)
            elif num_params == 1:
                result = module.calculate(df.copy())
            else:
                raise ValueError(f"{module_name}.calculate() beklenmedik sayıda parametreye sahip: {num_params}")

            if not isinstance(result, dict):
                raise ValueError(f"{module_name} calculate() sözlük dönmeli")

            signal_result = result.get('sinyal', 'YOK')
            
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
                print(f"    └── [HATA DETAYI - {module_name}]: {error_reasons[0]}", file=sys.stderr)

        except Exception as e:
            log_to_file(f"{module_name} HATA: {e}")
            traceback.print_exc(file=sys.stderr)
    
    return df, results

if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Eksik parametreler"}))
            sys.exit(1)

        symbol = sys.argv[1]
        interval = sys.argv[2]
        
        print(f"[INFO] Analiz başlatılıyor: {symbol} - {interval}", file=sys.stderr)
        df, results = run_all_analysis(symbol, interval)

        final = {"analysis_results": results}
        
        lstm_result = next((r for r in results if r["indikator"] == "lstm_predictor"), None)
        onay_modeli_result = next((r for r in results if r["indikator"] == "crypto_prediction_model"), None)
        
        # --- ⭐⭐⭐ DÜZELTME BURADA ⭐⭐⭐ ---
        # Fonksiyona eksik olan 'interval' parametresini ekliyoruz.
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
        print(f"    └── Pozitif Sinyaller: {final_verdict_data.get('positive_signals')}, Negatif Sinyaller: {final_verdict_data.get('negative_signals')}", file=sys.stderr)
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

    except Exception as e:
        msg = f"CLI hatası: {e}"
        log_to_file(msg)
        print(json.dumps({"error": msg}))
        sys.stdout.flush()