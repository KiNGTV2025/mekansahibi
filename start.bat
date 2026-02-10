@echo off
chcp 65001 >nul
title Advanced HLS Proxy - Anti-Block Edition

echo ======================================
echo 🛡️ Advanced HLS Proxy Başlatılıyor...
echo ======================================
echo.

REM Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python bulunamadı!
    echo Python 3.8+ kurulu olmalıdır.
    pause
    exit /b 1
)

echo ✅ Python bulundu
echo.

REM Gerekli paketleri kontrol et
echo 📦 Paketler kontrol ediliyor...
pip show aiohttp >nul 2>&1
if errorlevel 1 (
    echo ⚠️  aiohttp kuruluyor...
    pip install aiohttp
)

pip show gunicorn >nul 2>&1
if errorlevel 1 (
    echo ℹ️  gunicorn Windows'ta desteklenmiyor, normal mode kullanılacak
)

echo.
echo ======================================
echo ✨ Hazır!
echo ======================================
echo.

REM IP adresini al
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set IP=%%a
set IP=%IP: =%

echo 📋 Sunucu Bilgileri:
echo   • Local: http://localhost:7860
echo   • WiFi: http://%IP%:7860
echo.
echo 📱 LOKKE Browser için URL:
echo http://%IP%:7860/vavoo
echo.
echo ======================================
echo.

REM Başlat
echo 🚀 Sunucu başlatılıyor...
echo.
echo Tarayıcınızda aç: http://localhost:7860
echo LOKKE Browser'da aç: http://%IP%:7860/vavoo
echo.
echo Kapatmak için CTRL+C
echo ======================================
echo.

python app_advanced.py

pause
