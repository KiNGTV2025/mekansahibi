# 🚂 Railway.app Deployment Rehberi - PreProxyVavoo

## 📋 Ön Hazırlık

### 1. Gerekli Dosyalar
PreProxyVavoo-Optimized.zip içindeki tüm dosyalar + bu iki yeni dosya:
- ✅ `nixpacks.toml` (Railway config)
- ✅ `.env.example` (Environment variables şablonu)

---

## 🚀 Adım Adım Deployment

### Adım 1: Railway Hesabı
1. https://railway.app adresine git
2. **Start a New Project** tıkla
3. GitHub ile giriş yap (önerilen)

### Adım 2: Repository Oluştur
1. GitHub'da yeni repository oluştur (public veya private)
2. PreProxyVavoo dosyalarını yükle:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/USERNAME/REPO.git
   git push -u origin main
   ```

### Adım 3: Railway'de Deploy
1. Railway dashboard'da **+ New Project**
2. **Deploy from GitHub repo** seç
3. Repository'nizi seçin
4. Railway otomatik detect edecek ve deploy başlayacak

### Adım 4: Environment Variables Ayarla
Railway dashboard'da **Variables** sekmesine git ve ekle:

```bash
LOG_LEVEL=WARNING
WORKERS=2
DVR_ENABLED=false
MPD_MODE=legacy
PYTHONUNBUFFERED=1
```

**Opsiyonel** (güvenlik için önerilen):
```bash
API_PASSWORD=your-secret-password-123
```

### Adım 5: Domain Ayarla
1. **Settings** → **Networking**
2. Railway otomatik bir domain verecek: `your-app.up.railway.app`
3. İsterseniz custom domain ekleyin

---

## ⚙️ Yapılandırma Detayları

### nixpacks.toml Açıklaması
```toml
[phases.setup]
nixPkgs = ["ffmpeg"]  # FFmpeg kurulumu

[phases.install]
cmds = ["pip install -r requirements.txt"]  # Python paketleri

[start]
cmd = "gunicorn ..."  # Gunicorn ile başlat
```

### Neden Dockerfile değil nixpacks?
Railway **nixpacks** kullanıyor (default). Daha hızlı build.
İsterseniz Dockerfile da kullanabilirsiniz.

---

## 🔧 Railway-Specific Optimizasyonlar

### 1. Port Configuration
Railway otomatik `PORT` environment variable atar.
```python
PORT = int(os.environ.get("PORT", 7860))
```
✅ Kodunuzda zaten var, değişiklik gerekmez.

### 2. Health Checks
Railway otomatik health check yapar.
Endpoint: `/` veya `/health` veya `/info`
✅ PreProxyVavoo'da `/info` var, sorun yok.

### 3. Logs
```bash
# Railway CLI ile logları görüntüle
railway logs

# Real-time
railway logs --follow
```

### 4. Resource Limits (Free Tier)
- **CPU**: Shared
- **RAM**: 512MB
- **Bandwidth**: 100GB/ay
- **Build Time**: 10 dakika
- **Uptime**: %99.9

---

## 📊 Monitoring & Debugging

### Railway Dashboard'da
- **Metrics**: CPU, Memory, Network kullanımı
- **Logs**: Real-time application logs
- **Deployments**: Deployment geçmişi

### CLI ile
```bash
# Railway CLI kur
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Logs
railway logs

# Variables
railway variables

# Deploy (manual)
railway up
```

---

## 🐛 Troubleshooting

### Problem 1: Build Failed
**Çözüm**:
```bash
# nixpacks.toml dosyasının root'ta olduğundan emin ol
# requirements.txt'in doğru olduğunu kontrol et
```

### Problem 2: App Crashes
**Çözüm**:
```bash
# Logs kontrol et
railway logs

# Environment variables kontrol et
railway variables
```

### Problem 3: FFmpeg Hatası
**Çözüm**:
```toml
# nixpacks.toml'da ffmpeg var mı kontrol et
[phases.setup]
nixPkgs = ["ffmpeg"]
```

### Problem 4: Port Binding Error
**Çözüm**:
```python
# app.py'de PORT env var kullanıldığından emin ol
PORT = int(os.environ.get("PORT", 7860))
```

---

## 💰 Maliyet (Free Tier Limitleri)

Railway Free Tier:
- ✅ **$5/ay kredi** (kullanıma göre tüketilir)
- ✅ **500 saat/ay** execution time
- ✅ **100GB/ay** bandwidth
- ✅ Unlimited projeler

**Tahmini Kullanım**:
- Idle app: ~$1-2/ay
- Orta kullanım: ~$3-4/ay
- Yoğun kullanım: $5+/ay (ücretli plan gerekir)

---

## 🔄 Güncelleme & Maintenance

### Otomatik Deploy
GitHub'a push → Railway otomatik deploy eder
```bash
git add .
git commit -m "Update"
git push
```

### Manuel Deploy
```bash
railway up
```

### Rollback
Railway dashboard → **Deployments** → Eski versiyonu seç → **Redeploy**

---

## 🎯 Performans İpuçları

### 1. Worker Ayarları
```bash
# Düşük trafik
WORKERS=1

# Orta trafik  
WORKERS=2  # ✅ Önerilen

# Yüksek trafik (ücretli plan)
WORKERS=4
```

### 2. Log Level
```bash
# Production
LOG_LEVEL=WARNING  # ✅ Önerilen

# Debug
LOG_LEVEL=INFO
```

### 3. Timeout
Railway'de max timeout yok ama önerilen:
```bash
--timeout 180  # 3 dakika
```

---

## 📝 Checklist

Deploy öncesi kontrol:

- [ ] nixpacks.toml root dizinde
- [ ] requirements.txt güncel
- [ ] PORT env variable kullanılıyor
- [ ] DVR_ENABLED=false (Railway'de storage yok)
- [ ] API_PASSWORD ayarlandı (güvenlik)
- [ ] GitHub repo hazır
- [ ] Railway hesabı oluşturuldu

---

## 🔗 Yararlı Linkler

- **Railway Dashboard**: https://railway.app/dashboard
- **Railway Docs**: https://docs.railway.app
- **Railway CLI**: https://docs.railway.app/develop/cli
- **Community**: https://discord.gg/railway

---

## ✅ Deploy Sonrası

### Test Et
```bash
# Health check
curl https://your-app.up.railway.app/info

# Proxy test
curl "https://your-app.up.railway.app/proxy/hls/manifest.m3u8?url=STREAM_URL"
```

### Optimize Et
1. Logs kontrol et
2. Metrics izle
3. Environment variables fine-tune et

---

**🎉 Tebrikler! Artık Railway'de çalışıyor!**

Railway URL'nizi IPTV player'ınızda kullanabilirsiniz:
```
https://your-app.up.railway.app/proxy/hls/manifest.m3u8?url=STREAM_URL
```
