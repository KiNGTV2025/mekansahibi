# ✈️ Fly.io Deployment Rehberi

## 🚀 Hızlı Başlangıç

### 1. Fly.io CLI Kur
```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

### 2. Login
```bash
fly auth login
```

### 3. Deploy
```bash
# Proje dizininde
cd PreProxyVavoo_optimized

# fly.toml dosyasını kopyala (yukarıdaki)

# Launch app
fly launch --no-deploy

# Deploy
fly deploy
```

---

## 📁 Gerekli Dosyalar

```
PreProxyVavoo/
├── Dockerfile       # Var (optimize edilmiş)
├── fly.toml         # ← Yeni ekle
├── app.py
├── requirements.txt
└── ...
```

---

## ⚙️ fly.toml Ayarları

```toml
app = "preproxy-vavoo"  # ⚠️ Değiştir: benzersiz olmalı
primary_region = "fra"   # Frankfurt

[http_service]
  internal_port = 7860
  force_https = true
  auto_stop_machines = false  # ✅ Sürekli çalışsın
  min_machines_running = 1    # ✅ En az 1 machine

[[vm]]
  memory_mb = 512  # Free: 256-512MB
```

---

## 🌍 Region Seçimi

```toml
# Avrupa
primary_region = "fra"  # Frankfurt ✅ Önerilen
primary_region = "ams"  # Amsterdam
primary_region = "lhr"  # London

# Amerika
primary_region = "iad"  # Virginia
primary_region = "lax"  # Los Angeles

# Asya
primary_region = "sin"  # Singapore
primary_region = "nrt"  # Tokyo
```

---

## 💰 Fly.io Free Tier

Ücretsiz:
- ✅ **3 shared-cpu VM** (256MB RAM her biri)
- ✅ **160GB bandwidth/ay**
- ✅ Otomatik SSL
- ✅ Global anycast

**Tavsiye**: 1 VM ile başla (512MB), gerekirse 2-3'e çıkar.

---

## 🔧 Komutlar

```bash
# Deploy
fly deploy

# Logs
fly logs

# Status
fly status

# Scale
fly scale memory 512  # MB
fly scale count 2     # Machine sayısı

# Secrets (env vars)
fly secrets set API_PASSWORD=secret123

# SSH
fly ssh console

# Dashboard
fly dashboard
```

---

## 📊 Monitoring

```bash
# Real-time logs
fly logs -f

# Metrics
fly dashboard  # Web'de görüntüle
```

---

## 🐛 Troubleshooting

### Problem: Deploy Failed
```bash
# Logs kontrol et
fly logs

# Dockerfile kontrol et
fly deploy --build-only
```

### Problem: Out of Memory
```bash
# Memory artır
fly scale memory 1024  # 1GB
```

### Problem: App Crashes
```bash
# Health check kontrol et
fly checks list

# Restart
fly apps restart
```

---

## 🎯 Domain Ayarlama

```bash
# Fly otomatik domain verir
# https://preproxy-vavoo.fly.dev

# Custom domain ekle
fly certs add yourdomain.com

# DNS ayarları göster
fly certs show yourdomain.com
```

---

## ✅ Fly.io vs Railway

| Özellik | Fly.io | Railway |
|---------|--------|---------|
| **Free Tier** | 3 VM, 160GB | $5 kredi |
| **Setup** | CLI gerekli | Web-only |
| **Docker** | ✅ Native | ✅ Destekler |
| **Global** | ✅ Anycast | ❌ Single region |
| **Kolay** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Tavsiye**: 
- Kolay deployment → **Railway** ✅
- Global deployment → **Fly.io**
- Free tier optimize → **Railway**

---

## 📝 Checklist

- [ ] flyctl kuruldu
- [ ] fly auth login yapıldı
- [ ] fly.toml oluşturuldu
- [ ] app name unique
- [ ] Dockerfile hazır
- [ ] Deploy başarılı
- [ ] Test edildi

---

**🎉 Tebrikler! Fly.io'da çalışıyor!**

URL: `https://your-app.fly.dev`
