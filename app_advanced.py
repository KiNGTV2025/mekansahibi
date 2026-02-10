import logging
import sys
import os
import asyncio
import random
import hashlib
import time
from aiohttp import web
import aiohttp

# Aggiungi path corrente per import moduli
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.hls_proxy import HLSProxy
from services.ffmpeg_manager import FFmpegManager
from config import PORT, DVR_ENABLED, RECORDINGS_DIR, MAX_RECORDING_DURATION, RECORDINGS_RETENTION_DAYS

# Only import DVR components if enabled
if DVR_ENABLED:
    from services.recording_manager import RecordingManager
    from routes.recordings import setup_recording_routes

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# 🔐 ANTI-BLOCK FEATURES
class AntiBlockManager:
    """Gelişmiş anti-block ve stealth özellikleri"""
    
    # Rotating User-Agents pool
    USER_AGENTS = [
        # Chrome on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # Chrome on Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        # Firefox
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
        # Edge
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
        # Safari
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        # Mobile
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.101 Mobile Safari/537.36',
    ]
    
    REFERERS = [
        'https://www.google.com/',
        'https://www.bing.com/',
        'https://duckduckgo.com/',
        'https://www.facebook.com/',
        'https://twitter.com/',
    ]
    
    @staticmethod
    def get_random_headers(url: str = None):
        """Rastgele browser headers oluştur"""
        headers = {
            'User-Agent': random.choice(AntiBlockManager.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        # %50 şans ile referer ekle
        if random.random() > 0.5:
            headers['Referer'] = random.choice(AntiBlockManager.REFERERS)
        
        return headers
    
    @staticmethod
    def generate_session_id():
        """Unique session ID oluştur"""
        timestamp = str(time.time())
        random_str = str(random.randint(100000, 999999))
        return hashlib.md5(f"{timestamp}{random_str}".encode()).hexdigest()
    
    @staticmethod
    async def add_random_delay():
        """İnsan benzeri rastgele gecikme ekle"""
        await asyncio.sleep(random.uniform(0.1, 0.5))


# 🚀 DOMAIN ROTATION MANAGER
class DomainRotator:
    """Domain rotasyonu için manager"""
    
    # Vavoo için alternatif domain'ler ve mirror'lar
    VAVOO_DOMAINS = [
        'vavoo.to',
        'vavoo.tv',
        'vavootv.to',
        'vavoo.cc',
    ]
    
    # Proxy servisler (opsiyonel)
    PROXY_SERVICES = [
        'https://api.allorigins.win/raw?url=',
        'https://api.codetabs.com/v1/proxy?quest=',
    ]
    
    def __init__(self):
        self.domain_index = 0
        self.failed_domains = set()
        self.last_success = {}
    
    def get_next_domain(self):
        """Bir sonraki çalışan domain'i al"""
        available = [d for d in self.VAVOO_DOMAINS if d not in self.failed_domains]
        if not available:
            # Tüm domain'ler fail olduysa sıfırla
            self.failed_domains.clear()
            available = self.VAVOO_DOMAINS
        
        domain = available[self.domain_index % len(available)]
        self.domain_index += 1
        return domain
    
    def mark_failed(self, domain: str):
        """Domain'i başarısız olarak işaretle"""
        self.failed_domains.add(domain)
        logging.warning(f"❌ Domain marked as failed: {domain}")
    
    def mark_success(self, domain: str):
        """Domain'i başarılı olarak işaretle"""
        self.last_success[domain] = time.time()
        if domain in self.failed_domains:
            self.failed_domains.remove(domain)
        logging.info(f"✅ Domain working: {domain}")


# 🛡️ ENHANCED HLS PROXY WITH ANTI-BLOCK
class EnhancedHLSProxy(HLSProxy):
    """Anti-block özellikleri eklenmiş HLS Proxy"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.anti_block = AntiBlockManager()
        self.domain_rotator = DomainRotator()
        self.session_cache = {}
    
    async def fetch_with_retry(self, url: str, max_retries: int = 3):
        """Retry ve domain rotation ile fetch"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Rastgele headers kullan
                headers = self.anti_block.get_random_headers(url)
                
                # Session ID cookie ekle
                session_id = self.anti_block.generate_session_id()
                headers['Cookie'] = f'session={session_id}'
                
                # İnsan benzeri gecikme
                if attempt > 0:
                    await self.anti_block.add_random_delay()
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30),
                        allow_redirects=True,
                        ssl=False  # SSL doğrulamasını atla
                    ) as response:
                        if response.status == 200:
                            content = await response.read()
                            logging.info(f"✅ Successfully fetched: {url}")
                            return content
                        else:
                            logging.warning(f"⚠️ HTTP {response.status} for {url}")
                            last_error = f"HTTP {response.status}"
            
            except Exception as e:
                logging.error(f"❌ Attempt {attempt + 1} failed for {url}: {e}")
                last_error = str(e)
                
                # Son deneme değilse devam et
                if attempt < max_retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
        
        raise Exception(f"Failed after {max_retries} attempts: {last_error}")
    
    async def handle_vavoo_bypass(self, request):
        """Vavoo için özel bypass handler"""
        try:
            target_url = request.query.get('url', 'https://vavoo.to')
            
            # Domain rotation dene
            for _ in range(len(self.domain_rotator.VAVOO_DOMAINS)):
                current_domain = self.domain_rotator.get_next_domain()
                
                # URL'deki domain'i değiştir
                if 'vavoo' in target_url:
                    test_url = target_url.replace('vavoo.to', current_domain)
                else:
                    test_url = f'https://{current_domain}'
                
                try:
                    content = await self.fetch_with_retry(test_url)
                    self.domain_rotator.mark_success(current_domain)
                    
                    # HTML içeriğini döndür
                    return web.Response(
                        body=content,
                        content_type='text/html',
                        headers={
                            'Access-Control-Allow-Origin': '*',
                            'Cache-Control': 'no-cache',
                        }
                    )
                
                except Exception as e:
                    logging.error(f"Failed with domain {current_domain}: {e}")
                    self.domain_rotator.mark_failed(current_domain)
                    continue
            
            # Tüm domain'ler başarısız olduysa
            return web.Response(
                status=503,
                text="All Vavoo domains are currently unavailable. Please try again later."
            )
        
        except Exception as e:
            logging.error(f"Error in vavoo bypass: {e}")
            return web.Response(status=500, text=str(e))


def create_app():
    """Crea e configura l'applicazione aiohttp con enhanced features."""
    ffmpeg_manager = FFmpegManager()
    proxy = EnhancedHLSProxy(ffmpeg_manager=ffmpeg_manager)
    
    app = web.Application(client_max_size=1024**3)
    app['ffmpeg_manager'] = ffmpeg_manager
    app.ffmpeg_manager = ffmpeg_manager

    if DVR_ENABLED:
        recording_manager = RecordingManager(
            recordings_dir=RECORDINGS_DIR,
            max_duration=MAX_RECORDING_DURATION,
            retention_days=RECORDINGS_RETENTION_DAYS
        )
        app['recording_manager'] = recording_manager

    # 🆕 YENI BYPASS ROUTE'LARI
    app.router.add_get('/vavoo', proxy.handle_vavoo_bypass)
    app.router.add_get('/vavoo/bypass', proxy.handle_vavoo_bypass)
    
    # Mevcut route'lar
    app.router.add_get('/', proxy.handle_root)
    app.router.add_get('/favicon.ico', proxy.handle_favicon)
    
    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    if not os.path.exists(static_path):
        os.makedirs(static_path)
    app.router.add_static('/static', static_path)
    
    app.router.add_get('/builder', proxy.handle_builder)
    app.router.add_get('/info', proxy.handle_info_page)
    app.router.add_get('/api/info', proxy.handle_api_info)
    app.router.add_get('/key', proxy.handle_key_request)
    app.router.add_get('/proxy/manifest.m3u8', proxy.handle_proxy_request)
    app.router.add_get('/proxy/hls/manifest.m3u8', proxy.handle_proxy_request)
    app.router.add_get('/proxy/mpd/manifest.m3u8', proxy.handle_proxy_request)
    app.router.add_get('/proxy/stream', proxy.handle_proxy_request)
    app.router.add_get('/extractor', proxy.handle_extractor_request)
    app.router.add_get('/extractor/video', proxy.handle_extractor_request)
    app.router.add_get('/proxy/hls/segment.ts', proxy.handle_proxy_request)
    app.router.add_get('/proxy/hls/segment.m4s', proxy.handle_proxy_request)
    app.router.add_get('/proxy/hls/segment.mp4', proxy.handle_proxy_request)
    app.router.add_get('/playlist', proxy.handle_playlist_request)
    app.router.add_get('/segment/{segment}', proxy.handle_ts_segment)
    app.router.add_get('/decrypt/segment.mp4', proxy.handle_decrypt_segment)
    app.router.add_get('/decrypt/segment.ts', proxy.handle_decrypt_segment)
    app.router.add_get('/license', proxy.handle_license_request)
    app.router.add_post('/license', proxy.handle_license_request)
    app.router.add_post('/generate_urls', proxy.handle_generate_urls)

    # FFmpeg stream handler
    async def proxy_hls_stream(request):
        stream_id = request.match_info['stream_id']
        filename = request.match_info['filename']
        file_path = os.path.join("temp_hls", stream_id, filename)

        try:
            if not os.path.abspath(file_path).startswith(os.path.abspath("temp_hls")):
                return web.Response(status=403, text="Access denied")
        except:
            return web.Response(status=403, text="Access denied")

        if hasattr(app, 'ffmpeg_manager'):
            app.ffmpeg_manager.touch_stream(stream_id)

        max_retries = 8
        for retry in range(max_retries):
            if os.path.exists(file_path):
                break
            wait_time = min(0.05 * (2 ** retry), 1.0)
            await asyncio.sleep(wait_time)
        
        if not os.path.exists(file_path):
            return web.Response(status=404, text="Segment not found")

        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Expose-Headers": "*",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "Keep-Alive": "timeout=300, max=1000",
            "X-Accel-Buffering": "no",
        }

        if filename.endswith('.m3u8'):
            try:
                content = ""
                for attempt in range(5):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if content.strip():
                        break
                    await asyncio.sleep(0.1)
                
                if not content.strip():
                    return web.Response(status=503, text="Playlist not ready")
                
                headers['Content-Type'] = 'application/vnd.apple.mpegurl'
                return web.Response(text=content, headers=headers)
            except Exception as e:
                logging.error(f"Error reading playlist {file_path}: {e}")
                return web.Response(status=500, text="Internal Server Error")

        if filename.endswith('.ts'):
            headers['Content-Type'] = 'video/MP2T'
            headers['Accept-Ranges'] = 'bytes'
        
        try:
            stat = os.stat(file_path)
            file_size = stat.st_size
            
            range_header = request.headers.get('Range')
            if range_header:
                range_match = range_header.replace('bytes=', '').split('-')
                start = int(range_match[0]) if range_match[0] else 0
                end = int(range_match[1]) if len(range_match) > 1 and range_match[1] else file_size - 1
                
                headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
                headers['Content-Length'] = str(end - start + 1)
                
                response = web.StreamResponse(status=206, headers=headers)
                await response.prepare(request)
                
                with open(file_path, 'rb') as f:
                    f.seek(start)
                    remaining = end - start + 1
                    chunk_size = 128 * 1024
                    
                    while remaining > 0:
                        chunk = f.read(min(chunk_size, remaining))
                        if not chunk:
                            break
                        await response.write(chunk)
                        remaining -= len(chunk)
                
                await response.write_eof()
                return response
            else:
                headers['Content-Length'] = str(file_size)
                return web.FileResponse(file_path, headers=headers, chunk_size=128*1024)
                
        except Exception as e:
            logging.error(f"Error serving segment {file_path}: {e}")
            return web.Response(status=500, text="Internal Server Error")

    app.router.add_get('/ffmpeg_stream/{stream_id}/{filename}', proxy_hls_stream)
    app.router.add_get('/proxy/ip', proxy.handle_proxy_ip)

    if DVR_ENABLED:
        setup_recording_routes(app, recording_manager)

    app.router.add_route('OPTIONS', '/{tail:.*}', proxy.handle_options)

    async def cleanup_handler(app):
        await proxy.cleanup()
    app.on_cleanup.append(cleanup_handler)

    async def on_startup(app):
        asyncio.create_task(ffmpeg_manager.cleanup_loop())
        if DVR_ENABLED:
            asyncio.create_task(recording_manager.cleanup_loop())
    app.on_startup.append(on_startup)

    async def on_shutdown(app):
        if DVR_ENABLED:
            await recording_manager.shutdown()
    app.on_shutdown.append(on_shutdown)

    return app

app = create_app()

def main():
    """Funzione principale per avviare il server."""
    if sys.platform == 'win32':
        logging.getLogger('asyncio').setLevel(logging.CRITICAL)

    hf_space = os.environ.get('SYSTEM') == 'spaces' or os.environ.get('HF_SPACE', 'false').lower() == 'true'

    print("=" * 60)
    print("🛡️ ADVANCED HLS PROXY - Anti-Block Edition")
    if hf_space:
        print("🚀 HF Space Mode - Stealth Enabled")
        print(f"📡 URL: https://umitm0d-pre.hf.space")
        print("🔐 Features:")
        print("  ✓ User-Agent Rotation")
        print("  ✓ Domain Rotation")
        print("  ✓ Anti-Fingerprinting")
        print("  ✓ SSL Bypass")
        print(f"🔧 Port: {PORT}")
        print("=" * 60)
        print("📝 Vavoo Bypass URLs:")
        print("  • /vavoo - Direct bypass")
        print("  • /vavoo/bypass?url=https://vavoo.to")
        print("=" * 60)
        
        try:
            from gunicorn.app.base import BaseApplication
            
            class HFApplication(BaseApplication):
                def __init__(self, app):
                    self.application = app
                    super().__init__()

                def load_config(self):
                    self.cfg.set("bind", f"0.0.0.0:{PORT}")
                    self.cfg.set("workers", 2)
                    self.cfg.set("worker_class", "aiohttp.GunicornWebWorker")
                    self.cfg.set("timeout", 180)
                    self.cfg.set("keepalive", 60)
                    self.cfg.set("graceful_timeout", 90)
                    self.cfg.set("accesslog", None)
                    self.cfg.set("errorlog", "-")
                    self.cfg.set("loglevel", "warning")
                    self.cfg.set("preload_app", True)
                    self.cfg.set("worker_connections", 1000)
                    self.cfg.set("max_requests", 10000)
                    self.cfg.set("max_requests_jitter", 1000)

                def load(self):
                    return self.application

            HFApplication(app).run()
        except ImportError as e:
            print(f"⚠️ Gunicorn not available: {e}, using aiohttp")
            web.run_app(
                app,
                host='0.0.0.0',
                port=PORT,
                access_log=None,
            )
    else:
        print("🚀 HLS Proxy Server - Advanced (Local Mode)")
        print(f"📡 http://localhost:{PORT}")
        
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            wifi_ip = s.getsockname()[0]
            s.close()
            print(f"📱 http://{wifi_ip}:{PORT} (WiFi/LAN)")
            print(f"💡 LOKKE Browser URL: http://{wifi_ip}:{PORT}/vavoo")
        except Exception as e:
            print(f"⚠️ Could not detect WiFi IP: {e}")
        
        print("=" * 60)
        print("🔗 Available Endpoints:")
        print("  • / - Main page")
        print("  • /vavoo - Vavoo bypass (YENI!)")
        print("  • /builder - Playlist builder")
        print("  • /info - Server info")
        if DVR_ENABLED:
            print("  • /recordings - DVR recordings")
        print("  • /proxy/hls/manifest.m3u8?url=<URL> - Stream proxy")
        print("=" * 60)
        
        web.run_app(app, host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    main()
