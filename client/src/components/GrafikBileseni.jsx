// client/src/components/GrafikBileseni.jsx

import React, { useEffect, useRef, memo } from 'react';

const GrafikBileseni = memo(({ symbol, interval }) => {
  const containerRef = useRef(null);
  const widgetRef = useRef(null);

  useEffect(() => {
    const createWidget = () => {
      if (!symbol || !interval || !containerRef.current || !window.TradingView) {
        return;
      }

      if (widgetRef.current) {
        widgetRef.current.remove();
        widgetRef.current = null;
      }

      // --- ⭐⭐⭐ DEĞİŞİKLİK BURADA BAŞLIYOR ⭐⭐⭐ ---
      // Widget'ı, indikatörler ve ayarlarıyla birlikte oluşturuyoruz.
      const widget = new window.TradingView.widget({
        // --- Standart Ayarlarınız ---
        container_id: containerRef.current.id,
        autosize: true,
        symbol: `BINANCE:${symbol}`,
        interval: interval,
        timezone: "Etc/UTC",
        theme: "dark",
        style: "1",
        locale: "tr",
        toolbar_bg: "#1e293b",
        enable_publishing: false,
        hide_side_toolbar: false,
        allow_symbol_change: false,
        save_image: false,
        details: true,
        withdateranges: true,
        hide_volume: false,

        // --- ⭐⭐⭐ ARAŞTIRMA SONUCU KESİN VE DOĞRU YÖNTEM ⭐⭐⭐ ---
        // studies_overrides'i tamamen kaldırıyoruz.
        // Tüm indikatörleri ve ayarlarını doğrudan 'studies' dizisi içinde tanımlıyoruz.
        studies: [
          // 1. İndikatör: Hızlı EMA (9 periyot)
          {
            id: "MASimple@tv-basicstudies", // Temel "Basit Hareketli Ortalama"yı çağırıyoruz
            inputs: {
              length: 9,
              type: "EMA" // <<< İÇERİDE TİPİNİ "EMA" OLARAK DEĞİŞTİRİYORUZ
            },
            styles: {
              "plot.color": "#3399FF" // Mavi renk
            }
          },

          // 2. İndikatör: Yavaş EMA (21 periyot)
          {
            id: "MASimple@tv-basicstudies",
            inputs: {
              length: 21,
              type: "EMA" // <<< İÇERİDE TİPİNİ "EMA" OLARAK DEĞİŞTİRİYORUZ
            },
            styles: {
              "plot.color": "#FF6D00" // Turuncu renk
            }
          },

          // 3. İndikatör: MACD (Zaten çalışıyor, dokunmuyoruz)
          {
            id: "MACD@tv-basicstudies",
            inputs: {
              fast_length: 12,
              slow_length: 26,
              signal_length: 9,
              source: "close"
            }
          }
        ]
      });

      // --- ⭐⭐⭐ DEĞİŞİKLİK BURADA BİTİYOR ⭐⭐⭐ ---

      widgetRef.current = widget;
    };

    if (!document.getElementById('tradingview-widget-script')) {
      const script = document.createElement('script');
      script.id = 'tradingview-widget-script';
      script.src = 'https://s3.tradingview.com/tv.js';
      script.async = true;
      script.onload = createWidget;
      document.body.appendChild(script);
    } else {
      createWidget();
    }

    return () => {
      if (widgetRef.current) {
        try {
          widgetRef.current.remove();
          widgetRef.current = null;
        } catch (error) {
          console.error("Widget kaldırılırken hata oluştu:", error);
        }
      }
    };
  }, [symbol, interval]);

  return (
    <div
      ref={containerRef}
      id="tv_chart_container"
      style={{
        width: "100%",
        height: "100%",
        minHeight: "400px",
      }}
    />
  );
});

export default GrafikBileseni;