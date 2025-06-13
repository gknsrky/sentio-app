// client/src/components/AyarlarSayfasi.jsx

import React, { useState } from "react";

function AyarlarSayfasi() {
  const [aktifSekme, setAktifSekme] = useState("scalping");

  return (
    <div className="max-w-5xl mx-auto mt-10 bg-gray-800 text-white p-6 rounded-lg">
      {/* Sekme Butonları */}
      <div className="flex gap-4 border-b border-gray-600 mb-6 pb-2">
        <button
          onClick={() => setAktifSekme("scalping")}
          className={`px-4 py-2 rounded ${aktifSekme === "scalping" ? "bg-blue-600" : "bg-gray-700"}`}
        >
          Scalping
        </button>
        <button
          onClick={() => setAktifSekme("yatirim")}
          className={`px-4 py-2 rounded ${aktifSekme === "yatirim" ? "bg-blue-600" : "bg-gray-700"}`}
        >
          Yatırım
        </button>
        <button
          onClick={() => setAktifSekme("kisisel")}
          className={`px-4 py-2 rounded ${aktifSekme === "kisisel" ? "bg-blue-600" : "bg-gray-700"}`}
        >
          Kişisel Ayarlar
        </button>
      </div>

      {/* İçerik Alanı */}
      {aktifSekme === "scalping" && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Scalping İndikatör Ayarları</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label>EMA Periyot: <input type="number" defaultValue={9} className="w-full p-2 bg-gray-900 rounded" /></label>
            <label>RSI Periyot: <input type="number" defaultValue={14} className="w-full p-2 bg-gray-900 rounded" /></label>
            <label>VWAP Modu:
              <select className="w-full p-2 bg-gray-900 rounded">
                <option>Saatlik</option>
                <option>Günlük</option>
              </select>
            </label>
            <label>Bollinger Sapması: <input type="number" defaultValue={2} step={0.1} className="w-full p-2 bg-gray-900 rounded" /></label>
          </div>
        </div>
      )}

      {aktifSekme === "yatirim" && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Yatırım İndikatör Ayarları</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label>MACD Signal Line: <input type="number" defaultValue={9} className="w-full p-2 bg-gray-900 rounded" /></label>
            <label>RSI Periyot: <input type="number" defaultValue={14} className="w-full p-2 bg-gray-900 rounded" /></label>
            <label>MA200 Periyot: <input type="number" defaultValue={200} className="w-full p-2 bg-gray-900 rounded" /></label>
            <label>Ichimoku Tenkan: <input type="number" defaultValue={9} className="w-full p-2 bg-gray-900 rounded" /></label>
          </div>
        </div>
      )}

      {aktifSekme === "kisisel" && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Kişisel Ayarlar & API</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label>Borsa Seçimi:
              <select className="w-full p-2 bg-gray-900 rounded">
                <option>Binance</option>
                <option>KuCoin</option>
                <option>MEXC</option>
              </select>
            </label>
            <label>API Key: <input type="text" className="w-full p-2 bg-gray-900 rounded" /></label>
            <label>API Secret: <input type="password" className="w-full p-2 bg-gray-900 rounded" /></label>
            <label>Portföy Takibi Aktif:
              <select className="w-full p-2 bg-gray-900 rounded">
                <option>Evet</option>
                <option>Hayır</option>
              </select>
            </label>
          </div>
        </div>
      )}
    </div>
  );
}

export default AyarlarSayfasi;
