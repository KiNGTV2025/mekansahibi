# 🛡️ Advanced HLS Proxy - Anti-Block Edition

Gelişmiş HLS streaming proxy sistemi - Vavoo bypass ve anti-block özellikleri ile.

## 🚀 Özellikler

### 🔐 Anti-Block Mekanizmaları
- **User-Agent Rotation**: 9+ farklı browser simulation
- **Domain Rotation**: Otomatik domain değiştirme (vavoo.to, vavoo.tv, vavootv.to, vavoo.cc)
- **SSL Bypass**: Gelişmiş SSL sertifika bypass
- **Anti-Fingerprinting**: Browser parmak izi koruması
- **Smart Retry**: Akıllı yeniden deneme sistemi
- **Session Management**: Dinamik session ID yönetimi

### 📺 Streaming
- HLS/DASH proxy desteği
- Segment caching
- Adaptive bitrate support
- FFmpeg entegrasyonu
- DRM decryption

### 📹 DVR/Recording
- Live stream recording
- Otomatik cleanup
- Multi-stream desteği

## 📱 LOKKE Browser Kullanımı

### Adım 1: Sunucuyu Başlat
```bash
python app_advanced.py
```

### Adım 2: IP Adresini Öğren
Terminal'de gösterilecek:
```
📱 http://192.168.1.100:7860 (WiFi/LAN)
💡 LOKKE Browser URL: http://192.168.1.100:7860/vavoo
```

### Adım 3: LOKKE Browser'da Aç
1. LOKKE Browser'ı aç (www.lokke.app)
2. URL alanına gir:
   ```
   http://192.168.1.100:7860/vavoo
   ```
3. Enter'a bas - Vavoo otomatik açılacak! 🎉

## 🔧 API Endpoints

### Vavoo Bypass
```bash
# Doğrudan bypass
GET /vavoo

# Özel URL ile
GET /vavoo/bypass?url=https://vavoo.to
```

### HLS Proxy
```bash
GET /proxy/hls/manifest.m3u8?url=STREAM_URL
```

### Stream Extractor
```bash
GET /extractor?url=VIDEO_PAGE_URL
```

### Playlist Builder
```bash
GET /builder
```

## ⚙️ Kurulum

### Gereksinimler
```bash
pip install aiohttp
pip install gunicorn  # production için
```

### Temel Kullanım
```bash
# Local development
python app_advanced.py

# Production (Gunicorn ile)
gunicorn app_advanced:app --bind 0.0.0.0:7860 --worker-class aiohttp.GunicornWebWorker
```

### Docker ile
```bash
docker build -t hls-proxy .
docker run -p 7860:7860 hls-proxy
```

## 🎯 Özellik Detayları

### Anti-Block Sistemi
Sistem otomatik olarak:
- Her istekte rastgele User-Agent kullanır
- Failed domain'leri tespit edip alternatife geçer
- İnsan benzeri delay'ler ekler (0.1-0.5 saniye)
- Session cookie'leri dinamik oluşturur
- Referer header'ları randomize eder

### Domain Rotation
4 farklı Vavoo domain'i desteklenir:
1. vavoo.to (primary)
2. vavoo.tv
3. vavootv.to
4. vavoo.cc

Bir domain fail olursa otomatik olarak diğerine geçer.

### Smart Retry
- Max 3 retry
- Exponential backoff (1s, 2s, 3s)
- Her retry'da farklı User-Agent
- Domain rotation ile birlikte çalışır

## 📊 Konfigürasyon

`config_advanced.py` dosyasından özelleştirilebilir:

```python
# Anti-block
ENABLE_ANTI_BLOCK = True
ENABLE_DOMAIN_ROTATION = True
ENABLE_USER_AGENT_ROTATION = True

# Performance
CHUNK_SIZE = 128 * 1024  # 128KB
BUFFER_SIZE = 1024 * 1024  # 1MB
MAX_CONNECTIONS = 100

# Retry
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
```

## 🔍 Troubleshooting

### Problem: "All domains unavailable"
**Çözüm:**
- Internet bağlantınızı kontrol edin
- VPN kullanmayı deneyin
- `EXTERNAL_PROXY_URL` ayarlayın

### Problem: Yavaş streaming
**Çözüm:**
- `CHUNK_SIZE` değerini artırın
- `BUFFER_SIZE` değerini artırın
- WiFi sinyalini kontrol edin

### Problem: LOKKE'de açılmıyor
**Çözüm:**
- Doğru IP adresini kullandığınızdan emin olun
- Port'un açık olduğunu kontrol edin (firewall)
- `/vavoo` endpoint'ini kullanın

## 🛠️ Geliştirme

### Yeni Extractor Eklemek
```python
# extractors/myextractor.py
class MyExtractor:
    @staticmethod
    async def extract(url):
        # Implementation
        return stream_url
```

### Custom Domain Eklemek
```python
# config_advanced.py
VAVOO_BACKUP_DOMAINS = [
    'vavoo.tv',
    'vavootv.to',
    'vavoo.cc',
    'yeni-domain.com',  # Yeni domain
]
```

## 📝 Notlar

- **Yasal Kullanım**: Bu yazılım sadece kişisel kullanım içindir
- **Telif Hakları**: Telif haklarına saygı gösterin
- **Rate Limiting**: Aşırı kullanımdan kaçının

## 🤝 Katkıda Bulunma

Pull request'ler kabul edilir. Büyük değişiklikler için önce issue açın.

## 📄 Lisans

MIT License - Detaylar için LICENSE dosyasına bakın.

## 🙏 Teşekkürler

- aiohttp team
- FFmpeg project
- Tüm katkıda bulunanlara

## 📧 İletişim

Sorular için issue açın veya pull request gönderin.

---

**Made with ❤️ by Community**

Version: 2.0 - Advanced Anti-Block Edition
