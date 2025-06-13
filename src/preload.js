const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
    runAnalysis: (params) => ipcRenderer.invoke("run_analysis", params),
    kaydetAnaliz: (data) => ipcRenderer.invoke("kaydet_analiz", data),
    runAnalysis: (params) => ipcRenderer.invoke("run_analysis", params),
    guncelleListe: () => ipcRenderer.invoke("guncelle-liste"),
    getCoinList: () => ipcRenderer.invoke("get_coin_list"),
    getPredictionLog: () => ipcRenderer.invoke('get-prediction-log')
});
