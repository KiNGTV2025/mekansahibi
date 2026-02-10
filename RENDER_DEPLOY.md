# 🎨 Render.com Deployment Rehberi - PreProxyVavoo

## 🚀 Hızlı Başlangıç

### Adım 1: GitHub'a Yükle
```bash
cd PreProxyVavoo_optimized
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/preproxy-vavoo.git
git push -u origin main
```

### Adım 2: Render.com'a Git
1. https://render.com → **Sign Up** (GitHub ile)
2. **New +** → **Web Service**
3. **Connect Repository** → GitHub repo seç

### Adım 3: Service Ayarları
```
Name: preproxy-vavoo
Region: Frankfurt  # Avrupa için
Branch: main
Runtime: Docker
Dockerfile Path: ./Dockerfile
Plan: Free
```

### Adım 4: Deploy
**Create Web Service** → Otomatik build başlar ✅

**İlk deploy**: ~5-8 dakika

---

## 📁 Gerekli Dosyalar

```
PreProxyVavoo/
├── Dockerfile         # ✅ Var (optimize edilmiş)
├── render.yaml        # ← Yeni ekle (opsiyonel)
├── app.py
├── requirements.txt
└── ...
```

`render.yaml` opsiyonel ama Infrastructure as Code için önerilen.

---

## ⚙️ Environment Variables

Render dashboard → **Environment** sekmesi:

### Otomatik Eklenenler
```bash
PORT=10000  # Render otomatik atar
```

### Manuel Ekle
```bash
LOG_LEVEL=WARNING
WORKERS=2
DVR_ENABLED=false
MPD_MODE=legacy
PYTHONUNBUFFERED=1
```

### Güvenlik (Önerilen)
```bash
API_PASSWORD=your-secret-password
```

---

## 🎯 render.yaml Kullanımı (Önerilen)

`render.yaml` root dizinine ekle:

```yaml
services:
  - type: web
    name: preproxy-vavoo
    runtime: docker
    region: frankfurt
    plan: free
    dockerfilePath: ./Dockerfile
    envVars:
      - key: LOG_LEVEL
        value: WARNING
      - key: WORKERS
        value: 2
    healthCheckPath: /info
```

**Avantajları**:
- ✅ Infrastructure as Code
- ✅ Tekrar edilebilir deployment
- ✅ Version control

---

## 🌍 Region Seçimi

Render dashboard'da region seçebilirsiniz:

```yaml
# render.yaml'da
region: frankfurt  # ✅ Avrupa için önerilen
region: oregon     # ABD Batı
region: singapore  # Asya
```

---

## 💰 Render Free Tier

**Ücretsiz**:
- ✅ **750 saat/ay** (31 gün × 24 saat = 744 saat)
- ✅ 512MB RAM
- ✅ 0.5 CPU
- ✅ Otomatik SSL
- ✅ Custom domain

**Kısıtlar**:
- ⚠️ **15 dakika inaktiviteden sonra sleep**
- ⚠️ **Cold start**: ~30 saniye
- ⚠️ Aylık 100GB bandwidth

---

## 🐛 Render'ın Sleep Sorunu

### Problem
15 dakika request yoksa app sleep mode'a girer.
Yeni request geldiğinde ~30 saniye cold start.

### Çözümler

#### 1. UptimeRobot ile Keep-Alive ✅ (ÖNERİLEN)
```bash
# https://uptimerobot.com
# Free plan: 50 monitor

# Monitor ekle:
URL: https://your-app.onrender.com/health
Interval: 5 dakika
```

#### 2. Cron Job ile Ping
```bash
# Kendi sunucunuzdan veya GitHub Actions
*/5 * * * * curl https://your-app.onrender.com/health
```

#### 3. Paid Plan ($7/ay)
- ✅ Sleep yok
- ✅ Her zaman aktif
- ✅ Daha fazla kaynak

---

## 🔧 Dockerfile Optimizasyonu (Render için)

Render için Dockerfile zaten optimize edilmiş:

```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder
# ... build dependencies

FROM python:3.11-slim
# ... runtime only
```

**Avantajlar**:
- ✅ Daha küçük image (~700MB)
- ✅ Daha hızlı build
- ✅ Daha az bandwidth

---

## 📊 Monitoring

### Render Dashboard
- **Metrics**: CPU, Memory, Bandwidth
- **Logs**: Real-time logs
- **Events**: Deploy history

### Log Streaming
```bash
# Render CLI ile
render logs -s preproxy-vavoo --tail 100

# Real-time
render logs -s preproxy-vavoo --follow
```

---

## 🔄 Auto-Deploy

### GitHub Integration
Render otomatik GitHub branch'i izler:

```yaml
# render.yaml'da
autoDeploy: true  # ✅ Her push'ta deploy
```

**Workflow**:
```bash
git add .
git commit -m "Update"
git push
# → Render otomatik deploy başlatır
```

---

## 🐛 Troubleshooting

### Problem 1: Build Failed
**Çözüm**:
```bash
# Logs kontrol et
render logs -s preproxy-vavoo

# Dockerfile syntax kontrol et
docker build -t test .
```

### Problem 2: Health Check Failed
**Çözüm**:
```yaml
# render.yaml'da
healthCheckPath: /info  # veya /health

# app.py'de endpoint olduğundan emin ol
@app.route('/info')
def info():
    return jsonify({"status": "ok"})
```

### Problem 3: Out of Memory
**Çözüm**:
```bash
# Worker sayısını azalt
WORKERS=1  # 2 yerine

# Veya Starter plan'a upgrade ($7/ay, 2GB RAM)
```

### Problem 4: Cold Start Çok Yavaş
**Çözüm**:
1. UptimeRobot keep-alive ekle
2. Dockerfile optimize et (multi-stage)
3. Paid plan'a geç ($7/ay, sleep yok)

---

## 💡 Performans İpuçları

### 1. Worker Ayarları
```bash
# Free tier için
WORKERS=2  # Yeterli

# Paid tier için
WORKERS=4  # Daha fazla concurrency
```

### 2. Log Level
```bash
# Production
LOG_LEVEL=WARNING  # ✅ Daha az I/O

# Debug
LOG_LEVEL=INFO
```

### 3. Health Check
```python
# Lightweight endpoint
@app.route('/health')
def health():
    return "OK", 200  # Minimal response
```

---

## 🎯 Render vs Railway vs Fly.io

| Özellik | Render | Railway | Fly.io |
|---------|--------|---------|--------|
| **Free Tier** | 750h/ay | $5 kredi | 3 VM |
| **Sleep** | ⚠️ 15 min | ✅ Yok | ✅ Yok |
| **Setup** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Cold Start** | ~30s | - | - |
| **Best For** | Web apps | Proxy/API | Global |

**Render için TAVSİYE**:
- ✅ Web app'ler için iyi
- ⚠️ Streaming proxy için **Railway veya Fly.io daha iyi**
- ⚠️ Sleep sorunu yüzünden buffering olabilir

---

## 🚨 Önemli: Sleep Sorunu

**Render Free Tier'da**:
- 15 dakika inaktivite → Sleep
- Yeni request → 30 saniye cold start
- **Streaming için problem!**

**Çözüm**:
1. UptimeRobot ile 5 dakikada bir ping ✅
2. Paid plan ($7/ay) - sleep yok
3. **Veya Railway/Fly.io kullan** (sleep yok)

---

## 📝 Deployment Checklist

**Render Deployment**:
- [ ] GitHub repo hazır
- [ ] Dockerfile optimize edilmiş
- [ ] render.yaml eklendi
- [ ] Render hesabı oluşturuldu
- [ ] Repository connected
- [ ] Environment variables ayarlandı
- [ ] Build tamamlandı
- [ ] Health check çalışıyor
- [ ] UptimeRobot monitor eklendi (keep-alive)
- [ ] Test edildi ✅

---

## 🔗 Yararlı Linkler

- **Render Dashboard**: https://dashboard.render.com
- **Render Docs**: https://render.com/docs
- **UptimeRobot**: https://uptimerobot.com (keep-alive için)
- **Community**: https://community.render.com

---

## ✅ Deploy Sonrası

### Test Et
```bash
# Health check
curl https://your-app.onrender.com/info

# Proxy test
curl "https://your-app.onrender.com/proxy/hls/manifest.m3u8?url=STREAM_URL"
```

### UptimeRobot Ekle
1. https://uptimerobot.com → Sign up
2. **Add New Monitor**
   - Type: HTTP(s)
   - URL: `https://your-app.onrender.com/health`
   - Interval: 5 minutes
3. ✅ Save

Bu sayede app 7/24 aktif kalır!

---

## 💰 Maliyet Optimizasyonu

### Free Tier'da Kalma
```bash
# 750 saat = 31.25 gün
# 24/7 çalışsa bile free tier'da kalır!

# Tek dikkat: UptimeRobot ile keep-alive
# → Bandwidth kullanımı artar ama 100GB içinde kalır
```

### Upgrade Gerekirse
**Starter Plan**: $7/ay
- ✅ Sleep yok
- ✅ 512MB → 2GB RAM
- ✅ Priority support

---

## 🎉 Sonuç

**Render.com**:
- ✅ Kolay setup
- ✅ Ücretsiz plan iyi
- ⚠️ **Sleep sorunu var!**
- ⚠️ Streaming için ideal değil

**Tavsiye**:
- Web apps için: **Render ✅**
- Streaming proxy için: **Railway veya Fly.io ✅✅✅**

---

**Not**: `render.yaml` dosyası ile deploy daha kolay! 
Infrastructure as Code FTW! 🚀
