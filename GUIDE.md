# 📖 Advanced HLS Proxy - Detaylı Kullanım Rehberi

## İçindekiler
1. [Giriş](#giriş)
2. [Kurulum](#kurulum)
3. [LOKKE Browser Kullanımı](#lokke-browser-kullanımı)
4. [Anti-Block Özellikleri](#anti-block-özellikleri)
5. [API Referansı](#api-referansı)
6. [Sorun Giderme](#sorun-giderme)
7. [İpuçları](#ipuçları)

---

## Giriş

Advanced HLS Proxy, Vavoo gibi streaming servislerini bypass etmek için geliştirilmiş, anti-block özellikleri içeren gelişmiş bir proxy sistemidir.

### Temel Özellikler
- ✅ User-Agent rotation (9+ farklı browser)
- ✅ Domain rotation (4 farklı Vavoo domain)
- ✅ SSL bypass
- ✅ Anti-fingerprinting
- ✅ Smart retry sistemi
- ✅ Session management
- ✅ HLS/DASH proxy
- ✅ DVR/Recording desteği

---

## Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- pip (Python package manager)
- 2GB+ RAM
- Aktif internet bağlantısı

### Windows'ta Kurulum

1. **Python Kurulumu**
   - python.org'dan Python 3.8+ indirin
   - Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin

2. **Projeyi İndirin**
   ```cmd
   cd Downloads
   unzip PreProxyVavoo_Advanced.zip
   cd PreProxyVavoo_Advanced
   ```

3. **Başlatın**
   - `start.bat` dosyasına çift tıklayın
   - Veya komut satırından: `python app_advanced.py`

### Linux/Mac'te Kurulum

1. **Terminal'i Açın**
   ```bash
   cd ~/Downloads
   unzip PreProxyVavoo_Advanced.zip
   cd PreProxyVavoo_Advanced
   ```

2. **Başlatın**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

### Docker ile Kurulum

```bash
docker build -t hls-proxy .
docker run -p 7860:7860 hls-proxy
```

---

## LOKKE Browser Kullanımı

### Adım Adım Rehber

#### 1. Sunucuyu Başlatın
```bash
python app_advanced.py
```

Terminal'de şu çıktıyı göreceksiniz:
```
======================================
🛡️ ADVANCED HLS PROXY - Anti-Block Edition
🚀 HLS Proxy Server - Advanced (Local Mode)
📡 http://localhost:7860
📱 http://192.168.1.100:7860 (WiFi/LAN)
💡 LOKKE Browser URL: http://192.168.1.100:7860/vavoo
======================================
```

#### 2. IP Adresinizi Not Edin
Yukarıdaki örnekte: `192.168.1.100` (sizinki farklı olacaktır)

#### 3. LOKKE Browser'ı Açın
- Telefonunuzda LOKKE Browser'ı açın
- www.lokke.app adresine gidin

#### 4. Proxy URL'ini Girin
LOKKE Browser'daki URL alanına:
```
http://192.168.1.100:7860/vavoo
```
(192.168.1.100 yerine kendi IP adresinizi kullanın)

#### 5. Enter'a Basın
- Vavoo otomatik olarak açılacak
- Artık tüm içerikleri izleyebilirsiniz! 🎉

### Alternatif Kullanım Yöntemleri

#### Yöntem 1: Doğrudan Ana Sayfa
```
http://192.168.1.100:7860
```
Bu size tüm özelliklere erişim sağlar.

#### Yöntem 2: Playlist Builder
```
http://192.168.1.100:7860/builder
```
Kendi playlist'inizi oluşturun.

#### Yöntem 3: Manuel Stream
```
http://192.168.1.100:7860/proxy/hls/manifest.m3u8?url=STREAM_URL
```

---

## Anti-Block Özellikleri

### 1. User-Agent Rotation

Sistem otomatik olarak her istekte farklı browser simulation kullanır:

- Chrome on Windows (2 varyant)
- Chrome on Mac
- Firefox (2 varyant)
- Edge
- Safari
- iPhone Safari
- Android Chrome

**Nasıl Çalışır:**
```python
# Her istekte rastgele seçilir
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...
```

### 2. Domain Rotation

4 farklı Vavoo domain'i desteklenir:
1. **vavoo.to** (Primary)
2. **vavoo.tv**
3. **vavootv.to**
4. **vavoo.cc**

**Nasıl Çalışır:**
- Bir domain fail olursa otomatik olarak diğerine geçer
- Failed domain'ler 5 dakika boyunca cache'lenir
- 3 başarısız denemeden sonra domain blacklist'e alınır

### 3. Smart Retry

**Özellikler:**
- Maximum 3 retry
- Exponential backoff (1s, 2s, 3s)
- Her retry'da farklı User-Agent
- Domain rotation ile entegre

**Örnek:**
```
Attempt 1: vavoo.to + Chrome/Windows -> FAIL
Wait 1s...
Attempt 2: vavoo.tv + Firefox/Mac -> FAIL
Wait 2s...
Attempt 3: vavootv.to + Safari/iPhone -> SUCCESS ✅
```

### 4. SSL Bypass

**Özellikler:**
- SSL sertifika doğrulamasını atlar
- HTTPS üzerinden güvenli bağlantı
- Man-in-the-middle koruması

### 5. Anti-Fingerprinting

**Korunulan Özellikler:**
- Canvas fingerprinting
- WebGL fingerprinting
- Audio fingerprinting
- Font fingerprinting

**Eklenen Header'lar:**
```
DNT: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
```

### 6. Session Management

**Özellikler:**
- Dinamik session ID oluşturma
- Cookie yönetimi
- Session caching
- Timeout handling

---

## API Referansı

### Vavoo Bypass

#### GET /vavoo
Doğrudan Vavoo bypass.

**Örnek:**
```bash
curl http://localhost:7860/vavoo
```

**Response:**
```html
<!DOCTYPE html>
<html>
  <!-- Vavoo content -->
</html>
```

#### GET /vavoo/bypass
Özel URL ile bypass.

**Parameters:**
- `url` (string): Target URL

**Örnek:**
```bash
curl "http://localhost:7860/vavoo/bypass?url=https://vavoo.to/category/movies"
```

### HLS Proxy

#### GET /proxy/hls/manifest.m3u8
HLS stream proxy.

**Parameters:**
- `url` (string, required): HLS stream URL

**Örnek:**
```bash
curl "http://localhost:7860/proxy/hls/manifest.m3u8?url=https://example.com/stream.m3u8"
```

### Stream Extractor

#### GET /extractor
Video URL'inden stream çıkar.

**Parameters:**
- `url` (string, required): Video page URL

**Örnek:**
```bash
curl "http://localhost:7860/extractor?url=https://example.com/video/123"
```

**Response:**
```json
{
  "success": true,
  "stream_url": "https://example.com/stream.m3u8",
  "extractor": "generic"
}
```

### Playlist Builder

#### GET /builder
Interactive playlist builder.

**Örnek:**
```
http://localhost:7860/builder
```

#### POST /generate_urls
Playlist URL'leri oluştur.

**Body:**
```json
{
  "channels": [
    {
      "name": "Channel 1",
      "url": "https://example.com/stream1.m3u8"
    }
  ]
}
```

### Server Info

#### GET /info
Server bilgilerini görüntüle.

#### GET /api/info
JSON formatında server bilgileri.

**Response:**
```json
{
  "version": "2.0",
  "features": {
    "anti_block": true,
    "domain_rotation": true,
    "hls_proxy": true
  },
  "uptime": 3600,
  "active_streams": 5
}
```

---

## Sorun Giderme

### Problem 1: "All domains unavailable"

**Belirtiler:**
```
❌ Failed with domain vavoo.to
❌ Failed with domain vavoo.tv
❌ Failed with domain vavootv.to
❌ Failed with domain vavoo.cc
503 Service Unavailable
```

**Çözümler:**

1. **Internet bağlantınızı kontrol edin**
   ```bash
   ping google.com
   ```

2. **VPN kullanın**
   - ProtonVPN, NordVPN, vb.
   - Farklı bir ülke server'ı deneyin

3. **External proxy kullanın**
   ```python
   # config_advanced.py
   USE_EXTERNAL_PROXY = True
   EXTERNAL_PROXY_URL = 'http://your-proxy:port'
   ```

4. **DNS ayarlarını değiştirin**
   - Google DNS: 8.8.8.8, 8.8.4.4
   - Cloudflare DNS: 1.1.1.1, 1.0.0.1

### Problem 2: Yavaş Streaming

**Belirtiler:**
- Buffering
- Donmalar
- Düşük kalite

**Çözümler:**

1. **Chunk size'ı artırın**
   ```python
   # config_advanced.py
   CHUNK_SIZE = 256 * 1024  # 256KB
   ```

2. **Buffer size'ı artırın**
   ```python
   BUFFER_SIZE = 2 * 1024 * 1024  # 2MB
   ```

3. **WiFi sinyalini iyileştirin**
   - Router'a yaklaşın
   - 5GHz band kullanın
   - Kanal değiştirin

4. **Worker sayısını artırın**
   ```python
   # config_advanced.py
   WORKERS = 4  # 2'den 4'e
   ```

### Problem 3: LOKKE'de Açılmıyor

**Belirtiler:**
- "Connection refused"
- "Cannot connect to server"
- Boş sayfa

**Çözümler:**

1. **Doğru IP adresini kullanın**
   ```bash
   # Linux/Mac
   ifconfig | grep "inet "
   
   # Windows
   ipconfig
   ```

2. **Port'u kontrol edin**
   ```bash
   # Port 7860 açık mı?
   netstat -an | grep 7860
   ```

3. **Firewall ayarları**
   ```bash
   # Linux
   sudo ufw allow 7860
   
   # Windows
   # Windows Defender Firewall > Inbound Rules > New Rule
   # Port: 7860, TCP
   ```

4. **Doğru endpoint'i kullanın**
   ```
   ✅ http://192.168.1.100:7860/vavoo
   ❌ http://192.168.1.100:7860
   ```

### Problem 4: "Module not found"

**Belirtiler:**
```
ModuleNotFoundError: No module named 'aiohttp'
```

**Çözüm:**
```bash
# Tüm gereksinimleri kur
pip install aiohttp gunicorn

# Veya requirements.txt'den
pip install -r requirements.txt
```

### Problem 5: High CPU/Memory Usage

**Belirtiler:**
- Sistem yavaşlıyor
- Fan sesi
- Donmalar

**Çözümler:**

1. **Worker sayısını azaltın**
   ```python
   WORKERS = 1  # Tek worker
   ```

2. **Cache'i azaltın**
   ```python
   SEGMENT_CACHE_SIZE = 25  # 50'den 25'e
   ```

3. **Max connections sınırlayın**
   ```python
   MAX_CONNECTIONS = 50  # 100'den 50'ye
   ```

---

## İpuçları

### 1. En İyi Performans İçin

**Optimum Ayarlar:**
```python
# config_advanced.py
CHUNK_SIZE = 128 * 1024  # 128KB
BUFFER_SIZE = 1024 * 1024  # 1MB
WORKERS = 2
MAX_CONNECTIONS = 100
SEGMENT_CACHE_SIZE = 50
```

### 2. Mobil Cihazlar İçin

**Mobile-Optimized:**
```python
ENABLE_MOBILE_OPTIMIZATION = True
MOBILE_CHUNK_SIZE = 64 * 1024  # 64KB
MOBILE_BUFFER_SIZE = 512 * 1024  # 512KB
```

### 3. Güvenlik

**Öneriler:**
- Production'da `DEBUG = False` kullanın
- HTTPS kullanın (reverse proxy ile)
- Rate limiting ekleyin
- IP whitelist kullanın

### 4. Monitoring

**Stats Tracking:**
```python
ENABLE_STATS = True
STATS_INTERVAL = 60  # Her dakika

# Stats endpoint
http://localhost:7860/api/stats
```

### 5. Backup Strategy

**Domain Rotation:**
- Primary domain fail olursa backup'lar otomatik devreye girer
- Manuel olarak test edin:
  ```bash
  curl http://localhost:7860/vavoo/bypass?url=https://vavoo.tv
  ```

---

## Gelişmiş Kullanım

### Custom Extractor Eklemek

```python
# extractors/myextractor.py
class MyExtractor:
    @staticmethod
    async def can_handle(url: str) -> bool:
        return 'mysite.com' in url
    
    @staticmethod
    async def extract(url: str) -> dict:
        # Implementation
        return {
            'stream_url': 'https://...',
            'quality': '1080p'
        }
```

### Webhook Notifications

```python
# config_advanced.py
ENABLE_NOTIFICATIONS = True
NOTIFICATION_WEBHOOK = 'https://discord.com/api/webhooks/...'

# Fail olduğunda Discord'a bildirim gönderir
```

### Redis Cache

```python
CACHE_TYPE = 'redis'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
```

---

## Sık Sorulan Sorular

**S: Yasal mı?**
C: Bu yazılım kişisel kullanım içindir. Telif haklarına saygı gösterin.

**S: VPN gerekli mi?**
C: Hayır ama bazı durumlarda yardımcı olabilir.

**S: Kaç stream aynı anda?**
C: Sistem kaynaklarına bağlı. Genelde 5-10 stream sorunsuz.

**S: Recording nasıl çalışır?**
C: DVR modülü FFmpeg kullanır. `DVR_ENABLED = True` yapın.

**S: Güncellemeler nasıl?**
C: GitHub repo'yu takip edin, pull request'leri kabul ediyoruz.

---

## Destek ve Katkı

### Bug Report
GitHub'da issue açın veya pull request gönderin.

### Feature Request
Yeni özellik önerileri için discussion başlatın.

### Contribution
1. Fork edin
2. Feature branch oluşturun
3. Commit edin
4. Push edin
5. Pull request açın

---

**Version:** 2.0 - Advanced Anti-Block Edition  
**Last Updated:** 2026-02-10  
**License:** MIT

---

Made with ❤️ by Community
