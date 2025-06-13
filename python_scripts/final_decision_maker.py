# python_scripts/final_decision_maker.py

# Zaman dilimine duyarlı, veriye dayalı ağırlık haritası
TIME_SENSITIVE_WEIGHT_MAP = {
    "15m": {
        "macd_signal":    {"YUKARI": 3, "AŞAĞI": -3},
        "atr_signal":     {"VOLATİL": 2, "DURGUN": -1},
        "mfi_signal":     {"YUKARI": 2, "AŞAĞI": -2},
        "ema_signal":     {"YUKARI": 1, "AŞAĞI": -1},
        "rsi_signal":     {"GÜÇLÜ AL": 2, "AL": 1, "SAT": -1, "GÜÇLÜ SAT": -2},
    },
    "1h": {
        "atr_signal":     {"VOLATİL": 3, "DURGUN": -1},
        "mfi_signal":     {"YUKARI": 3, "AŞAĞI": -3},
        "macd_signal":    {"YUKARI": 2, "AŞAĞI": -2},
        "rsi_signal":     {"GÜÇLÜ AL": 2, "AL": 1, "SAT": -1, "GÜÇLÜ SAT": -2},
        "ema_signal":     {"YUKARI": 1, "AŞAĞI": -1},
    },
    "4h": {
        "mfi_signal":     {"YUKARI": 3, "AŞAĞI": -3},
        "atr_signal":     {"VOLATİL": 3, "DURGUN": -1},
        "rsi_signal":     {"GÜÇLÜ AL": 2, "AL": 1, "SAT": -1, "GÜÇLÜ SAT": -2},
        "macd_signal":    {"YUKARI": 2, "AŞAĞI": -2},
        "ema_signal":     {"YUKARI": 1, "AŞAĞI": -1},
    },
    # 1d ve 1w gibi diğer tüm zaman dilimleri için genel varsayılan set
    "default": {
        "mfi_signal":     {"YUKARI": 3, "AŞAĞI": -3},
        "rsi_signal":     {"GÜÇLÜ AL": 2, "AL": 1, "SAT": -1, "GÜÇLÜ SAT": -2},
        "macd_signal":    {"YUKARI": 2, "AŞAĞI": -2},
        "atr_signal":     {"VOLATİL": 1, "DURGUN": -1},
        "ema_signal":     {"YUKARI": 1, "AŞAĞI": -1},
    }
}

# Çekirdek portföyümüz dışındaki diğer tüm indikatörler için genel harita
# Bu indikatörlere daha az güveniyoruz ve daha düşük puan veriyoruz.
GENERAL_WEIGHT_MAP = {
    "bollinger_bands":          {"YUKARI": 0.5, "AŞAĞI": -0.5},
    "heikin_ashi":              {"GÜÇLÜ AL": 1, "AL": 0.5, "SAT": -0.5, "GÜÇLÜ SAT": -1},
    "keltner_channel":          {"YUKARI": 0.5, "AŞAĞI": -0.5},
    "squeeze_momentum":         {"YUKARI": 1, "AŞAĞI": -1},
    "stochastic_signal":        {"YUKARI": 1, "AŞAĞI": -1},
    "trend_meter":              {"GÜÇLÜ AL": 1, "AL": 0.5, "SAT": -0.5, "GÜÇLÜ SAT": -1},
    # Diğerleri varsayılan olarak 0 puan alır
}

def get_final_verdict(results, interval):
    """
    Verilen analiz sonuçlarını ve zaman dilimini kullanarak nihai bir karar ve skor üretir.
    """
    if not results:
        return {"score": 0, "verdict": "VERİ YOK", "positive_signals": 0, "negative_signals": 0, "confidence_percent": 0}

    # Analiz yapılan zaman aralığına göre doğru ağırlık haritasını seç
    core_weights = TIME_SENSITIVE_WEIGHT_MAP.get(interval, TIME_SENSITIVE_WEIGHT_MAP["default"])

    score = 0
    positive_signals = 0
    negative_signals = 0
    
    # LSTM gibi AI modellerini toplam indikatör sayısından çıkarabiliriz.
    # Şimdilik hepsi dahil ediliyor.
    total_indicators = len(results)

    for result in results:
        indicator_name = result.get("indikator")
        signal = result.get("sinyal")

        # Puanı belirle: Önce çekirdek haritaya bak, orada yoksa genel haritaya bak.
        indicator_scores = core_weights.get(indicator_name)
        if indicator_scores is None:
            indicator_scores = GENERAL_WEIGHT_MAP.get(indicator_name, {})

        points = indicator_scores.get(signal, 0)
        
        score += points
        
        if points > 0:
            positive_signals += 1
        elif points < 0:
            negative_signals += 1
            
    total_active_signals = positive_signals + negative_signals

    # Fikir Birliği / Güven Yüzdesi Hesaplaması
    confidence_percent = 0
    if total_indicators > 0:
        # Toplam sinyal üreten indikatörlerin, tüm indikatörlere oranı
        confidence_percent = round((total_active_signals / total_indicators) * 100)

    # Karar eşikleri
    if score >= 5:
        verdict = "GÜÇLÜ ALIM"
    elif score >= 2:
        verdict = "ALIM AĞIRLIKLI"
    elif score <= -5:
        verdict = "GÜÇLÜ SATIM"
    elif score <= -2:
        verdict = "SATIM AĞIRLIKLI"
    else:
        verdict = "KARARSIZ"

    return {
        "score": round(score, 2),
        "verdict": verdict,
        "positive_signals": positive_signals,
        "negative_signals": negative_signals,
        "total_active_signals": total_active_signals,
        "confidence_percent": confidence_percent
    }