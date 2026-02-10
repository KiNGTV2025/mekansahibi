import asyncio
import logging
import re
import sys
import random
import os
import urllib.parse
from urllib.parse import urlparse, urljoin
import base64
import binascii
import hashlib
import hmac
import json
import ssl
import time
import aiohttp
from aiohttp import web, ClientSession, ClientTimeout, TCPConnector, ClientPayloadError, ServerDisconnectedError, ClientConnectionError
from aiohttp_socks import ProxyConnector
from config import GLOBAL_PROXIES, TRANSPORT_ROUTES, get_proxy_for_url, get_ssl_setting_for_url, API_PASSWORD, check_password, MPD_MODE
from extractors.generic import GenericHLSExtractor, ExtractorError
from services.manifest_rewriter import ManifestRewriter

# Legacy MPD converter
MPDToHLSConverter = None
decrypt_segment = None
if MPD_MODE == "legacy":
    try:
        from utils.mpd_converter import MPDToHLSConverter
        from utils.drm_decrypter import decrypt_segment
        logger = logging.getLogger(__name__)
        logger.info("✅ Legacy MPD modules loaded")
    except ImportError as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"⚠️ MPD_MODE=legacy but modules not found: {e}")

# Extractors
VavooExtractor, DLHDExtractor, VixSrcExtractor, PlaylistBuilder, SportsonlineExtractor = None, None, None, None, None
MixdropExtractor, VoeExtractor, StreamtapeExtractor, OrionExtractor, FreeshotExtractor = None, None, None, None, None
DoodStreamExtractor, FastreamExtractor, FileLionsExtractor, FileMoonExtractor, LuluStreamExtractor = None, None, None, None, None
MaxstreamExtractor, OkruExtractor, StreamWishExtractor, SupervideoExtractor, UqloadExtractor = None, None, None, None, None
VidmolyExtractor, VidozaExtractor, TurboVidPlayExtractor, LiveTVExtractor, F16PxExtractor = None, None, None, None, None

logger = logging.getLogger(__name__)

# Import extractors
try:
    from extractors.freeshot import FreeshotExtractor
    logger.info("✅ FreeshotExtractor loaded")
except ImportError:
    logger.warning("⚠️ FreeshotExtractor not found")

try:
    from extractors.vavoo import VavooExtractor
    logger.info("✅ VavooExtractor loaded")
except ImportError:
    logger.warning("⚠️ VavooExtractor not found")

try:
    from extractors.dlhd import DLHDExtractor
    logger.info("✅ DLHDExtractor loaded")
except ImportError:
    logger.warning("⚠️ DLHDExtractor not found")

try:
    from routes.playlist_builder import PlaylistBuilder
    logger.info("✅ PlaylistBuilder loaded")
except ImportError:
    logger.warning("⚠️ PlaylistBuilder not found")

try:
    from extractors.vixsrc import VixSrcExtractor
    logger.info("✅ VixSrcExtractor loaded")
except ImportError:
    logger.warning("⚠️ VixSrcExtractor not found")

try:
    from extractors.sportsonline import SportsonlineExtractor
    logger.info("✅ SportsonlineExtractor loaded")
except ImportError:
    logger.warning("⚠️ SportsonlineExtractor not found")

try:
    from extractors.mixdrop import MixdropExtractor
    logger.info("✅ MixdropExtractor loaded")
except ImportError:
    logger.warning("⚠️ MixdropExtractor not found")

try:
    from extractors.voe import VoeExtractor
    logger.info("✅ VoeExtractor loaded")
except ImportError:
    logger.warning("⚠️ VoeExtractor not found")

try:
    from extractors.streamtape import StreamtapeExtractor
    logger.info("✅ StreamtapeExtractor loaded")
except ImportError:
    logger.warning("⚠️ StreamtapeExtractor not found")

try:
    from extractors.orion import OrionExtractor
    logger.info("✅ OrionExtractor loaded")
except ImportError:
    logger.warning("⚠️ OrionExtractor not found")

# --- New Extractors ---
try:
    from extractors.doodstream import DoodStreamExtractor
    logger.info("✅ DoodStreamExtractor loaded")
except ImportError:
    logger.warning("⚠️ DoodStreamExtractor not found")

try:
    from extractors.fastream import FastreamExtractor
    logger.info("✅ FastreamExtractor loaded")
except ImportError:
    logger.warning("⚠️ FastreamExtractor not found")

try:
    from extractors.filelions import FileLionsExtractor
    logger.info("✅ FileLionsExtractor loaded")
except ImportError:
    logger.warning("⚠️ FileLionsExtractor not found")

try:
    from extractors.filemoon import FileMoonExtractor
    logger.info("✅ FileMoonExtractor loaded")
except ImportError:
    logger.warning("⚠️ FileMoonExtractor not found")

try:
    from extractors.lulustream import LuluStreamExtractor
    logger.info("✅ LuluStreamExtractor loaded")
except ImportError:
    logger.warning("⚠️ LuluStreamExtractor not found")

try:
    from extractors.maxstream import MaxstreamExtractor
    logger.info("✅ MaxstreamExtractor loaded")
except ImportError:
    logger.warning("⚠️ MaxstreamExtractor not found")

try:
    from extractors.okru import OkruExtractor
    logger.info("✅ OkruExtractor loaded")
except ImportError:
    logger.warning("⚠️ OkruExtractor not found")

try:
    from extractors.streamwish import StreamWishExtractor
    logger.info("✅ StreamWishExtractor loaded")
except ImportError:
    logger.warning("⚠️ StreamWishExtractor not found")

try:
    from extractors.supervideo import SupervideoExtractor
    logger.info("✅ SupervideoExtractor loaded")
except ImportError:
    logger.warning("⚠️ SupervideoExtractor not found")

try:
    from extractors.uqload import UqloadExtractor
    logger.info("✅ UqloadExtractor loaded")
except ImportError:
    logger.warning("⚠️ UqloadExtractor not found")

try:
    from extractors.vidmoly import VidmolyExtractor
    logger.info("✅ VidmolyExtractor loaded")
except ImportError:
    logger.warning("⚠️ VidmolyExtractor not found")

try:
    from extractors.vidoza import VidozaExtractor
    logger.info("✅ VidozaExtractor loaded")
except ImportError:
    logger.warning("⚠️ VidozaExtractor not found")

try:
    from extractors.turbovidplay import TurboVidPlayExtractor
    logger.info("✅ TurboVidPlayExtractor loaded")
except ImportError:
    logger.warning("⚠️ TurboVidPlayExtractor not found")

try:
    from extractors.livetv import LiveTVExtractor
    logger.info("✅ LiveTVExtractor loaded")
except ImportError:
    logger.warning("⚠️ LiveTVExtractor not found")

try:
    from extractors.f16px import F16PxExtractor
    logger.info("✅ F16PxExtractor loaded")
except ImportError:
    logger.warning("⚠️ F16PxExtractor not found")


class HLSProxy:
    """Ultra-fast HLS Proxy with connection pooling and smart caching"""
    
    def __init__(self, ffmpeg_manager=None):
        self.extractors = {}
        self.ffmpeg_manager = ffmpeg_manager
        
        if PlaylistBuilder:
            self.playlist_builder = PlaylistBuilder()
            logger.info("✅ PlaylistBuilder initialized")
        else:
            self.playlist_builder = None
        
        # ✅ ULTRA FAST: Aggressive connection pooling
        self.connector = TCPConnector(
            limit=0,  # Unlimited connections
            limit_per_host=0,  # Unlimited per host
            ttl_dns_cache=600,  # 10 min DNS cache
            enable_cleanup_closed=True,
            force_close=False,  # Reuse connections
            keepalive_timeout=90  # Keep alive 90s
        )
        
        # ✅ SMART CACHING: Multi-level cache
        self.init_cache = {}  # Init segments
        self.segment_cache = {}  # Decrypted segments
        self.segment_cache_ttl = 60  # 60s TTL
        self.playlist_cache = {}  # Playlist cache
        self.playlist_cache_ttl = 10  # 10s TTL
        
        # ✅ PREFETCH: Background download queue
        self.prefetch_tasks = {}
        self.prefetch_lock = asyncio.Lock()
        
        # ✅ SESSION POOL: Reuse sessions
        self.session = None
        self.proxy_sessions = {}
        
        # ✅ PERFORMANCE METRICS
        self.cache_hits = 0
        self.cache_misses = 0

    @staticmethod
    def _compute_key_headers(key_url: str, secret_key: str):
        """Compute X-Key-Timestamp and X-Key-Nonce for /key/ URLs"""
        pattern = r"/key/([^/]+)/(\d+)"
        match = re.search(pattern, key_url)
        if not match:
            return None
        
        resource = match.group(1)
        number = match.group(2)
        ts = int(time.time())
        
        hmac_hash = hmac.new(
            secret_key.encode("utf-8"),
            resource.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        nonce = 0
        for i in range(100000):
            combined = f"{hmac_hash}{resource}{number}{ts}{i}"
            md5_hash = hashlib.md5(combined.encode("utf-8")).hexdigest()
            if int(md5_hash[:4], 16) < 0x1000:
                nonce = i
                break
        
        return ts, nonce

    async def _get_session(self):
        """Get or create shared session with connection pooling"""
        if self.session is None or self.session.closed:
            timeout = ClientTimeout(
                total=120,  # 2 min total
                connect=10,  # 10s connect
                sock_read=60  # 60s read
            )
            self.session = ClientSession(
                connector=self.connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive'
                }
            )
        return self.session

    async def _get_proxy_session(self, url: str):
        """Get proxy-enabled session (cached and reused)"""
        proxy = get_proxy_for_url(url, TRANSPORT_ROUTES, GLOBAL_PROXIES)
        
        if proxy:
            # Check cache
            if proxy in self.proxy_sessions:
                cached = self.proxy_sessions[proxy]
                if not cached.closed:
                    logger.debug(f"♻️ Reusing proxy session: {proxy}")
                    return cached, False
                else:
                    del self.proxy_sessions[proxy]
            
            # Create new
            logger.info(f"🌍 Creating proxy session: {proxy}")
            try:
                connector = ProxyConnector.from_url(
                    proxy,
                    limit=0,
                    limit_per_host=0,
                    keepalive_timeout=90
                )
                timeout = ClientTimeout(total=120, connect=10, sock_read=60)
                session = ClientSession(timeout=timeout, connector=connector)
                self.proxy_sessions[proxy] = session
                return session, False
            except Exception as e:
                logger.warning(f"⚠️ Proxy failed: {e}, fallback to direct")
        
        return await self._get_session(), False

    async def get_extractor(self, url: str, request_headers: dict, host: str = None):
        """Get appropriate extractor for URL"""
        try:
            # 1. Manual selection via 'host' parameter
            if host:
                host = host.lower()
                key = host
                
                if host == "vavoo":
                    if key not in self.extractors:
                        self.extractors[key] = VavooExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host in ["dlhd", "daddylive", "daddyhd"]:
                    key = "dlhd"
                    if key not in self.extractors:
                        self.extractors[key] = DLHDExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "vixsrc":
                    if key not in self.extractors:
                        self.extractors[key] = VixSrcExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host in ["sportsonline", "sportzonline"]:
                    key = "sportsonline"
                    if key not in self.extractors:
                        self.extractors[key] = SportsonlineExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "mixdrop":
                    if key not in self.extractors:
                        self.extractors[key] = MixdropExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "voe":
                    if key not in self.extractors:
                        self.extractors[key] = VoeExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "streamtape":
                    if key not in self.extractors:
                        self.extractors[key] = StreamtapeExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "orion":
                    if key not in self.extractors:
                        self.extractors[key] = OrionExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "freeshot":
                    if key not in self.extractors:
                        self.extractors[key] = FreeshotExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                # --- New Extractors (host selection) ---
                elif host in ["doodstream", "dood", "d000d"]:
                    key = "doodstream"
                    if key not in self.extractors:
                        self.extractors[key] = DoodStreamExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "fastream":
                    if key not in self.extractors:
                        self.extractors[key] = FastreamExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "filelions":
                    if key not in self.extractors:
                        self.extractors[key] = FileLionsExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "filemoon":
                    if key not in self.extractors:
                        self.extractors[key] = FileMoonExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "lulustream":
                    if key not in self.extractors:
                        self.extractors[key] = LuluStreamExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "maxstream":
                    if key not in self.extractors:
                        self.extractors[key] = MaxstreamExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host in ["okru", "ok.ru"]:
                    key = "okru"
                    if key not in self.extractors:
                        self.extractors[key] = OkruExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "streamwish":
                    if key not in self.extractors:
                        self.extractors[key] = StreamWishExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "supervideo":
                    if key not in self.extractors:
                        self.extractors[key] = SupervideoExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "uqload":
                    if key not in self.extractors:
                        self.extractors[key] = UqloadExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "vidmoly":
                    if key not in self.extractors:
                        self.extractors[key] = VidmolyExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host in ["vidoza", "videzz"]:
                    key = "vidoza"
                    if key not in self.extractors:
                        self.extractors[key] = VidozaExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host in ["turbovidplay", "turboviplay", "emturbovid"]:
                    key = "turbovidplay"
                    if key not in self.extractors:
                        self.extractors[key] = TurboVidPlayExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "livetv":
                    if key not in self.extractors:
                        self.extractors[key] = LiveTVExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
                
                elif host == "f16px":
                    if key not in self.extractors:
                        self.extractors[key] = F16PxExtractor(request_headers, proxies=GLOBAL_PROXIES)
                    return self.extractors[key]
            
            # 2. Auto-detection based on URL
            if "vavoo.to" in url:
                key = "vavoo"
                proxy = get_proxy_for_url('vavoo.to', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = VavooExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif any(domain in url for domain in ["daddylive", "dlhd", "daddyhd"]) or re.search(r'watch\.php\?id=\d+', url):
                key = "dlhd"
                proxy = get_proxy_for_url('dlhd.dad', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = DLHDExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif 'vixsrc.to/' in url.lower() and any(x in url for x in ['/movie/', '/tv/', '/iframe/']):
                key = "vixsrc"
                proxy = get_proxy_for_url('vixsrc.to', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = VixSrcExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif any(domain in url for domain in ["sportzonline", "sportsonline"]):
                key = "sportsonline"
                proxy = get_proxy_for_url('sportsonline', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = SportsonlineExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "mixdrop" in url:
                key = "mixdrop"
                proxy = get_proxy_for_url('mixdrop', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = MixdropExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif any(d in url for d in ["voe.sx", "voe.to", "voe.st", "voe.eu", "voe.la", "voe-network.net"]):
                key = "voe"
                proxy = get_proxy_for_url('voe.sx', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = VoeExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "popcdn.day" in url:
                key = "freeshot"
                proxy = get_proxy_for_url('popcdn.day', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = FreeshotExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "streamtape.com" in url or "streamtape.to" in url or "streamtape.net" in url:
                key = "streamtape"
                proxy = get_proxy_for_url('streamtape', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = StreamtapeExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "orionoid.com" in url:
                key = "orion"
                proxy = get_proxy_for_url('orionoid.com', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = OrionExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            # --- New Extractors (URL auto-detection) ---
            elif any(d in url for d in ["doodstream", "d000d.com", "dood.wf", "dood.cx", "dood.la", "dood.so", "dood.pm"]):
                key = "doodstream"
                proxy = get_proxy_for_url('doodstream', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = DoodStreamExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "fastream" in url:
                key = "fastream"
                proxy = get_proxy_for_url('fastream', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = FastreamExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "filelions" in url:
                key = "filelions"
                proxy = get_proxy_for_url('filelions', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = FileLionsExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "filemoon" in url:
                key = "filemoon"
                proxy = get_proxy_for_url('filemoon', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = FileMoonExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "lulustream" in url:
                key = "lulustream"
                proxy = get_proxy_for_url('lulustream', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = LuluStreamExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "maxstream" in url or "uprot.net" in url:
                key = "maxstream"
                proxy = get_proxy_for_url('maxstream', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = MaxstreamExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "ok.ru" in url or "odnoklassniki" in url:
                key = "okru"
                proxy = get_proxy_for_url('ok.ru', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = OkruExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif any(d in url for d in ["streamwish", "swish", "wishfast", "embedwish", "wishembed"]):
                key = "streamwish"
                proxy = get_proxy_for_url('streamwish', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = StreamWishExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "supervideo" in url:
                key = "supervideo"
                proxy = get_proxy_for_url('supervideo', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = SupervideoExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "uqload" in url:
                key = "uqload"
                proxy = get_proxy_for_url('uqload', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = UqloadExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "vidmoly" in url:
                key = "vidmoly"
                proxy = get_proxy_for_url('vidmoly', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = VidmolyExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "vidoza" in url or "videzz" in url:
                key = "vidoza"
                proxy = get_proxy_for_url('vidoza', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = VidozaExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif any(d in url for d in ["turboviplay", "emturbovid", "tuborstb", "javggvideo", "stbturbo", "turbovidhls"]):
                key = "turbovidplay"
                proxy = get_proxy_for_url('turbovidplay', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = TurboVidPlayExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            elif "/e/" in url and any(d in url for d in ["f16px", "embedme", "embedsb", "playersb"]):
                key = "f16px"
                proxy = get_proxy_for_url('f16px', TRANSPORT_ROUTES, GLOBAL_PROXIES)
                proxy_list = [proxy] if proxy else []
                if key not in self.extractors:
                    self.extractors[key] = F16PxExtractor(request_headers, proxies=proxy_list)
                return self.extractors[key]
            
            else:
                # ✅ MODIFICATO: Fallback al GenericHLSExtractor per qualsiasi altro URL
                key = "hls_generic"
                if key not in self.extractors:
                    self.extractors[key] = GenericHLSExtractor(request_headers, proxies=GLOBAL_PROXIES)
                return self.extractors[key]
            
        except (NameError, TypeError) as e:
            raise ExtractorError(f"Extractor not available - module missing: {e}")

    async def handle_proxy_request(self, request):
        """Main proxy handler with ultra-fast optimization"""
        if not check_password(request):
            logger.warning(f"⛔ Unauthorized: {request.remote}")
            return web.Response(status=401, text="Unauthorized")
        
        try:
            target_url = request.query.get('url') or request.query.get('d')
            force_refresh = request.query.get('force', 'false').lower() == 'true'
            redirect_stream = request.query.get('redirect_stream', 'true').lower() == 'true'
            
            if not target_url:
                return web.Response(status=400, text="Missing 'url' parameter")
            
            try:
                target_url = urllib.parse.unquote(target_url)
            except:
                pass
            
            # ✅ CACHE CHECK: Playlist cache for instant response
            cache_key = hashlib.md5(target_url.encode()).hexdigest()
            if not force_refresh and cache_key in self.playlist_cache:
                cached_data, cached_time = self.playlist_cache[cache_key]
                if time.time() - cached_time < self.playlist_cache_ttl:
                    self.cache_hits += 1
                    logger.debug(f"💾 Playlist Cache HIT: {target_url[:50]}")
                    return web.Response(
                        text=cached_data,
                        content_type="application/vnd.apple.mpegurl",
                        headers={
                            "Access-Control-Allow-Origin": "*",
                            "Cache-Control": "no-cache",
                            "X-Cache": "HIT"
                        }
                    )
            
            self.cache_misses += 1
            
            # Extract h_ headers
            combined_headers = dict(request.headers)
            for param_name, param_value in request.query.items():
                if param_name.startswith('h_'):
                    header_name = param_name[2:]
                    combined_headers[header_name] = param_value
            
            logger.info(f"🎬 Proxying: {target_url[:80]}")
            
            extractor = await self.get_extractor(target_url, combined_headers)
            
            try:
                result = await extractor.extract(target_url, force_refresh=force_refresh)
                stream_url = result["destination_url"]
                stream_headers = result.get("request_headers", {})
                
                logger.info(f"✅ Resolved: {stream_url[:80]}")
                
                # Override headers from query
                h_params_found = []
                for param_name, param_value in request.query.items():
                    if param_name.startswith('h_'):
                        header_name = param_name[2:]
                        h_params_found.append(header_name)
                        # Remove duplicates (case-insensitive)
                        keys_to_remove = [k for k in stream_headers.keys() if k.lower() == header_name.lower()]
                        for k in keys_to_remove:
                            del stream_headers[k]
                        stream_headers[header_name] = param_value
                
                if h_params_found:
                    logger.debug(f"📝 Headers overridden: {h_params_found}")
                
                # MPD/DASH handling
                if ".mpd" in stream_url or "dash" in stream_url.lower():
                    if MPD_MODE == "ffmpeg" and self.ffmpeg_manager:
                        logger.info(f"🔄 [FFmpeg Mode] MPD: {stream_url[:80]}")
                        
                        clearkey_param = request.query.get('clearkey')
                        if not clearkey_param:
                            key_id_param = request.query.get('key_id')
                            key_val_param = request.query.get('key')
                            if key_id_param and key_val_param:
                                clearkey_param = f"{key_id_param}:{key_val_param}"
                        
                        playlist_rel_path = await self.ffmpeg_manager.get_stream(
                            stream_url, stream_headers, clearkey=clearkey_param
                        )
                        
                        if playlist_rel_path:
                            scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
                            host = request.headers.get('X-Forwarded-Host', request.host)
                            local_url = f"{scheme}://{host}/ffmpeg_stream/{playlist_rel_path}"
                            
                            master_playlist = (
                                "#EXTM3U\n"
                                "#EXT-X-VERSION:3\n"
                                "#EXT-X-STREAM-INF:BANDWIDTH=6000000,NAME=\"Live\"\n"
                                f"{local_url}\n"
                            )
                            
                            return web.Response(
                                text=master_playlist,
                                content_type="application/vnd.apple.mpegurl",
                                headers={
                                    "Access-Control-Allow-Origin": "*",
                                    "Cache-Control": "no-cache"
                                }
                            )
                    # ... (Legacy MPD logic - unchanged)
                
                # If redirect_stream is False, return JSON with details (MediaFlow style)
                if not redirect_stream:
                    # Build proxy base URL
                    scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
                    host = request.headers.get('X-Forwarded-Host', request.host)
                    proxy_base = f"{scheme}://{host}"
                    
                    mediaflow_endpoint = result.get("mediaflow_endpoint", "hls_proxy")
                    
                    # Determine correct endpoint
                    endpoint = "/proxy/hls/manifest.m3u8"
                    if mediaflow_endpoint == "proxy_stream_endpoint" or ".mp4" in stream_url or ".mkv" in stream_url or ".avi" in stream_url:
                        endpoint = "/proxy/stream"
                    elif ".mpd" in stream_url:
                        endpoint = "/proxy/mpd/manifest.m3u8"
                    
                    # Prepare parameters for JSON
                    q_params = {}
                    api_password = request.query.get('api_password')
                    if api_password:
                        q_params['api_password'] = api_password
                    
                    response_data = {
                        "destination_url": stream_url,
                        "request_headers": stream_headers,
                        "mediaflow_endpoint": mediaflow_endpoint,
                        "mediaflow_proxy_url": f"{proxy_base}{endpoint}",  # Clean URL
                        "query_params": q_params
                    }
                    
                    return web.json_response(response_data)
                
                return await self._proxy_stream(request, stream_url, stream_headers, cache_key)
                
            except ExtractorError as e:
                logger.warning(f"⚠️ Extraction failed, retrying: {e}")
                result = await extractor.extract(target_url, force_refresh=True)
                stream_url = result["destination_url"]
                stream_headers = result.get("request_headers", {})
                return await self._proxy_stream(request, stream_url, stream_headers, cache_key)
        
        except Exception as e:
            logger.error(f"❌ Proxy error: {e}")
            return web.Response(status=500, text=f"Error: {str(e)}")

    async def _proxy_stream(self, request, stream_url, stream_headers, cache_key=None):
        """Proxy stream with smart caching and prefetching"""
        try:
            headers = dict(stream_headers)
            
            # Pass through client headers
            for header in ['range', 'if-none-match', 'if-modified-since']:
                if header in request.headers:
                    headers[header] = request.headers[header]
            
            # Normalize critical headers
            for key in list(headers.keys()):
                lower_key = key.lower()
                if lower_key == 'user-agent':
                    headers['User-Agent'] = headers.pop(key)
                elif lower_key == 'referer':
                    headers['Referer'] = headers.pop(key)
                elif lower_key == 'origin':
                    headers['Origin'] = headers.pop(key)
            
            # Get proxy session
            session, should_close = await self._get_proxy_session(stream_url)
            disable_ssl = get_ssl_setting_for_url(stream_url, TRANSPORT_ROUTES)
            
            try:
                async with session.get(
                    stream_url,
                    headers=headers,
                    ssl=not disable_ssl,
                    allow_redirects=True
                ) as resp:
                    content_type = resp.headers.get('content-type', '')
                    
                    if resp.status not in [200, 206]:
                        error_body = await resp.read()
                        logger.warning(f"⚠️ Upstream error {resp.status}: {stream_url[:80]}")
                        return web.Response(
                            body=error_body,
                            status=resp.status,
                            headers={
                                'Content-Type': content_type,
                                'Access-Control-Allow-Origin': '*'
                            }
                        )
                    
                    # ✅ HLS Manifest handling
                    is_hls = 'mpegurl' in content_type or stream_url.endswith('.m3u8')
                    is_css = stream_url.endswith('.css')
                    
                    if is_hls or is_css:
                        content_bytes = await resp.read()
                        
                        try:
                            manifest_content = content_bytes.decode('utf-8')
                        except UnicodeDecodeError:
                            # Binary masked as CSS
                            logger.warning(f"⚠️ Binary in {stream_url[:80]}")
                            return web.Response(
                                body=content_bytes,
                                status=resp.status,
                                headers={
                                    'Content-Type': 'video/MP2T',
                                    'Access-Control-Allow-Origin': '*'
                                }
                            )
                        
                        # Check if CSS is actually HLS
                        if is_css and not manifest_content.strip().startswith('#EXTM3U'):
                            return web.Response(
                                text=manifest_content,
                                content_type=content_type or 'text/css',
                                headers={'Access-Control-Allow-Origin': '*'}
                            )
                        
                        # Rewrite manifest
                        scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
                        host = request.headers.get('X-Forwarded-Host', request.host)
                        proxy_base = f"{scheme}://{host}"
                        
                        original_url = request.query.get('url', '')
                        api_password = request.query.get('api_password')
                        no_bypass = request.query.get('no_bypass') == '1'
                        
                        rewritten = await ManifestRewriter.rewrite_manifest_urls(
                            manifest_content,
                            stream_url,
                            proxy_base,
                            headers,
                            original_url,
                            api_password,
                            self.get_extractor,
                            no_bypass
                        )
                        
                        # ✅ CACHE: Store playlist for fast re-access
                        if cache_key:
                            self.playlist_cache[cache_key] = (rewritten, time.time())
                            # Limit cache size
                            if len(self.playlist_cache) > 100:
                                oldest = min(self.playlist_cache.keys(), 
                                           key=lambda k: self.playlist_cache[k][1])
                                del self.playlist_cache[oldest]
                        
                        # ✅ PREFETCH: Parse and prefetch first 3 segments
                        asyncio.create_task(self._prefetch_from_playlist(rewritten, headers))
                        
                        return web.Response(
                            text=rewritten,
                            headers={
                                'Content-Type': 'application/vnd.apple.mpegurl',
                                'Content-Disposition': 'attachment; filename="stream.m3u8"',
                                'Access-Control-Allow-Origin': '*',
                                'Cache-Control': 'no-cache',
                                'X-Cache': 'MISS'
                            }
                        )
                    
                    # Normal streaming
                    response_headers = {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
                        'Access-Control-Allow-Headers': 'Range, Content-Type'
                    }
                    
                    for header in ['content-type', 'content-length', 'content-range', 
                                  'accept-ranges', 'last-modified', 'etag']:
                        if header in resp.headers:
                            response_headers[header] = resp.headers[header]
                    
                    # Force TS content type
                    if (stream_url.endswith('.ts') or request.path.endswith('.ts')):
                        if 'video/mp2t' not in response_headers.get('content-type', '').lower():
                            response_headers['Content-Type'] = 'video/MP2T'
                    
                    response = web.StreamResponse(status=resp.status, headers=response_headers)
                    await response.prepare(request)
                    
                    # ✅ OPTIMIZED: Larger chunks for better throughput
                    async for chunk in resp.content.iter_chunked(65536):  # 64KB chunks
                        await response.write(chunk)
                    
                    await response.write_eof()
                    return response
                    
            finally:
                if should_close and session and not session.closed:
                    await session.close()
        
        except (ClientPayloadError, ConnectionResetError, OSError) as e:
            logger.info(f"ℹ️ Client disconnected: {stream_url[:80]}")
            return web.Response(status=499, text="Client disconnected")
        except Exception as e:
            logger.error(f"❌ Stream error: {e}")
            return web.Response(status=500, text=f"Error: {str(e)}")

    async def _prefetch_from_playlist(self, playlist_content: str, headers: dict):
        """Parse playlist and prefetch first 3 segments in background"""
        try:
            lines = playlist_content.strip().split('\n')
            segment_urls = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # This is a segment URL
                if line.startswith('http'):
                    segment_urls.append(line)
                    if len(segment_urls) >= 3:
                        break
            
            if segment_urls:
                logger.debug(f"⚡ Prefetching {len(segment_urls)} segments")
                
                for url in segment_urls:
                    asyncio.create_task(self._prefetch_segment(url, headers))
        
        except Exception as e:
            logger.debug(f"⚠️ Prefetch parse error: {e}")

    async def _prefetch_segment(self, url: str, headers: dict):
        """Prefetch a single segment in background"""
        try:
            cache_key = hashlib.md5(url.encode()).hexdigest()
            
            # Check if already cached
            if cache_key in self.segment_cache:
                return
            
            # Acquire lock to prevent duplicate fetches
            async with self.prefetch_lock:
                if cache_key in self.prefetch_tasks:
                    return  # Already being fetched
                
                self.prefetch_tasks[cache_key] = True
            
            try:
                session = await self._get_session()
                
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        
                        # Store in cache
                        self.segment_cache[cache_key] = {
                            'data': data,
                            'time': time.time(),
                            'content_type': resp.headers.get('Content-Type', 'video/MP2T')
                        }
                        
                        # Limit cache size
                        if len(self.segment_cache) > 50:
                            oldest = min(self.segment_cache.keys(),
                                       key=lambda k: self.segment_cache[k]['time'])
                            del self.segment_cache[oldest]
                        
                        logger.debug(f"✅ Prefetched: {url[-40:]}")
            finally:
                # Remove from prefetch tasks
                async with self.prefetch_lock:
                    if cache_key in self.prefetch_tasks:
                        del self.prefetch_tasks[cache_key]
        
        except Exception as e:
            logger.debug(f"⚠️ Prefetch failed: {e}")

    async def handle_extractor_request(self, request):
        """MediaFlow-Proxy compatible endpoint for stream information"""
        logger.info(f"📥 Extractor Request: {request.url}")
        
        if not check_password(request):
            logger.warning("⛔ Unauthorized extractor request")
            return web.Response(status=401, text="Unauthorized: Invalid API Password")
        
        try:
            # Support both 'url' and 'd' parameters
            url = request.query.get('url') or request.query.get('d')
            
            if not url:
                # Help page with available hosts
                help_response = {
                    "message": "EasyProxy Extractor API",
                    "usage": {
                        "endpoint": "/extractor/video",
                        "parameters": {
                            "url": "(Required) URL to extract. Supports plain text, URL encoded, or Base64.",
                            "host": "(Optional) Force specific extractor (bypass auto-detect).",
                            "redirect_stream": "(Optional) 'true' to redirect to stream, 'false' for JSON.",
                            "api_password": "(Optional) API Password if configured."
                        }
                    },
                    "available_hosts": [
                        "vavoo", "dlhd", "daddylive", "vixsrc", "sportsonline",
                        "mixdrop", "voe", "streamtape", "orion", "freeshot",
                        "doodstream", "dood", "fastream", "filelions", "filemoon",
                        "lulustream", "maxstream", "okru", "streamwish", "supervideo",
                        "uqload", "vidmoly", "vidoza", "turbovidplay", "livetv", "f16px"
                    ],
                    "examples": [
                        f"{request.scheme}://{request.host}/extractor/video?url=https://vavoo.to/channel/123",
                        f"{request.scheme}://{request.host}/extractor/video?host=vavoo&url=https://custom-link.com",
                        f"{request.scheme}://{request.host}/extractor/video?url=BASE64_STRING"
                    ]
                }
                return web.json_response(help_response)
            
            # Decode URL if needed
            try:
                url = urllib.parse.unquote(url)
            except:
                pass
            
            # Base64 Decoding (Try)
            try:
                padded_url = url + '=' * (-len(url) % 4)
                decoded_bytes = base64.b64decode(padded_url, validate=True)
                decoded_str = decoded_bytes.decode('utf-8').strip()
                if decoded_str.startswith('http://') or decoded_str.startswith('https://'):
                    url = decoded_str
                    logger.info(f"🔓 Base64 decoded URL: {url}")
            except Exception:
                pass
            
            host_param = request.query.get('host')
            redirect_stream = request.query.get('redirect_stream', 'false').lower() == 'true'
            
            logger.info(f"🔍 Extracting: {url} (Host: {host_param}, Redirect: {redirect_stream})")
            
            extractor = await self.get_extractor(url, dict(request.headers), host=host_param)
            result = await extractor.extract(url)
            stream_url = result["destination_url"]
            stream_headers = result.get("request_headers", {})
            mediaflow_endpoint = result.get("mediaflow_endpoint", "hls_proxy")
            
            logger.info(f"✅ Extraction success: {stream_url[:50]}... Endpoint: {mediaflow_endpoint}")
            
            # Build proxy URL
            scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
            host = request.headers.get('X-Forwarded-Host', request.host)
            proxy_base = f"{scheme}://{host}"
            
            # Determine correct endpoint
            endpoint = "/proxy/hls/manifest.m3u8"
            if mediaflow_endpoint == "proxy_stream_endpoint" or ".mp4" in stream_url or ".mkv" in stream_url or ".avi" in stream_url:
                endpoint = "/proxy/stream"
            elif ".mpd" in stream_url:
                endpoint = "/proxy/mpd/manifest.m3u8"
            
            encoded_url = urllib.parse.quote(stream_url, safe='')
            header_params = "".join([f"&h_{urllib.parse.quote(key)}={urllib.parse.quote(value)}" for key, value in stream_headers.items()])
            
            # Add api_password if present
            api_password = request.query.get('api_password')
            if api_password:
                header_params += f"&api_password={api_password}"
            
            # Full URL (for redirect only)
            full_proxy_url = f"{proxy_base}{endpoint}?d={encoded_url}{header_params}"
            
            if redirect_stream:
                logger.info(f"↪️ Redirecting to: {full_proxy_url}")
                return web.HTTPFound(full_proxy_url)
            
            # Clean URL (for JSON response)
            q_params = {}
            if api_password:
                q_params['api_password'] = api_password
            
            response_data = {
                "destination_url": stream_url,
                "request_headers": stream_headers,
                "mediaflow_endpoint": mediaflow_endpoint,
                "mediaflow_proxy_url": f"{proxy_base}{endpoint}",
                "query_params": q_params
            }
            
            logger.info(f"✅ Extractor OK: {url} -> {stream_url[:50]}...")
            return web.json_response(response_data)
        
        except Exception as e:
            error_message = str(e).lower()
            is_expected_error = any(x in error_message for x in [
                'not found', 'unavailable', '403', 'forbidden', '502', 
                'bad gateway', 'timeout', 'temporarily unavailable'
            ])
            
            if is_expected_error:
                logger.warning(f"⚠️ Extractor request failed (expected error): {e}")
            else:
                logger.error(f"❌ Error in extractor request: {e}")
                import traceback
                traceback.print_exc()
            
            return web.Response(text=str(e), status=500)

    async def handle_license_request(self, request):
        """Handle DRM license requests (ClearKey and Proxy)"""
        try:
            # 1. Static ClearKey mode
            clearkey_param = request.query.get('clearkey')
            if clearkey_param:
                logger.info(f"🔑 Static ClearKey license request: {clearkey_param}")
                
                try:
                    # Support multiple keys separated by comma
                    key_pairs = clearkey_param.split(',')
                    keys_jwk = []
                    
                    def hex_to_b64url(hex_str):
                        return base64.urlsafe_b64encode(binascii.unhexlify(hex_str)).decode('utf-8').rstrip('=')
                    
                    for pair in key_pairs:
                        if ':' in pair:
                            kid_hex, key_hex = pair.split(':')
                            keys_jwk.append({
                                "kty": "oct",
                                "k": hex_to_b64url(key_hex),
                                "kid": hex_to_b64url(kid_hex),
                                "type": "temporary"
                            })
                    
                    if not keys_jwk:
                        raise ValueError("No valid keys found")
                    
                    jwk_response = {
                        "keys": keys_jwk,
                        "type": "temporary"
                    }
                    
                    logger.info(f"🔑 Serving static ClearKey license with {len(keys_jwk)} keys")
                    return web.json_response(jwk_response)
                
                except Exception as e:
                    logger.error(f"❌ Error generating static ClearKey license: {e}")
                    return web.Response(text="Invalid ClearKey format", status=400)
            
            # 2. License Proxy mode
            license_url = request.query.get('url')
            if not license_url:
                return web.Response(text="Missing url parameter", status=400)
            
            license_url = urllib.parse.unquote(license_url)
            
            # Reconstruct headers
            headers = {}
            for param_name, param_value in request.query.items():
                if param_name.startswith('h_'):
                    header_name = param_name[2:].replace('_', '-')
                    headers[header_name] = param_value
            
            if request.headers.get('Content-Type'):
                headers['Content-Type'] = request.headers.get('Content-Type')
            
            # Read request body (DRM challenge)
            body = await request.read()
            
            logger.info(f"🔐 Proxying License Request to: {license_url}")
            
            proxy = random.choice(GLOBAL_PROXIES) if GLOBAL_PROXIES else None
            connector_kwargs = {}
            if proxy:
                connector_kwargs['proxy'] = proxy
            
            async with ClientSession() as session:
                async with session.request(
                    request.method,
                    license_url,
                    headers=headers,
                    data=body,
                    **connector_kwargs
                ) as resp:
                    response_body = await resp.read()
                    logger.info(f"✅ License response: {resp.status} ({len(response_body)} bytes)")
                    
                    response_headers = {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
                    }
                    
                    if 'Content-Type' in resp.headers:
                        response_headers['Content-Type'] = resp.headers['Content-Type']
                    
                    return web.Response(
                        body=response_body,
                        status=resp.status,
                        headers=response_headers
                    )
        
        except Exception as e:
            logger.error(f"❌ License proxy error: {str(e)}")
            return web.Response(text=f"License error: {str(e)}", status=500)

    async def handle_key_request(self, request):
        """Handle AES-128 key requests"""
        if not check_password(request):
            return web.Response(status=401, text="Unauthorized: Invalid API Password")
        
        # 1. Static key handling
        static_key = request.query.get('static_key')
        if static_key:
            try:
                key_bytes = binascii.unhexlify(static_key)
                return web.Response(
                    body=key_bytes,
                    content_type='application/octet-stream',
                    headers={'Access-Control-Allow-Origin': '*'}
                )
            except Exception as e:
                logger.error(f"❌ Error decoding static key: {e}")
                return web.Response(text="Invalid static key", status=400)
        
        # 2. Remote key proxy
        key_url = request.query.get('key_url')
        if not key_url:
            return web.Response(text="Missing key_url or static_key parameter", status=400)
        
        try:
            try:
                key_url = urllib.parse.unquote(key_url)
            except:
                pass
            
            # Initialize headers from dynamic parameters
            headers = {}
            for param_name, param_value in request.query.items():
                if param_name.startswith('h_'):
                    header_name = param_name[2:].replace('_', '-')
                    if header_name.lower() == 'range':
                        continue
                    headers[header_name] = param_value
            
            logger.info(f"🔑 Fetching AES key from: {key_url}")
            logger.info(f" -> with headers: {headers}")
            
            # Use routing system based on TRANSPORT_ROUTES
            proxy = get_proxy_for_url(key_url, TRANSPORT_ROUTES, GLOBAL_PROXIES)
            connector_kwargs = {}
            if proxy:
                connector_kwargs['proxy'] = proxy
            
            logger.info(f"Using proxy {proxy} for the key request.")
            
            timeout = ClientTimeout(total=30)
            async with ClientSession(timeout=timeout) as session:
                secret_key = headers.pop('X-Secret-Key', None)
                
                # Calculate X-Key-Timestamp and X-Key-Nonce if we have secret_key
                if secret_key and '/key/' in key_url:
                    nonce_result = self._compute_key_headers(key_url, secret_key)
                    if nonce_result:
                        ts, nonce = nonce_result
                        headers['X-Key-Timestamp'] = str(ts)
                        headers['X-Key-Nonce'] = str(nonce)
                        logger.info(f"🔐 Computed nonce headers: ts={ts}, nonce={nonce}")
                    else:
                        logger.warning(f"⚠️ Could not compute nonce headers for {key_url}")
                
                # 'auth' case - URLs containing 'auth' require special headers
                if 'auth' in key_url.lower():
                    logger.info(f"🔐 Detected 'auth' key URL, ensuring special headers are present")
                    if 'X-User-Agent' not in headers:
                        headers['X-User-Agent'] = headers.get('User-Agent', headers.get('user-agent', 'Mozilla/5.0'))
                    
                    logger.info(f"🔐 Auth key headers: Authorization={'***' if headers.get('Authorization') else 'missing'}, X-Channel-Key={headers.get('X-Channel-Key', 'missing')}, X-User-Agent={headers.get('X-User-Agent', 'missing')}")
                
                async with session.get(key_url, headers=headers, **connector_kwargs) as resp:
                    if resp.status == 200 or resp.status == 206:
                        key_data = await resp.read()
                        logger.info(f"✅ AES key fetched successfully: {len(key_data)} bytes")
                        
                        return web.Response(
                            body=key_data,
                            content_type="application/octet-stream",
                            headers={
                                "Access-Control-Allow-Origin": "*",
                                "Access-Control-Allow-Headers": "*",
                                "Cache-Control": "no-cache, no-store, must-revalidate"
                            }
                        )
                    else:
                        logger.error(f"❌ Key fetch failed with status: {resp.status}")
                        
                        # Auto-invalidation logic
                        try:
                            url_param = request.query.get('original_channel_url')
                            if url_param:
                                extractor = await self.get_extractor(url_param, {})
                                if hasattr(extractor, 'invalidate_cache_for_url'):
                                    await extractor.invalidate_cache_for_url(url_param)
                        except Exception as cache_e:
                            logger.error(f"⚠️ Error during automatic cache invalidation: {cache_e}")
                        
                        return web.Response(text=f"Key fetch failed: {resp.status}", status=resp.status)
        
        except Exception as e:
            logger.error(f"❌ Error fetching AES key: {str(e)}")
            return web.Response(text=f"Key error: {str(e)}", status=500)

    async def handle_ts_segment(self, request):
        """Handle .ts segment requests"""
        try:
            segment_name = request.match_info.get('segment')
            base_url = request.query.get('base_url')
            
            if not base_url:
                return web.Response(text="Missing base URL for segment", status=400)
            
            base_url = urllib.parse.unquote(base_url)
            
            if base_url.endswith('/'):
                segment_url = f"{base_url}{segment_name}"
            else:
                if any(ext in base_url for ext in ['.mp4', '.m4s', '.ts', '.m4i', '.m4a', '.m4v']):
                    segment_url = base_url
                else:
                    segment_url = f"{base_url.rsplit('/', 1)[0]}/{segment_name}"
            
            logger.info(f"📦 Proxy Segment: {segment_name}")
            
            return await self._proxy_segment(request, segment_url, {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "referer": base_url
            }, segment_name)
        
        except Exception as e:
            logger.error(f"Error in .ts segment proxy: {str(e)}")
            return web.Response(text=f"Segment error: {str(e)}", status=500)

    async def _proxy_segment(self, request, segment_url, stream_headers, segment_name):
        """Dedicated proxy for .ts segments with Content-Disposition"""
        try:
            headers = dict(stream_headers)
            
            # Pass through client headers
            for header in ['range', 'if-none-match', 'if-modified-since']:
                if header in request.headers:
                    headers[header] = request.headers[header]
            
            proxy = random.choice(GLOBAL_PROXIES) if GLOBAL_PROXIES else None
            connector_kwargs = {}
            if proxy:
                connector_kwargs['proxy'] = proxy
            
            logger.debug(f"📡 [Proxy Segment] Using proxy {proxy} for .ts segment")
            
            timeout = ClientTimeout(total=60, connect=30)
            async with ClientSession(timeout=timeout) as session:
                async with session.get(segment_url, headers=headers, **connector_kwargs) as resp:
                    response_headers = {}
                    for header in ['content-type', 'content-length', 'content-range', 
                                  'accept-ranges', 'last-modified', 'etag']:
                        if header in resp.headers:
                            response_headers[header] = resp.headers[header]
                    
                    # Force content-type and add Content-Disposition for .ts
                    response_headers['Content-Type'] = 'video/MP2T'
                    response_headers['Content-Disposition'] = f'attachment; filename="{segment_name}"'
                    response_headers['Access-Control-Allow-Origin'] = '*'
                    response_headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
                    response_headers['Access-Control-Allow-Headers'] = 'Range, Content-Type'
                    
                    response = web.StreamResponse(
                        status=resp.status,
                        headers=response_headers
                    )
                    await response.prepare(request)
                    
                    async for chunk in resp.content.iter_chunked(8192):
                        await response.write(chunk)
                    
                    await response.write_eof()
                    return response
        
        except Exception as e:
            logger.error(f"Error in segment proxy: {str(e)}")
            return web.Response(text=f"Segment error: {str(e)}", status=500)

    async def handle_playlist_request(self, request):
        """Handle playlist builder requests"""
        if not self.playlist_builder:
            return web.Response(text="❌ Playlist Builder not available - module missing", status=503)
        
        try:
            url_param = request.query.get('url')
            if not url_param:
                return web.Response(text="Missing 'url' parameter", status=400)
            
            if not url_param.strip():
                return web.Response(text="'url' parameter cannot be empty", status=400)
            
            playlist_definitions = [def_.strip() for def_ in url_param.split(';') if def_.strip()]
            if not playlist_definitions:
                return web.Response(text="No valid playlist definition found", status=400)
            
            scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
            host = request.headers.get('X-Forwarded-Host', request.host)
            base_url = f"{scheme}://{host}"
            
            api_password = request.query.get('api_password')
            
            async def generate_response():
                async for line in self.playlist_builder.async_generate_combined_playlist(
                    playlist_definitions, base_url, api_password=api_password
                ):
                    yield line.encode('utf-8')
            
            response = web.StreamResponse(
                status=200,
                headers={
                    'Content-Type': 'application/vnd.apple.mpegurl',
                    'Content-Disposition': 'attachment; filename="playlist.m3u"',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            await response.prepare(request)
            
            async for chunk in generate_response():
                await response.write(chunk)
            
            await response.write_eof()
            return response
        
        except Exception as e:
            logger.error(f"General error in playlist handler: {str(e)}")
            return web.Response(text=f"Error: {str(e)}", status=500)

    def _read_template(self, filename: str) -> str:
        """Helper function to read a template file"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(base_dir, 'templates', filename)
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    async def handle_root(self, request):
        """Serve main index.html page"""
        try:
            html_content = self._read_template('index.html')
            return web.Response(text=html_content, content_type='text/html')
        except Exception as e:
            logger.error(f"❌ Critical error: unable to load 'index.html': {e}")
            return web.Response(
                text="<h1>Error 500</h1><p>Page not found.</p>", 
                status=500, 
                content_type='text/html'
            )

    async def handle_builder(self, request):
        """Handle playlist builder web interface"""
        try:
            html_content = self._read_template('builder.html')
            return web.Response(text=html_content, content_type='text/html')
        except Exception as e:
            logger.error(f"❌ Critical error: unable to load 'builder.html': {e}")
            return web.Response(
                text="<h1>Error 500</h1><p>Unable to load builder interface.</p>", 
                status=500, 
                content_type='text/html'
            )

    async def handle_info_page(self, request):
        """Serve info HTML page"""
        try:
            html_content = self._read_template('info.html')
            return web.Response(text=html_content, content_type='text/html')
        except Exception as e:
            logger.error(f"❌ Critical error: unable to load 'info.html': {e}")
            return web.Response(
                text="<h1>Error 500</h1><p>Unable to load info page.</p>", 
                status=500, 
                content_type='text/html'
            )

    async def handle_favicon(self, request):
        """Serve favicon.ico file"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        favicon_path = os.path.join(base_dir, 'static', 'favicon.ico')
        
        if os.path.exists(favicon_path):
            return web.FileResponse(favicon_path)
        
        return web.Response(status=204)

    async def handle_options(self, request):
        """Handle OPTIONS requests for CORS"""
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
            'Access-Control-Allow-Headers': 'Range, Content-Type',
            'Access-Control-Max-Age': '86400'
        }
        return web.Response(headers=headers)

    async def handle_api_info(self, request):
        """API endpoint returning server information in JSON format"""
        info = {
            "proxy": "HLS Proxy Server",
            "version": "2.5.0",
            "status": "✅ Running",
            "features": [
                "✅ Proxy HLS streams",
                "✅ AES-128 key proxying",
                "✅ Playlist building",
                "✅ Proxy Support (SOCKS5, HTTP/S)",
                "✅ Multi-extractor support",
                "✅ CORS enabled"
            ],
            "extractors_loaded": list(self.extractors.keys()),
            "modules": {
                "playlist_builder": PlaylistBuilder is not None,
                "vavoo_extractor": VavooExtractor is not None,
                "dlhd_extractor": DLHDExtractor is not None,
                "vixsrc_extractor": VixSrcExtractor is not None,
                "sportsonline_extractor": SportsonlineExtractor is not None,
                "mixdrop_extractor": MixdropExtractor is not None,
                "voe_extractor": VoeExtractor is not None,
                "streamtape_extractor": StreamtapeExtractor is not None,
            },
            "proxy_config": {
                "global_proxies": f"{len(GLOBAL_PROXIES)} proxies loaded",
                "transport_routes": f"{len(TRANSPORT_ROUTES)} routing rules configured",
                "routes": [{"url": route['url'], "has_proxy": route['proxy'] is not None} for route in TRANSPORT_ROUTES]
            },
            "endpoints": {
                "/proxy/hls/manifest.m3u8": "Proxy HLS (MFP compatibility) - ?d=<URL>",
                "/proxy/mpd/manifest.m3u8": "Proxy MPD (MFP compatibility) - ?d=<URL>",
                "/proxy/manifest.m3u8": "Proxy Legacy - ?url=<URL>",
                "/key": "Proxy AES-128 keys - ?key_url=<URL>",
                "/playlist": "Playlist builder - ?url=<definitions>",
                "/builder": "Web interface for playlist builder",
                "/segment/{segment}": "Proxy for .ts segments - ?base_url=<URL>",
                "/license": "Proxy DRM licenses (ClearKey/Widevine) - ?url=<URL> or ?clearkey=<id:key>",
                "/info": "HTML page with server information",
                "/api/info": "JSON endpoint with server information"
            },
            "usage_examples": {
                "proxy_hls": "/proxy/hls/manifest.m3u8?d=https://example.com/stream.m3u8",
                "proxy_mpd": "/proxy/mpd/manifest.m3u8?d=https://example.com/stream.mpd",
                "aes_key": "/key?key_url=https://server.com/key.bin",
                "playlist": "/playlist?url=http://example.com/playlist1.m3u8;http://example.com/playlist2.m3u8",
                "custom_headers": "/proxy/hls/manifest.m3u8?d=<URL>&h_Authorization=Bearer%20token"
            },
            "performance": {
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "hit_rate": f"{(self.cache_hits / (self.cache_hits + self.cache_misses) * 100) if (self.cache_hits + self.cache_misses) > 0 else 0:.1f}%"
            }
        }
        return web.json_response(info)

    async def handle_decrypt_segment(self, request):
        """Decrypt fMP4 segments server-side for ClearKey (legacy mode)"""
        if not check_password(request):
            return web.Response(status=401, text="Unauthorized: Invalid API Password")
        
        url = request.query.get('url')
        logger.info(f"🔓 Decrypt Request: {url.split('/')[-1] if url else 'unknown'}")
        
        init_url = request.query.get('init_url')
        key = request.query.get('key')
        key_id = request.query.get('key_id')
        
        if not url or not key or not key_id:
            return web.Response(text="Missing url, key, or key_id", status=400)
        
        if decrypt_segment is None:
            return web.Response(text="Decrypt not available (MPD_MODE is not legacy)", status=503)
        
        # Check cache first
        import time
        cache_key = f"{url}:{key_id}:ts"
        
        if cache_key in self.segment_cache:
            cached_content, cached_time = self.segment_cache[cache_key]
            if time.time() - cached_time < self.segment_cache_ttl:
                logger.info(f"📦 Cache HIT for segment: {url.split('/')[-1]}")
                return web.Response(
                    body=cached_content,
                    status=200,
                    headers={
                        'Content-Type': 'video/MP2T',
                        'Access-Control-Allow-Origin': '*',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive'
                    }
                )
            else:
                del self.segment_cache[cache_key]
        
        try:
            # Reconstruct headers for upstream requests
            headers = {
                'Connection': 'keep-alive',
                'Accept-Encoding': 'identity'
            }
            
            for param_name, param_value in request.query.items():
                if param_name.startswith('h_'):
                    header_name = param_name[2:].replace('_', '-')
                    headers[header_name] = param_value
            
            # Get proxy-enabled session for segment fetches
            segment_session, should_close = await self._get_proxy_session(url)
            
            try:
                # Parallel download of init and media segment
                async def fetch_init():
                    if not init_url:
                        return b""
                    
                    if init_url in self.init_cache:
                        return self.init_cache[init_url]
                    
                    disable_ssl = get_ssl_setting_for_url(init_url, TRANSPORT_ROUTES)
                    try:
                        async with segment_session.get(init_url, headers=headers, ssl=not disable_ssl, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                            if resp.status == 200:
                                content = await resp.read()
                                self.init_cache[init_url] = content
                                return content
                            
                            logger.error(f"❌ Init segment returned status {resp.status}: {init_url}")
                            return None
                    
                    except Exception as e:
                        logger.error(f"❌ Failed to fetch init segment: {e}")
                        return None
                
                async def fetch_segment():
                    disable_ssl = get_ssl_setting_for_url(url, TRANSPORT_ROUTES)
                    try:
                        async with segment_session.get(url, headers=headers, ssl=not disable_ssl, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                            if resp.status == 200:
                                return await resp.read()
                            
                            logger.error(f"❌ Segment returned status {resp.status}: {url}")
                            return None
                    
                    except Exception as e:
                        logger.error(f"❌ Failed to fetch segment: {e}")
                        return None
                
                # Parallel fetch
                init_content, segment_content = await asyncio.gather(fetch_init(), fetch_segment())
            
            finally:
                # Close the session if we created one for proxy
                if should_close and segment_session and not segment_session.closed:
                    await segment_session.close()
            
            if init_content is None and init_url:
                logger.error(f"❌ Failed to fetch init segment")
                return web.Response(status=502)
            
            if segment_content is None:
                logger.error(f"❌ Failed to fetch segment")
                return web.Response(status=502)
            
            init_content = init_content or b""
            
            # Check if we should skip decryption (null key case)
            skip_decrypt = request.query.get('skip_decrypt') == '1'
            
            if skip_decrypt:
                # Null key: just concatenate init + segment without decryption
                logger.info(f"🔓 Skip decrypt mode - remuxing without decryption")
                combined_content = init_content + segment_content
            else:
                # Decrypt with PyCryptodome
                loop = asyncio.get_event_loop()
                combined_content = await loop.run_in_executor(None, decrypt_segment, init_content, segment_content, key_id, key)
            
            # Light REMUX to TS
            ts_content = await self._remux_to_ts(combined_content)
            
            if not ts_content:
                logger.warning("⚠️ Remux failed, serving raw fMP4")
                ts_content = combined_content
                content_type = 'video/mp4'
            else:
                content_type = 'video/MP2T'
                logger.info("⚡ Remuxed fMP4 -> TS")
            
            # Store in cache
            self.segment_cache[cache_key] = (ts_content, time.time())
            
            # Clean old cache entries (keep max 50)
            if len(self.segment_cache) > 50:
                oldest_keys = sorted(self.segment_cache.keys(), key=lambda k: self.segment_cache[k][1])[:20]
                for k in oldest_keys:
                    del self.segment_cache[k]
            
            # Prefetch next segments in background
            self._prefetch_next_segments(url, init_url, key, key_id, headers)
            
            # Send response
            return web.Response(
                body=ts_content,
                status=200,
                headers={
                    'Content-Type': content_type,
                    'Access-Control-Allow-Origin': '*',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }
            )
        
        except Exception as e:
            logger.error(f"❌ Decryption error: {e}")
            return web.Response(status=500, text=f"Decryption failed: {str(e)}")

    def _prefetch_next_segments(self, current_url, init_url, key, key_id, headers):
        """Identify next segments and start background download"""
        try:
            parsed = urllib.parse.urlparse(current_url)
            path = parsed.path
            
            # Find numeric pattern at the end of the path (e.g., segment-1.m4s)
            match = re.search(r'([-_])(\d+)(\.[^.]+)$', path)
            if not match:
                return
            
            separator, current_number, extension = match.groups()
            current_num = int(current_number)
            
            # Prefetch next 3 segments
            for i in range(1, 4):
                next_num = current_num + i
                pattern = f"{separator}{current_number}{re.escape(extension)}$"
                replacement = f"{separator}{next_num}{extension}"
                new_path = re.sub(pattern, replacement, path)
                
                # Reconstruct URL
                next_url = urllib.parse.urlunparse(parsed._replace(path=new_path))
                cache_key = f"{next_url}:{key_id}"
                
                if (cache_key not in self.segment_cache and cache_key not in self.prefetch_tasks):
                    self.prefetch_tasks.add(cache_key)
                    asyncio.create_task(
                        self._fetch_and_cache_segment(next_url, init_url, key, key_id, headers, cache_key)
                    )
        
        except Exception as e:
            logger.warning(f"⚠️ Prefetch error: {e}")

    async def _fetch_and_cache_segment(self, url, init_url, key, key_id, headers, cache_key):
        """Download, decrypt and cache a segment in background"""
        try:
            if decrypt_segment is None:
                return
            
            session = await self._get_session()
            
            # Download Init (use cache if possible)
            init_content = b""
            if init_url:
                if init_url in self.init_cache:
                    init_content = self.init_cache[init_url]
                else:
                    disable_ssl = get_ssl_setting_for_url(init_url, TRANSPORT_ROUTES)
                    try:
                        async with session.get(init_url, headers=headers, ssl=not disable_ssl, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                            if resp.status == 200:
                                init_content = await resp.read()
                                self.init_cache[init_url] = init_content
                    except Exception:
                        pass
            
            # Download Segment
            segment_content = None
            disable_ssl = get_ssl_setting_for_url(url, TRANSPORT_ROUTES)
            try:
                async with session.get(url, headers=headers, ssl=not disable_ssl, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        segment_content = await resp.read()
            except Exception:
                pass
            
            if segment_content:
                # Decrypt
                loop = asyncio.get_event_loop()
                decrypted_content = await loop.run_in_executor(None, decrypt_segment, init_content, segment_content, key_id, key)
                
                import time
                self.segment_cache[cache_key] = (decrypted_content, time.time())
                logger.info(f"📦 Prefetched segment: {url.split('/')[-1]}")
        
        except Exception as e:
            pass
        finally:
            if cache_key in self.prefetch_tasks:
                self.prefetch_tasks.remove(cache_key)

    async def _remux_to_ts(self, content):
        """Convert segments (fMP4) to MPEG-TS using FFmpeg pipe"""
        try:
            cmd = [
                'ffmpeg',
                '-y',
                '-i', 'pipe:0',
                '-c', 'copy',
                '-copyts',
                '-bsf:v', 'h264_mp4toannexb',
                '-bsf:a', 'aac_adtstoasc',
                '-f', 'mpegts',
                'pipe:1'
            ]
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate(input=content)
            
            # Check for data presence regardless of return code
            if len(stdout) > 0:
                if proc.returncode != 0:
                    logger.debug(f"FFmpeg remux finished with code {proc.returncode} but produced output (ignoring). Stderr: {stderr.decode()[:200]}")
                return stdout
            
            if proc.returncode != 0:
                logger.error(f"❌ FFmpeg remux failed: {stderr.decode()}")
                return None
            
            return stdout
        
        except Exception as e:
            logger.error(f"❌ Remux error: {e}")
            return None

    async def handle_generate_urls(self, request):
        """MediaFlow-Proxy compatible endpoint for generating proxy URLs"""
        try:
            data = await request.json()
            
            # Verify password if present in body
            req_password = data.get('api_password')
            if API_PASSWORD and req_password != API_PASSWORD:
                if not check_password(request):
                    logger.warning("⛔ Unauthorized generate_urls request")
                    return web.Response(status=401, text="Unauthorized: Invalid API Password")
            
            urls_to_process = data.get('urls', [])
            
            # Logging
            client_ip = request.remote
            exit_strategy = "IP del Server (Diretto)"
            
            if GLOBAL_PROXIES:
                exit_strategy = f"Proxy Globale Random (Pool di {len(GLOBAL_PROXIES)} proxy)"
            
            logger.info(f"🔄 [Generate URLs] Richiesta da Client IP: {client_ip}")
            logger.info(f" -> Strategia di uscita prevista per lo stream: {exit_strategy}")
            
            if urls_to_process:
                logger.info(f" -> Generazione di {len(urls_to_process)} URL proxy per destinazione: {urls_to_process[0].get('destination_url', 'N/A')}")
            
            generated_urls = []
            
            # Determine proxy base URL
            scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
            host = request.headers.get('X-Forwarded-Host', request.host)
            proxy_base = f"{scheme}://{host}"
            
            for item in urls_to_process:
                dest_url = item.get('destination_url')
                if not dest_url:
                    continue
                
                endpoint = item.get('endpoint', '/proxy/stream')
                req_headers = item.get('request_headers', {})
                
                # Build query params
                encoded_url = urllib.parse.quote(dest_url, safe='')
                params = [f"d={encoded_url}"]
                
                # Add headers as h_ params
                for key, value in req_headers.items():
                    params.append(f"h_{urllib.parse.quote(key)}={urllib.parse.quote(value)}")
                
                # Add password if needed
                if API_PASSWORD:
                    params.append(f"api_password={API_PASSWORD}")
                
                # Build final URL
                query_string = "&".join(params)
                
                if not endpoint.startswith('/'):
                    endpoint = '/' + endpoint
                
                full_url = f"{proxy_base}{endpoint}?{query_string}"
                generated_urls.append(full_url)
            
            return web.json_response({"urls": generated_urls})
        
        except Exception as e:
            logger.error(f"❌ Error generating URLs: {e}")
            return web.Response(text=str(e), status=500)

    async def handle_proxy_ip(self, request):
        """Return public IP address of server (or proxy if configured)"""
        if not check_password(request):
            return web.Response(status=401, text="Unauthorized: Invalid API Password")
        
        try:
            # Use global proxy if configured, otherwise direct connection
            proxy = random.choice(GLOBAL_PROXIES) if GLOBAL_PROXIES else None
            
            # Create dedicated session with configured proxy
            if proxy:
                logger.info(f"🌍 Checking IP via proxy: {proxy}")
                connector = ProxyConnector.from_url(proxy)
            else:
                connector = TCPConnector()
            
            timeout = ClientTimeout(total=10)
            async with ClientSession(timeout=timeout, connector=connector) as session:
                # Use external service to determine public IP
                async with session.get('https://api.ipify.org?format=json') as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return web.json_response(data)
                    else:
                        logger.error(f"❌ Failed to fetch IP: {resp.status}")
                        return web.Response(text="Failed to fetch IP", status=502)
        
        except Exception as e:
            logger.error(f"❌ Error fetching IP: {e}")
            return web.Response(text=str(e), status=500)

    async def cleanup(self):
        """Cleanup resources"""
        try:
            # Cancel prefetch tasks
            for task_id in list(self.prefetch_tasks.keys()):
                async with self.prefetch_lock:
                    if task_id in self.prefetch_tasks:
                        del self.prefetch_tasks[task_id]
            
            # Close sessions
            if self.session and not self.session.closed:
                await self.session.close()
            
            for proxy_url, session in list(self.proxy_sessions.items()):
                if session and not session.closed:
                    await session.close()
            
            self.proxy_sessions.clear()
            
            # Close extractors
            for extractor in self.extractors.values():
                if hasattr(extractor, 'close'):
                    await extractor.close()
            
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")