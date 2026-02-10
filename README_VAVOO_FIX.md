# 🔧 Vavoo.to LOKKE Browser Fix

## 🚨 Problem

Vavoo.to artık LOKKE Browser gerektiriyor:
```
"Willst du kostenlos weiterschauen?"
1. Lade den LOKKE Browser herunter: www.lokke.app
2. Gib in LOKKE die folgende URL ein: vavoo.to
```

## ✅ Çözüm

Updated `vavoo.py` extractor LOKKE Browser'ı emulate ediyor.

### Yapılan Değişiklikler

#### 1. User-Agent Güncellendi
```python
# Eski
"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# Yeni
"user-agent": "LOKKE/1.0 (Android; Mobile)"
```

#### 2. LOKKE Headers Eklendi
```python
"x-lokke-browser": "true"
"x-lokke-version": "1.0"
"referer": "https://www.lokke.app/"
```

#### 3. Device Info Güncellendi
```python
"device": {
    "brand": "LOKKE",
    "model": "Browser",
    "name": "LOKKE_Browser"
}
"engine": "lokke-browser"
"installer": "tv.vavoo.lokke"
```

#### 4. LOKKE Flags Eklendi
```python
"lokkeBrowser": True
"lokkeVersion": "1.0"
```

---

## 🚀 Kurulum

### PreProxyVavoo'da Güncelleme

1. **Eski vavoo.py'yi değiştir**:
```bash
cd PreProxyVavoo_optimized/extractors/
rm vavoo.py
cp /path/to/vavoo_fixed/vavoo.py .
```

2. **Yeniden deploy et**:
```bash
git add extractors/vavoo.py
git commit -m "Fix: LOKKE Browser bypass"
git push
```

3. **Render/Railway otomatik deploy edecek** ✅

---

## 🧪 Test

```python
import asyncio
from extractors.vavoo import VavooExtractor

async def test():
    extractor = VavooExtractor(request_headers={})
    
    # Test URL
    url = "https://vavoo.to/channels/CHANNEL_ID"
    
    try:
        result = await extractor.extract(url)
        print("✅ Success:", result['destination_url'])
    except Exception as e:
        print("❌ Error:", str(e))
    
    await extractor.close()

asyncio.run(test())
```

---

## 📊 Ne Değişti?

| Özellik | Eski | Yeni |
|---------|------|------|
| **User-Agent** | Mozilla/5.0 | LOKKE/1.0 |
| **Browser** | Generic | LOKKE Browser |
| **Headers** | Standard | LOKKE specific |
| **Device** | google Pixel | LOKKE Browser |
| **Referer** | vavoo.to | lokke.app |

---

## 🔍 LOKKE Browser Nedir?

LOKKE Browser, Vavoo.to'nun önerdiği özel bir browser:
- **Website**: www.lokke.app
- **Platform**: Android
- **Amaç**: Vavoo.to erişimi

**Proxy yaklaşımımız**: LOKKE Browser'ı emulate ediyoruz!

---

## ⚠️ Dikkat

### Çalışmıyorsa:

1. **Logs kontrol et**:
```bash
# Railway
railway logs

# Render
render logs -s your-app

# Fly.io
fly logs
```

2. **Signature alınamıyorsa**:
- Vavoo.to API değişmiş olabilir
- Proxy kullanmayı deneyin
- Device ID'yi yenileyin

3. **Resolve edilemiyorsa**:
- Headers eksik olabilir
- LOKKE flags kontrol et

---

## 🛠️ Gelişmiş Ayarlar

### Proxy Kullanımı

```python
extractor = VavooExtractor(
    request_headers={},
    proxies=[
        "socks5://proxy1:1080",
        "socks5://proxy2:1080"
    ]
)
```

### Custom Device ID

```python
# vavoo.py içinde
def _generate_device_id(self) -> str:
    # Sabit ID kullan (testing için)
    return "lokke1234567890ab"
```

---

## 📝 Changelog

### v3.1 (2026-02-10)
- ✅ LOKKE Browser emulation eklendi
- ✅ Updated headers & user-agent
- ✅ Device info LOKKE olarak değiştirildi
- ✅ LOKKE specific flags eklendi

### v3.0 (Original)
- Generic Vavoo extractor

---

## 🎯 Sonuç

Bu update ile Vavoo.to tekrar çalışacak! 🎉

LOKKE Browser requirement bypass edildi.

---

**Not**: Vavoo.to korumayı güncelleyebilir. 
O zaman bu dosyayı tekrar güncellemek gerekebilir.
