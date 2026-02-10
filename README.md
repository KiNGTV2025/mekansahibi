---
title: PreProxy Vavoo - Optimized
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# 🚀 PreProxy Vavoo - Optimized v3.0

Ultra-fast HLS proxy server with Vavoo, DLHD support and playlist builder.

## ⚡ Performance Optimizations

### What's Been Improved:

1. **Multi-stage Docker Build** - 40% smaller image
2. **Streaming Optimization** - 128KB chunks (was 64KB)
3. **Worker Configuration** - 2 workers (was 1)
4. **Faster Retry** - Max 1s wait (was 2s)
5. **Minimal Logging** - Less overhead

## 📊 Performance Comparison

| Metric | Original | Optimized |
|--------|----------|-----------|
| Docker Image | ~1.2GB | ~700MB |
| Startup Time | ~8s | ~4s |
| Chunk Size | 64KB | 128KB |
| Workers | 1 | 2 |
| Timeout | 300s | 180s |

## 🚀 Quick Deploy

1. Create Space: https://huggingface.co/new-space
2. SDK: **Docker**
3. Upload all files
4. Auto-build starts

## 📡 Main Endpoints

- `/` - Main page
- `/builder` - Playlist builder
- `/proxy/hls/manifest.m3u8?url=URL` - HLS proxy
- `/info` - Server info

## ⚙️ Environment Variables

```bash
PORT=7860                    # Server port
LOG_LEVEL=WARNING           # Log level
WORKERS=2                   # Gunicorn workers
API_PASSWORD=               # Optional protection
DVR_ENABLED=false          # Recording feature
```

## 🔧 Usage

### Basic Proxy
```
/proxy/hls/manifest.m3u8?url=https://stream.example.com/playlist.m3u8
```

### Vavoo Stream
```
/proxy/hls/manifest.m3u8?url=https://vavoo.to/channels/channel123
```

## 📞 Info

- **Optimized by**: Ümitm0d
- **Version**: 3.0
- **License**: MIT

---

**⚡ Built for Speed**
