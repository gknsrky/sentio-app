// client/src/components/GecmisAnalizler.jsx

import React, { useState, useEffect } from 'react';

// --- YARDIMCI BİLEŞENLER ve FONKSİYONLAR (Değişiklik yok) ---
const StatusBadge = ({ status }) => {
  const color = status === 'VERIFIED' ? 'bg-green-500' : 'bg-yellow-500';
  return <span className={`px-2 py-1 text-xs font-bold text-white rounded-full ${color}`}>{status}</span>;
};

const SuccessBadge = ({ success }) => {
  if (success === null || success === undefined) return <span className="text-gray-400">-</span>;
  const color = success ? 'text-green-400' : 'text-red-400';
  const text = success ? 'BAŞARILI' : 'BAŞARISIZ';
  return <span className={`font-bold ${color}`}>{text}</span>;
};

const getAccuracyColor = (percentage) => {
  if (percentage === null || percentage === undefined) return "text-gray-400";
  if (percentage >= 99.5) return 'text-green-400';
  if (percentage >= 98) return 'text-lime-400';
  return 'text-red-500';
};

const getSignalColor = (signal) => {
  if (!signal) return "text-gray-400";
  if (signal.includes("AL")) return "text-green-400";
  if (signal.includes("SAT")) return "text-red-400";
  if (signal === "YUKARI") return "text-green-400";
  if (signal === "AŞAĞI") return "text-red-400";
  if (signal === "SIKIŞMA") return "text-yellow-400";
  if (signal === "VOLATİL") return "text-blue-400";
  return "text-gray-400";
};


function GecmisAnalizler() {
  const [allLogs, setAllLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [selectedLog, setSelectedLog] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [uniqueCoins, setUniqueCoins] = useState([]);

  useEffect(() => {
    window.electronAPI.getPredictionLog().then(logs => {
      if (Array.isArray(logs)) {
        const sortedLogs = logs.sort((a, b) => new Date(b.analysis_timestamp) - new Date(a.analysis_timestamp));
        setAllLogs(sortedLogs);
        setFilteredLogs(sortedLogs); // Başlangıçta hepsi filtrelenmiş listede
        if (sortedLogs.length > 0) {
          setSelectedLog(sortedLogs[0]); // Başlangıçta en yenisi seçili
        }
        // Benzersiz coinleri alıp sıralayarak state'e ata
        const coins = [...new Set(logs.map(log => log.symbol))];
        setUniqueCoins(coins.sort());
      }
    }).catch(err => console.error("Tahmin günlüğü alınamadı:", err));
  }, []);

  // --- ⭐⭐⭐ HATA AYIKLAMA KODLARI EKLENDİ ⭐⭐⭐ ---
  useEffect(() => {
    // 1. Konsola ne ile filtreleme yapıldığını yazdır.
    console.log(`Filtreleme efekti çalıştı. Arama terimi: "${searchTerm}"`);

    // 2. Filtrele. Veri tutarlılığı için trim() ekledim.
    const filtered = searchTerm
      ? allLogs.filter(log => log.symbol.trim() === searchTerm.trim())
      : allLogs;

    // 3. Filtreleme sonrası kaç kayıt kaldığını yazdır.
    console.log(`Filtreleme sonrası bulunan kayıt sayısı: ${filtered.length}`);
    setFilteredLogs(filtered);

    // 4. Detay panelini güncelle (bu kısım zaten çalışıyordu).
    if (filtered.length > 0) {
      setSelectedLog(filtered[0]);
    } else {
      setSelectedLog(null);
    }
  }, [searchTerm, allLogs]);

  useEffect(() => {
    // --- ⭐⭐⭐ DEĞİŞİKLİK BURADA ⭐⭐⭐ ---
    // Katı eşitlik (===) yerine daha esnek olan includes() metodunu kullanıyoruz.
    const filtered = searchTerm
      ? allLogs.filter(log => log.symbol.includes(searchTerm))
      : allLogs;

    setFilteredLogs(filtered);

    if (filtered.length > 0) {
      // Eğer seçili olan analiz, yeni filtrelenmiş listede yoksa, listenin ilk elemanını seç.
      const isSelectedLogVisible = filtered.some(log => log.prediction_id === selectedLog?.prediction_id);
      if (!isSelectedLogVisible) {
        setSelectedLog(filtered[0]);
      }
    } else {
      setSelectedLog(null);
    }
  }, [searchTerm, allLogs,]); // selectedLog'u dependency'e ekledik.

  const renderDetailView = () => {
    if (!selectedLog) {
      return <div className="flex items-center justify-center h-full text-gray-500">Detayları görmek için soldaki listeden bir analiz seçin.</div>;
    }

    // Bu kısımda değişiklik yok, her şey 'selectedLog' state'ine bağlı olduğu için otomatik çalışacak.
    const { predictions_at_analysis: predictions, verification_results: verification } = selectedLog;

    return (
      <div className="p-4 space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold">{selectedLog.symbol} <span className="text-lg text-gray-400">{selectedLog.interval}</span></h2>
            <p className="text-xs text-gray-500">Analiz Zamanı: {new Date(selectedLog.analysis_timestamp).toLocaleString('tr-TR')}</p>
          </div>
          <StatusBadge status={selectedLog.status} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-center">
          <div className="bg-gray-700/50 p-3 rounded-lg">
            <h3 className="text-sm text-gray-400">Nihai Karar</h3>
            <p className="text-xl font-bold">{predictions.final_verdict.verdict}</p>
            <p className="text-xs">Skor: {predictions.final_verdict.score}</p>
          </div>
          <div className="bg-gray-700/50 p-3 rounded-lg">
            <h3 className="text-sm text-gray-400">Nihai Karar Başarısı</h3>
            <SuccessBadge success={verification.final_verdict_success} />
          </div>
          <div className="bg-gray-700/50 p-3 rounded-lg">
            <h3 className="text-sm text-gray-400">LSTM Sinyali</h3>
            <p className="text-xl font-bold">{predictions.lstm_signal}</p>
          </div>
          <div className="bg-gray-700/50 p-3 rounded-lg">
            <h3 className="text-sm text-gray-400">LSTM Sinyal Başarısı</h3>
            <SuccessBadge success={verification.lstm_signal_success} />
          </div>
          <div className="bg-gray-700/50 p-3 rounded-lg col-span-1 md:col-span-2">
            <h3 className="text-sm text-gray-400">LSTM Fiyat Tahmini</h3>
            <div className="flex justify-around items-start pt-2 text-sm">

              {/* Açılış Fiyatı ve Zamanı */}
              <div className="flex flex-col items-center text-center">
                <span className="text-xs text-gray-400 font-semibold">Açılış</span>
                <span className="text-base">{selectedLog.target_candle_open_price}</span>
                <span className="text-xs text-gray-500 mt-1">
                  {new Date(selectedLog.target_candle_open_time).toLocaleTimeString('tr-TR', { timeZone: 'UTC' })} UTC
                </span>
              </div>

              {/* Tahmini Fiyat */}
              <div className="flex flex-col items-center text-center">
                <span className="text-xs text-gray-400 font-semibold">Tahmin</span>
                <span className="text-base">{predictions.lstm_predicted_price?.toFixed(4) || "-"}</span>
              </div>

              {/* Gerçekleşen Fiyat ve Kapanış Zamanı */}
              <div className="flex flex-col items-center text-center">
                <span className="text-xs text-gray-400 font-semibold">Gerçekleşen</span>
                <span className="text-base">{verification.actual_close_price?.toFixed(4) || "-"}</span>
                <span className="text-xs text-gray-500 mt-1">
                  {new Date(selectedLog.target_candle_close_time).toLocaleTimeString('tr-TR', { timeZone: 'UTC' })} UTC
                </span>
              </div>

              {/* Doğruluk Yüzdesi */}
              <div className="flex flex-col items-center text-center justify-center">
                <span className="text-xs font-normal">Hata Oranı: </span>
                <span className={getAccuracyColor(100 - verification.lstm_price_mape_percent)}>
                  %{verification.lstm_price_mape_percent?.toFixed(2) ?? "-"}
                </span>
              </div>

            </div>
          </div>
        </div>

        <div>
          <h3 className="font-semibold mb-2">Analiz Anındaki İndikatör Sinyalleri:</h3>
          <div className="bg-gray-700/50 p-4 rounded-lg">
            <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-2 text-sm">
              {Object.entries(predictions.all_indicator_signals).map(([key, value]) => (
                <li key={key} className="flex justify-between border-b border-gray-600/50 py-1">
                  <span className="text-gray-400 capitalize">{key.replace(/_signal|_predictor|_model/g, '')}:</span>
                  <span className={`font-semibold ${getSignalColor(value)}`}>{value}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="p-6 h-full flex flex-col">
      <h1 className="text-2xl font-bold mb-4 flex-shrink-0">📊 Geçmiş Analizler ve Başarı Karnesi</h1>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-0">

        {/* --- Sol Sütun: Kayıtlı Analizler Listesi --- */}
        <div className="lg:col-span-1 bg-gray-800 rounded-lg p-4 flex flex-col overflow-y-auto" style={{ maxHeight: '800px' }}>
          <h2 className="text-lg font-semibold mb-3 flex-shrink-0">Kayıtlı Analizler</h2>
          <select
            className="w-full p-2 bg-gray-700 rounded-md mb-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 flex-shrink-0"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          >
            <option value="">Tüm Coinleri Göster</option>
            {uniqueCoins.map(coin => <option key={coin} value={coin}>{coin}</option>)}
          </select>

          {/* SCROLL OLACAK ALAN */}
          <div className="flex-1 overflow-y-auto pr-2">
            {filteredLogs.length > 0 ? (
              <ul className="space-y-2 text-sm">
                {filteredLogs.map(log => (
                  <li
                    key={log.prediction_id}
                    className={`border border-gray-700 p-3 rounded-lg cursor-pointer hover:bg-gray-700/60 transition-colors ${selectedLog?.prediction_id === log.prediction_id ? 'bg-blue-600 border-blue-400' : ''}`}
                    onClick={() => setSelectedLog(log)}
                  >
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold">{log.symbol} - {log.interval}</span>
                      <StatusBadge status={log.status} />
                    </div>
                    <div className="flex justify-between text-xs text-gray-400">
                      <span>{new Date(log.analysis_timestamp).toLocaleDateString('tr-TR')}</span>
                      <span>{new Date(log.analysis_timestamp).toLocaleTimeString('tr-TR')}</span>
                    </div>
                  </li>
                ))}
              </ul>
            ) : <p className="text-gray-500 text-center mt-4">Kayıt bulunamadı.</p>}
          </div>
        </div>

        {/* --- Sağ Sütun: Analiz Detayları --- */}
        <div className="lg:col-span-2 bg-gray-800 rounded-lg flex flex-col overflow-y-auto" style={{ maxHeight: '800px' }}>
          <div className="flex-1 overflow-y-auto">
            {renderDetailView()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default GecmisAnalizler;