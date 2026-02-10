#!/bin/bash

# 🚀 Advanced HLS Proxy - Quick Start Script
# Anti-Block Edition

echo "======================================"
echo "🛡️ Advanced HLS Proxy Başlatılıyor..."
echo "======================================"
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Python version kontrolü
echo -e "${BLUE}🔍 Python versiyonu kontrol ediliyor...${NC}"
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo -e "${GREEN}✅ Python $python_version bulundu${NC}"
echo ""

# Gerekli paketleri kontrol et
echo -e "${BLUE}📦 Gerekli paketler kontrol ediliyor...${NC}"
packages=("aiohttp" "gunicorn")
missing_packages=()

for package in "${packages[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✅ $package kurulu${NC}"
    else
        echo -e "${YELLOW}⚠️  $package eksik${NC}"
        missing_packages+=("$package")
    fi
done

# Eksik paketleri kur
if [ ${#missing_packages[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}📥 Eksik paketler kuruluyor...${NC}"
    pip3 install --break-system-packages ${missing_packages[@]}
fi

echo ""
echo "======================================"
echo -e "${GREEN}✨ Kurulum Tamamlandı!${NC}"
echo "======================================"
echo ""

# IP adresini tespit et
IP_ADDRESS=$(hostname -I | awk '{print $1}')
PORT=7860

echo -e "${BLUE}📋 Sunucu Bilgileri:${NC}"
echo "  • Local: http://localhost:$PORT"
echo "  • WiFi: http://$IP_ADDRESS:$PORT"
echo ""
echo -e "${YELLOW}📱 LOKKE Browser için URL:${NC}"
echo -e "${GREEN}http://$IP_ADDRESS:$PORT/vavoo${NC}"
echo ""

# Başlatma seçenekleri
echo "======================================"
echo "Nasıl başlatmak istersiniz?"
echo "======================================"
echo "1) Normal Mode (Development)"
echo "2) Production Mode (Gunicorn)"
echo "3) Config'i Görüntüle"
echo "4) Çıkış"
echo ""
read -p "Seçiminiz (1-4): " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}🚀 Normal mode başlatılıyor...${NC}"
        echo ""
        python3 app_advanced.py
        ;;
    2)
        echo ""
        echo -e "${GREEN}🚀 Production mode başlatılıyor...${NC}"
        echo ""
        gunicorn app_advanced:app \
            --bind 0.0.0.0:$PORT \
            --workers 2 \
            --worker-class aiohttp.GunicornWebWorker \
            --timeout 180 \
            --keepalive 60 \
            --access-logfile - \
            --error-logfile -
        ;;
    3)
        echo ""
        python3 config_advanced.py
        echo ""
        read -p "Devam etmek için Enter'a basın..."
        exec "$0"
        ;;
    4)
        echo ""
        echo -e "${BLUE}👋 Görüşmek üzere!${NC}"
        exit 0
        ;;
    *)
        echo ""
        echo -e "${RED}❌ Geçersiz seçim!${NC}"
        exit 1
        ;;
esac
