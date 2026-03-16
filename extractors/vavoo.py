import asyncio
import logging
import time
import socket
import aiohttp
import json
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from aiohttp_socks import ProxyConnector
from typing import Optional, Dict, Any
import random

logger = logging.getLogger(__name__)

class ExtractorError(Exception):
    pass

class VavooExtractor:
    """Vavoo URL extractor - Gerçek video linkini API'den alır"""
    
    def __init__(self, request_headers: dict, proxies: list = None):
        self.request_headers = request_headers
        self.base_headers = {
            "user-agent": "MediaHubMX/2",
            "accept": "application/json",
            "content-type": "application/json"
        }
        self.session = None
        self.mediaflow_endpoint = "proxy_stream_endpoint"
        self.proxies = proxies or []
        self.resolve_url = "https://vavoo.to/mediahubmx-resolve.json"

    def _get_random_proxy(self):
        return random.choice(self.proxies) if self.proxies else None
        
    async def _get_session(self):
        if self.session is None or self.session.closed:
            timeout = ClientTimeout(total=60, connect=30, sock_read=30)
            proxy = self._get_random_proxy()
            if proxy:
                logger.info(f"Using proxy {proxy} for Vavoo session.")
                connector = ProxyConnector.from_url(proxy)
            else:
                connector = TCPConnector(
                    limit=0,
                    limit_per_host=0,
                    keepalive_timeout=60,
                    enable_cleanup_closed=True,
                    force_close=False,
                    use_dns_cache=True,
                    family=socket.AF_INET
                )

            self.session = ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self.base_headers
            )
        return self.session

    async def extract(self, url: str, **kwargs) -> Dict[str, Any]:
        if "vavoo.to" not in url:
            raise ExtractorError("Not a valid Vavoo URL")
        
        # API'ye POST isteği yap - Güneş TV'nin yaptığı gibi
        session = await self._get_session()
        
        # Request body - Güneş TV'nin kullandığı format
        payload = {
            "language": "tr",
            "region": "TR",
            "url": url,
            "clientVersion": "3.0.3"
        }
        
        logger.info(f"Vavoo API çağrısı yapılıyor: {url}")
        
        try:
            async with session.post(
                self.resolve_url,
                json=payload,
                headers={
                    "User-Agent": "MediaHubMX/2",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Origin": "https://vavoo.to",
                    "Referer": "https://vavoo.to/"
                }
            ) as response:
                
                if response.status != 200:
                    logger.error(f"API hatası: HTTP {response.status}")
                    raise ExtractorError(f"API returned {response.status}")
                
                data = await response.json()
                
                # API'den dönen gerçek video linki
                if "streamUrl" in data:
                    real_url = data["streamUrl"]
                    logger.info(f"Gerçek video linki alındı: {real_url}")
                    
                    # Gerçek video linki için header'lar
                    stream_headers = {
                        "user-agent": "MediaHubMX/2",
                        "referer": "https://vavoo.to/",
                        "origin": "https://vavoo.to"
                    }
                    
                    return {
                        "destination_url": real_url,
                        "request_headers": stream_headers,
                        "mediaflow_endpoint": self.mediaflow_endpoint,
                    }
                else:
                    logger.error("API yanıtında streamUrl bulunamadı")
                    raise ExtractorError("No streamUrl in response")
                    
        except Exception as e:
            logger.error(f"Vavoo çözümleme hatası: {str(e)}")
            raise ExtractorError(f"Vavoo extraction failed: {str(e)}")

    async def extract_m3u(self, m3u_content: str) -> str:
        """M3U dosyasındaki tüm Vavoo linklerini çözümler"""
        lines = m3u_content.split('\n')
        new_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            new_lines.append(line)
            
            # Bir sonraki satır link mi?
            if i + 1 < len(lines) and lines[i+1].startswith('http'):
                url = lines[i+1]
                if 'vavoo.to' in url:
                    try:
                        result = await self.extract(url)
                        # Link satırını değiştir
                        new_lines[-1] = line  # EXTINF satırı aynı kalır
                        new_lines.append(result["destination_url"])  # Gerçek link
                        i += 1  # Bir sonraki satırı atla
                    except Exception as e:
                        logger.error(f"Link çözümlenemedi: {url} - {e}")
                        new_lines.append(url)  # Orijinal linki kullan
                else:
                    new_lines.append(url)
            i += 1
        
        return '\n'.join(new_lines)

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
