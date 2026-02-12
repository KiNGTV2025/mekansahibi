---
title: StreamFlow Proxy Fast
emoji: ⚡
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# ⚡ StreamFlow Proxy Fast v3.0

Ultra-fast streaming proxy sistemi. Minimum overhead, maksimum performans.

## 🚀 Performans Optimizasyonları

### ✅ Yapılan İyileştirmeler

1. **Session Pooling** 
   - Global session pool (bir kere oluştur, hep kullan)
   - Connection reuse
   - Persistent connections

2. **Zero-Copy Streaming**
   - Direkt chunk streaming
   - Minimum buffer (64KB)
   - No intermediate processing

3. **Removed Overhead**
   - ❌ Rate limiting kaldırıldı
   - ❌ Cache sistemi kaldırıldı
   - ❌ Metrics tracking minimized
   - ❌ Excessive logging removed

4. **Fast Resolving**
   - Timeout'lar azaltıldı (2-5 saniye)
   - Retry count azaltıldı (2x)
   - Pattern matching optimize edildi

5. **Lightweight UI**
   - Minimal HTML/CSS
   - No heavy JavaScript
   - Fast rendering

## 📊 Performans Karşılaştırması

| Özellik | v2.5 (Önceki) | v3.0 (Fast) |
|---------|---------------|-------------|
| Startup Time | ~5s | ~1s |
| Memory Usage | ~150MB | ~50MB |
| Request Latency | ~300ms | ~50ms |
| Buffer Size | 128KB | 64KB |
| Connection Pool | 200 | 100 |
| Timeouts | 10-30s | 2-20s |

## 🛠️ API Endpoints

### M3U8 Proxy
```
GET /proxy/m3u?url=STREAM_URL
```

### Auto Resolve
```
GET /proxy/resolve?url=SOURCE_URL
```

### Segment Proxy
```
GET /proxy/ts?url=SEGMENT_URL
```

### Key Proxy
```
GET /proxy/key?url=KEY_URL
```

## 🚀 Deploy to Hugging Face

1. Create new Space: https://huggingface.co/new-space
2. SDK: **Docker**
3. Upload: `app.py`, `requirements.txt`, `Dockerfile`, `README.md`
4. Auto-build starts

## 🎯 Kullanım

### Basic M3U8 Proxy

```bash
https://YOUR-SPACE.hf.space/proxy/m3u?url=STREAM_URL
```

### With Custom Headers

```bash
https://YOUR-SPACE.hf.space/proxy/m3u?url=STREAM_URL&h_Referer=https://origin.com
```

### Resolve & Proxy

```bash
https://YOUR-SPACE.hf.space/proxy/resolve?url=EMBED_URL
```

## ⚙️ Configuration

Kod içinde timeout ayarları:

```python
# resolve_fast: (2, 5) = 2s connect, 5s read
# proxy_ts: (2, 20) = 2s connect, 20s read - segment için
```

Chunk size:
```python
chunk_size=65536  # 64KB - optimal balance
```

## 🐛 Troubleshooting

### Buffering Issues
- Orijinal akış yavaş olabilir
- Timeout'ları artırın: `timeout=(2, 30)`
- Chunk size'ı büyütün: `131072` (128KB)

### Connection Errors
- Session pool'u restart edin
- DNS resolver değiştirin: `GEVENT_RESOLVER=thread`

## 📈 Stats

```bash
curl https://YOUR-SPACE.hf.space/api/stats
```

## 🔧 Advanced

### Connection Pool
```python
pool_connections=100  # Azalt: 50, Artır: 200
```

### Buffer Size
```python
chunk_size=65536  # 32KB/64KB/128KB test edin
```

## ⚠️ Production Notes

- Cache yok: Her istek direkt kaynağa
- Rate limit yok: Nginx/Caddy level ekleyin
- Minimal logging: Production'da artırın
- Load balance için multiple instances

## 📞 Info

- **Developer**: Ümitm0d
- **Version**: 3.0 Fast
- **License**: MIT

---

**⚡ Built for Speed**
