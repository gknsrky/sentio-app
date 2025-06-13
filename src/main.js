const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn, exec, execFile } = require("child_process");

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, "preload.js"),
        },
    });

    mainWindow.loadFile(path.join(__dirname, "../client/build/index.html"));
}

app.whenReady().then(() => {
    createWindow();
    app.on("activate", function () {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });

    // --- OTOMASYON ZAMANLAYICI BAŞLANGICI ---

    // 1. Uygulama ilk açıldığında, gecikme olmasın diye script'i bir kez hemen çalıştır.
    runVerificationScript();

    // 2. Ardından, her 5 dakikada bir (300,000 milisaniye) script'i tekrar çalıştırmak için zamanlayıcı kur.
    setInterval(runVerificationScript, 5 * 60 * 1000);

    // --- OTOMASYON ZAMANLAYICI BİTİŞİ ---
});

app.on("window-all-closed", function () {
    if (process.platform !== "darwin") app.quit();
});

// ✅ ANALİZ BAŞLAT (run_analysis)
ipcMain.handle("run_analysis", async (event, { symbol, interval, mode }) => {
    const scriptPath = path.join(__dirname, "../python_scripts/run_all_analysis.py");
    console.log(">> run_analysis isteği geldi");
    console.log("PYTHON ÇAĞRISI:", scriptPath, symbol, interval, mode);

    return new Promise((resolve, reject) => {
        const pythonProcess = spawn("python", [scriptPath, symbol, interval, mode], {
            env: { ...process.env, PYTHONUTF8: '1' }
        });

        let stdoutData = "";
        let stderrData = "";

        pythonProcess.stdout.on("data", (data) => {
            stdoutData += data.toString("utf-8");
        });
        pythonProcess.stderr.on("data", (data) => {
            const errStr = data.toString("utf-8");
            console.error("PYTHON STDERR:", errStr);
            stderrData += errStr;
        });
        pythonProcess.on("close", (code) => {
            if (code === 0) {
                try {
                    const parsed = JSON.parse(stdoutData);
                    resolve(parsed);
                } catch (err) {
                    reject({ error: true, message: "JSON parse hatası", output: stdoutData, stderr: stderrData });
                }
            } else {
                reject({ error: true, message: "Python script hata verdi", stderr: stderrData });
            }
        });
    });
});

// ✅ COIN LİSTESİ OKUMA
ipcMain.handle("get_coin_list", async () => {
    const filePath = path.join(__dirname, "../client/public/binance_symbols.json");
    try {
        const json = fs.readFileSync(filePath, "utf8");
        return JSON.parse(json);
    } catch (e) {
        console.error("Coin listesi okunamadı:", e);
        return [];
    }
});

// ✅ COIN LİSTESİ GÜNCELLEME
ipcMain.handle("guncelle-liste", async () => {
    return new Promise((resolve, reject) => {
        const script = path.join(__dirname, "../python_scripts/update_binance_symbols.py");
        exec(`python "${script}"`, { env: { ...process.env, PYTHONUTF8: '1' } }, (error, stdout, stderr) => {
            if (error) {
                console.error("Liste güncelleme hatası:", stderr);
                reject(stderr);
            } else {
                console.log("Liste güncellendi:", stdout);
                resolve(stdout);
            }
        });
    });
});

// ⭐ YENİ EKLENEN BLOK BAŞLANGICI ⭐
// ✅ TAHMİN GÜNLÜĞÜNÜ OKUMA
ipcMain.handle("get-prediction-log", async () => {
    const filePath = path.join(__dirname, "..", "data", "prediction_log.json");
    if (!fs.existsSync(filePath)) {
        return []; // Dosya hiç yoksa boş liste döndür
    }
    try {
        const content = fs.readFileSync(filePath, "utf8");
        // Eğer dosya var ama içi boşsa, parse etmeye çalışma, boş liste döndür
        if (content.trim() === '') {
            return [];
        }
        return JSON.parse(content);
    } catch (e) {
        console.error("Tahmin günlüğü okunamadı:", e);
        return []; // Hata durumunda da boş liste döndür
    }
});
// Arka planda doğrulama script'ini çalıştırır.
function runVerificationScript() {
    const scriptPath = path.join(__dirname, "../python_scripts/verify_predictions.py");
    console.log("[OTOMASYON] Arka planda tahmin doğrulama işlemi başlatılıyor...");

    execFile("python", [scriptPath], { env: { ...process.env, PYTHONUTF8: '1' } }, (error, stdout, stderr) => {
        if (error) {
            console.error(`[OTOMASYON HATA] verify_predictions script'i çalıştırılamadı: ${stderr}`);
            return;
        }
        // Script'in çıktısını konsola yazdırır.
        console.log(`[OTOMASYON BAŞARILI] Doğrulama tamamlandı: ${stdout}`);
    });
  }