# run_feature_analysis.py
# Görevi: Kaydedilmiş ham verileri okumak, indikatörleri hesaplamak ve özellik önemi analizi yapmak.

import pandas as pd
import pandas_ta as ta
import lightgbm as lgb
from sklearn.model_selection import train_test_split
import os

def generate_features_and_target(df):
    if df.empty:
        return df
    
    # 5 çekirdek indikatörün sayısal değerlerini hesapla 
    df.ta.rsi(length=14, append=True)
    df.ta.mfi(length=14, append=True)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    df.ta.atr(length=14, append=True)
    df.ta.ema(length=50, append=True)
    
    # İndikatörlerden yeni özellikler türet 
    df['atr_percent'] = (df[f'ATRr_14'] / df['close']) * 100
    df['ema_percent_diff'] = ((df['close'] - df[f'EMA_50']) / df[f'EMA_50']) * 100
    
    # Hedef değişkeni oluştur: bir sonraki mum yükseldi mi (1) yoksa düşüş mü (0)
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    
    df.dropna(inplace=True)
    
    feature_columns = [f'RSI_14', f'MFI_14', f'MACDh_12_26_9', 'atr_percent', 'ema_percent_diff']
    
    if not all(col in df.columns for col in feature_columns):
        print("HATA: Gerekli özellik kolonlarından bazıları oluşturulamadı.")
        return pd.DataFrame()

    return df[feature_columns + ['target']]

def analyze_feature_importance(df):
    if df.empty:
        print("Analiz edilecek veri bulunamadı.")
        return

    print("\n" + "="*50)
    print("ÖZELLİK ÖNEMİ ANALİZİ BAŞLATILIYOR")
    print("="*50)

    timeframes = df['interval'].unique()
    for tf in sorted(timeframes):
        print(f"\n--- ZAMAN DİLİMİ: {tf} ---")
        tf_df = df[df['interval'] == tf]
        if len(tf_df) < 100:
            print(f"Yetersiz veri ({len(tf_df)} satır), bu zaman dilimi atlanıyor.")
            continue
            
        X = tf_df.drop(columns=['target', 'symbol', 'interval'])
        y = tf_df['target']
        
        # Veri setini eğitim ve test olarak ayır 
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # LightGBM modeli ile özellik önemini analiz et 
        model = lgb.LGBMClassifier(random_state=42)
        model.fit(X_train, y_train)
        
        accuracy = model.score(X_test, y_test)
        print(f"Model Doğruluğu (Accuracy): {accuracy:.2%}")
        
        importance_dict = dict(zip(X.columns, model.feature_importances_))
        sorted_importances = sorted(importance_dict.items(), key=lambda item: item[1], reverse=True)
        
        print("Özellik Önem Skorları (En Yüksekten Düşüğe):")
        for feature, importance in sorted_importances:
            print(f"  - {feature}: {importance}")
            
    print("\n" + "="*50)
    print("TÜM ANALİZLER TAMAMLANDI")
    print("="*50)


if __name__ == "__main__":
    # GÜNCELLEME: data_collector.py ile uyumlu hale getirilmiş coin ve zaman dilimi listeleri
    COIN_LIST = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "AVAXUSDT", "ADAUSDT", 
        "XRPUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "ARBUSDT", "DOGEUSDT"
    ]
    TIME_FRAMES = ["1m", "3m", "5m", "15m", "1h", "4h", "1d", "1w"]
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    input_dir = os.path.join(project_root, 'data', 'raw_price_data')
    output_path = os.path.join(project_root, 'data', 'feature_data_for_training.csv')

    all_feature_dfs = []

    print("Kaydedilmiş ham veriler okunuyor ve işleniyor...")
    for coin in COIN_LIST:
        for tf in TIME_FRAMES:
            file_path = os.path.join(input_dir, f"{coin}-{tf}.csv")
            if not os.path.exists(file_path):
                print(f"UYARI: Ham veri dosyası '{file_path}' bulunamadı, atlanıyor.")
                continue
            
            raw_df = pd.read_csv(file_path, index_col='time', parse_dates=True)
            
            feature_df = generate_features_and_target(raw_df.copy()).copy()
            if not feature_df.empty:
                feature_df['symbol'] = coin
                feature_df['interval'] = tf
                all_feature_dfs.append(feature_df)

    if all_feature_dfs:
        master_df = pd.concat(all_feature_dfs, ignore_index=True)
        print(f"\nTüm veriler birleştirildi. Toplam satır sayısı: {len(master_df)}")
        
        print(f"İşlenmiş veri seti '{output_path}' dosyasına kaydediliyor...")
        master_df.to_csv(output_path, index=False) # 
        print("Kaydetme işlemi tamamlandı.")
        
        analyze_feature_importance(master_df) # 
    else:
        print("Analiz edilecek hiç veri bulunamadı. Lütfen önce `data_collector.py`'ı çalıştırın.")