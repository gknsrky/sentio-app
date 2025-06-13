// App.jsx
import React, { useState, useEffect, useCallback } from "react";
import AyarlarSayfasi from "./components/AyarlarSayfasi";
import GecmisAnalizler from "./components/GecmisAnalizler";
import CoinSelector from "./components/CoinSelector";
import GrafikBileseni from "./components/GrafikBileseni";

// ⭐ Gerekli: İndikatörler için güzel isimler haritası
const indicatorDisplayNames = {
  atr_signal: "ATR Volatilitesi",
  bollinger_bands: "Bollinger Bantları",
  crypto_prediction_model: "Onay Mekanizması",
  ema_signal: "EMA (50) Trend",
  freqtrade_signal: "Freqtrade Stratejisi",
  heikin_ashi: "Heikin Ashi Trend",
  keltner_channel: "Keltner Kanalı",
  liquidity_zones: "Likidite Avı",
  lstm_predictor: "AI Fiyat Tahmini",
  macd_signal: "MACD Kesişimi",
  mfi_signal: "MFI Para Akışı",
  pivot_points: "Dinamik Destek/Direnç",
  qqe_mod: "QQE Momentum",
  rsi_signal: "RSI Sinyali",
  squeeze_momentum: "Squeeze Momentum",
  stochastic_signal: "Stochastic Sinyali",
  supertrend_signal: "Supertrend",
  top_scalping_indicator: "Scalping Formasyonu",
  trend_meter: "Trend Metresi",
  venky_signals: "VWAP Strateji #1",
  vwap_signal: "VWAP Kırılımı",
  zlsma: "ZLSMA Trend (Hızlı)",
};

// ⭐ Gerekli: Güven yüzdesini renklendirmek için yardımcı fonksiyon
const getConfidenceColor = (percentage) => {
  if (percentage >= 80) return { bg: "bg-green-500", text: "text-white font-bold" };
  if (percentage >= 60) return { bg: "bg-lime-400", text: "text-lime-900 font-bold" };
  if (percentage >= 40) return { bg: "bg-yellow-400", text: "text-yellow-900 font-bold" };
  if (percentage >= 20) return { bg: "bg-orange-500", text: "text-white font-bold" };
  return { bg: "bg-red-600", text: "text-white font-bold" };
};

function App() {
  const [mode, setMode] = useState("scalping");
  const [selectedCoin, setSelectedCoin] = useState("");
  const [selectedTimeframe, setSelectedTimeframe] = useState("1G");
  const [showSettings, setShowSettings] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [selectedExchange, setSelectedExchange] = useState("Binance");
  const [coinList, setCoinList] = useState([]);
  const [indicatorList, setIndicatorList] = useState([]);
  const [aiSignal, setAiSignal] = useState(null);
  const [openPrice, setOpenPrice] = useState(null);
  const [closePrice, setClosePrice] = useState(null);
  const [openTime, setOpenTime] = useState(null);
  const [closeTime, setCloseTime] = useState(null);
  const [statusMessage, setStatusMessage] = useState("Hazır");
  const [upperLiquidity, setUpperLiquidity] = useState(null);
  const [lowerLiquidity, setLowerLiquidity] = useState(null);
  const [finalVerdict, setFinalVerdict] = useState(null);
  const [onaySinyali, setOnaySinyali] = useState(null);
  const [progressPercentage, setProgressPercentage] = useState(0);

  const timeframes = ["1dk", "3dk", "5dk", "15dk", "30dk", "1s", "2s", "4s", "1G", "1Hafta", "1Ay"];

  const timeframeToBinance = {
    "1dk": "1m", "3dk": "3m", "5dk": "5m", "15dk": "15m", "30dk": "30m",
    "1s": "1h", "2s": "2h", "4s": "4h", "1G": "1d", "1Hafta": "1w", "1Ay": "1M"
  };

  const timeframeToTradingView = {
    "1dk": "1", "3dk": "3", "5dk": "5", "15dk": "15", "30dk": "30",
    "1s": "60", "2s": "120", "4s": "240", "1G": "D", "1Hafta": "W", "1Ay": "M"
  };

  const handleAnalyze = useCallback(() => {
    if (!selectedCoin || !timeframeToBinance[selectedTimeframe]) {
      setStatusMessage("Lütfen coin ve zaman aralığı seçin.");
      return;
    }
    setStatusMessage("Analiz yapiliyor...");
    setIndicatorList([]);
    setAiSignal(null); setOpenPrice(null); setClosePrice(null); setOpenTime(null); setCloseTime(null);
    setUpperLiquidity(null); setLowerLiquidity(null);
    setFinalVerdict(null); setOnaySinyali(null);
    setProgressPercentage(0); // Reset progress when starting new analysis

    window.electronAPI?.runAnalysis({
      symbol: selectedCoin,
      interval: timeframeToBinance[selectedTimeframe],
      mode
    }).then((res) => {
      setIndicatorList(Array.isArray(res.analysis_results) ? res.analysis_results : []);
      setAiSignal(res.sinyal || null);
      setOpenPrice(res.mumAcilis || null);
      setClosePrice(res.mumKapanis || null);
      setOpenTime(res.openTime || null);
      setCloseTime(res.closeTime || null);
      setUpperLiquidity(res.liquidity_levels?.upper ?? null);
      setLowerLiquidity(res.liquidity_levels?.lower ?? null);
      setFinalVerdict(res.final_verdict || null);
      setOnaySinyali(res.onay_sinyali || null);
      setStatusMessage("Analiz tamamlandi.");
      setProgressPercentage(100); // Set to 100% when analysis completes
    }).catch((err) => {
      console.error("Analiz hatasi:", err);
      setStatusMessage("Analiz hatasi olustu.");
      setProgressPercentage(0); // Reset progress on error
    });
  }, [selectedCoin, selectedTimeframe, mode]);

  useEffect(() => {
    window.electronAPI?.getCoinList?.().then((data) => {
      if (Array.isArray(data)) setCoinList(data);
    }).catch((err) => console.error("Coin listesi yüklenemedi:", err));
  }, []);

  useEffect(() => {
    let interval;
    if (statusMessage === "Analiz yapiliyor...") {
      let progressPercentage = 0;
      interval = setInterval(() => {
        if (progressPercentage < 100) {
          progressPercentage += 10; // Her 1 saniyede %10 artar
          setProgressPercentage(progressPercentage);
          document.querySelector(".progress").style.width = `${progressPercentage}%`;
        } else {
          clearInterval(interval);
        }
      }, 1000);
    }
    return () => clearInterval(interval); // Cleanup interval on component unmount or status change
  }, [statusMessage]);

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col overflow-hidden">
      <header className="flex justify-between items-center px-2 py-1 border-b border-gray-700">
        <div className="flex gap-2 text-sm items-center flex-wrap">
          <button onClick={() => { setMode("scalping"); setShowSettings(false); setShowHistory(false); }}
            className={`hover:text-blue-400 ${mode === "scalping" ? "text-blue-400 font-semibold" : ""}`}>Scalping</button>
          <button onClick={() => { setMode("yatirim"); setShowSettings(false); setShowHistory(false); }}
            className={`hover:text-blue-400 ${mode === "yatirim" ? "text-blue-400 font-semibold" : ""}`}>Yatırım</button>
          <select className="bg-gray-800 px-1 py-0.5 rounded text-sm" value={selectedExchange} onChange={(e) => setSelectedExchange(e.target.value)}>
            <option value="Binance">Binance</option>
          </select>
          <button onClick={() => { setShowSettings(true); setShowHistory(false); }} className="hover:text-blue-400">Ayarlar</button>
        </div>
        <div className="text-gray-400 text-xs">Kripto Analiz | {mode === "scalping" ? "Scalping Modu" : "Yatırım Modu"}</div>
      </header>

      <main className="flex-1 p-2 flex flex-col gap-2">
        {showSettings ? <AyarlarSayfasi /> :
          showHistory ? <GecmisAnalizler analizGecmisi={[]} handleSil={() => { }} /> : (
            <div className="flex flex-col lg:flex-row gap-2 flex-grow min-h-0">
              <div className="flex-1 flex flex-col gap-2">
                <div className="flex items-center gap-2 p-2 bg-gray-800 rounded-lg flex-wrap">
                  <CoinSelector selectedExchange={selectedExchange} onCoinChange={setSelectedCoin} coinList={coinList} selectedCoin={selectedCoin} />
                  <div className="flex gap-1 flex-wrap">
                    {timeframes.map((tf) => (<button key={tf} className={`px-2 py-1 rounded text-sm ${selectedTimeframe === tf ? "bg-blue-600" : "bg-gray-700 hover:bg-gray-600"}`} onClick={() => setSelectedTimeframe(tf)}>{tf}</button>))}
                  </div>
                  <button onClick={() => { setStatusMessage("Coin listesi güncelleniyor..."); window.electronAPI?.guncelleListe?.().then(() => setStatusMessage("Liste güncellendi.")); }}
                    className="bg-green-600 hover:bg-green-700 px-2 py-1 rounded text-sm">📥 Liste Güncelle</button>
                  <button onClick={handleAnalyze} className="bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded text-sm">Analiz Et</button>
                </div>

                <div className="bg-gray-800 rounded-lg flex-grow p-1">
                  {selectedCoin && selectedTimeframe ? <GrafikBileseni symbol={selectedCoin} interval={timeframeToTradingView[selectedTimeframe]} /> : <div className="flex justify-center items-center h-full text-gray-400">Lütfen bir coin ve zaman aralığı seçin.</div>}
                </div>
              </div>

              <div className="lg:w-72 xl:w-80 flex flex-col">
                <div className="bg-gray-800 p-2 rounded-lg flex flex-col flex-1 overflow-hidden">
                  <h2 className="text-sm font-semibold mb-2 text-gray-300">İndikatörler Konseyi</h2>
                  <div className="flex-1 overflow-y-auto pr-1">
                    {Array.isArray(indicatorList) && indicatorList.length > 0 ? (
                      <ul className="space-y-1 text-sm text-gray-300">
                        {indicatorList.map((ind, i) => {
                          const name = ind?.indikator || "—";
                          const displayName = indicatorDisplayNames[name] || name;
                          const signal = ind?.sinyal || "YOK";
                          const color = signal.includes("AL") ? "text-green-400" : signal.includes("SAT") ? "text-red-400" : signal === "YUKARI" ? "text-green-400" : signal === "AŞAĞI" ? "text-red-400" : signal === "SIKIŞMA" ? "text-yellow-400" : signal === "VOLATİL" ? "text-blue-400" : "text-gray-400";
                          return (<li key={i} className="flex justify-between items-center"><span className="truncate capitalize">{displayName}</span><span className={`font-semibold ${color}`}>{signal}</span></li>);
                        })}
                      </ul>
                    ) : <p className="text-xs text-gray-500">Analiz bekleniyor...</p>}
                  </div>
                </div>
              </div>
            </div>
          )}
      </main>

      {!showSettings && !showHistory && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2 p-2">
          <div className="bg-gray-800 p-1 rounded-lg text-center flex flex-col justify-center">
            <h2 className="text-xs font-semibold mb-0.5 text-gray-400">Açılış Fiyatı</h2>
            <p className="text-base font-bold text-gray-300">{openPrice !== null ? openPrice.toFixed(4) : "—"}</p>
          </div>
          <div className="bg-gray-800 p-1 rounded-lg text-center flex flex-col justify-center">
            <h2 className="text-xs font-semibold mb-0.5 text-gray-400">Kapanış Tahmini</h2>
            <p className="text-base font-bold text-blue-400">{closePrice !== null ? closePrice.toFixed(4) : "—"}</p>
          </div>
          <div className="bg-gray-800 p-1 rounded-lg text-center flex flex-col justify-center">
            <h2 className="text-xs font-semibold text-gray-400 text-center mb-0.5">Zaman</h2>
            {openTime && closeTime ? (
              <div className="flex justify-between items-center">
                <div className="flex flex-col text-center">
                  <span className="text-xs font-semibold text-white">{new Date(openTime).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" })}</span>
                  <span className="text-xs text-gray-300">{new Date(openTime).toLocaleDateString("tr-TR", { day: '2-digit', month: '2-digit', year: '2-digit' })}</span>
                </div>
                <span className="text-gray-400 self-center text-xs">→</span>
                <div className="flex flex-col text-center">
                  <span className="text-xs font-semibold text-white">{new Date(closeTime).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" })}</span>
                  <span className="text-xs text-gray-300">{new Date(closeTime).toLocaleDateString("tr-TR", { day: '2-digit', month: '2-digit', year: '2-digit' })}</span>
                </div>
              </div>
            ) : <p className="text-base font-bold text-gray-500">—</p>}
          </div>
          <div className="bg-gray-800 p-1 rounded-lg text-center flex flex-col justify-center">
            <h2 className="text-xs font-semibold mb-0.5 text-gray-400">AI Sinyali</h2>
            <p className={`text-lg font-bold ${aiSignal === "YUKARI" ? "text-green-400" : aiSignal === "AŞAĞI" ? "text-red-400" : "text-yellow-300"}`}>{aiSignal || "—"}</p>
          </div>
          <div className="bg-gray-800 p-1 rounded-lg text-center flex flex-col justify-center">
            <h2 className="text-xs font-semibold mb-0.5 text-gray-400">Alt Likidite</h2>
            <p className="text-base font-bold text-green-500">{lowerLiquidity !== null ? lowerLiquidity.toFixed(4) : "—"}</p>
          </div>
          <div className="bg-gray-800 p-1 rounded-lg text-center flex flex-col justify-center">
            <h2 className="text-xs font-semibold mb-0.5 text-gray-400">Üst Likidite</h2>
            <p className="text-base font-bold text-red-500">{upperLiquidity !== null ? upperLiquidity.toFixed(4) : "—"}</p>
          </div>
          <div className="bg-gray-800 p-1 rounded-lg text-center flex flex-col justify-center">
            <h2 className="text-xs font-semibold mb-0.5 text-gray-400">Genel Değerlendirme</h2>
            <p className={`text-base font-bold ${finalVerdict?.verdict.includes("ALIM") ? "text-green-400" : finalVerdict?.verdict.includes("SATIM") ? "text-red-400" : "text-yellow-300"}`}>{finalVerdict?.verdict || "—"}</p>
          </div>
          <div className="bg-gray-800 p-1 rounded-lg text-center flex flex-col justify-center">
            <h2 className="text-xs font-semibold mb-0.5 text-gray-400">Fikir Birliği %</h2>
            {finalVerdict ? (
              <div className="w-full bg-gray-700 rounded-full h-4 mt-0.5">
                <div className={`h-4 rounded-full flex items-center justify-center transition-all duration-500 ${getConfidenceColor(finalVerdict.confidence_percent).bg}`}
                  style={{ width: `${finalVerdict.confidence_percent || 0}%` }}>
                  <span className={`text-xs ${getConfidenceColor(finalVerdict.confidence_percent).text}`}>
                    %{finalVerdict.confidence_percent}
                  </span>
                </div>
              </div>
            ) : <p className="text-base font-bold text-gray-500">—</p>}
          </div>
        </div>
      )}

      <footer className="px-2 py-1 border-t border-gray-700 flex flex-col md:flex-row justify-between items-center text-sm gap-2">
        <div onClick={() => { setShowHistory(true); setShowSettings(false); }} className="cursor-pointer hover:text-blue-400">📊 Geçmiş Analizler</div>
        <div className="text-xs">
          <div className="progress-bar">
            <div className="progress" style={{ width: `${progressPercentage}%` }}></div>
            <span className="status-text">Durum: {statusMessage}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <button className="bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded">Alarm Oluştur</button>
        </div>
      </footer>
    </div>
  );
}

export default App;