import asyncio
import logging
import time
import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from aiohttp_socks import ProxyConnector
from typing import Optional, Dict, Any
import random
import hashlib
import json

logger = logging.getLogger(__name__)

class ExtractorError(Exception):
    pass

class VavooExtractor:
    """Enhanced Vavoo extractor with multiple bypass methods"""
    
    # Multiple API endpoints to try
    API_ENDPOINTS = [
        "https://www.vavoo.tv/api/app/ping",
        "https://api.vavoo.tv/app/ping",
        "https://vavoo.tv/api/app/ping"
    ]
    
    RESOLVE_ENDPOINTS = [
        "https://vavoo.to/mediahubmx-resolve.json",
        "https://api.vavoo.to/mediahubmx-resolve.json",
        "https://www.vavoo.to/mediahubmx-resolve.json"
    ]
    
    def __init__(self, request_headers: dict, proxies: list = None):
        self.request_headers = request_headers
        # Multiple user-agents to rotate
        self.user_agents = [
            "LOKKE/1.0 (Android; Mobile) AppleWebKit/537.36",
            "LOKKE/1.0 CFNetwork/1404.0.5 Darwin/22.3.0",
            "MediaHubMX/2.0 (Android; Mobile)",
            "Vavoo/3.1.21 (Android 13; Pixel)",
        ]
        self.session = None
        self.mediaflow_endpoint = "proxy_stream_endpoint"
        self.proxies = proxies or []

    def _get_random_proxy(self):
        return random.choice(self.proxies) if self.proxies else None
    
    def _get_user_agent(self):
        return random.choice(self.user_agents)
        
    async def _get_session(self):
        if self.session is None or self.session.closed:
            timeout = ClientTimeout(total=60, connect=30, sock_read=30)
            proxy = self._get_random_proxy()
            if proxy:
                logger.info(f"Using proxy {proxy}")
                connector = ProxyConnector.from_url(proxy)
            else:
                connector = TCPConnector(
                    limit=0,
                    limit_per_host=0,
                    keepalive_timeout=60,
                    enable_cleanup_closed=True,
                    force_close=False,
                    use_dns_cache=True,
                    ssl=False  # Disable SSL verification
                )

            self.session = ClientSession(
                timeout=timeout,
                connector=connector,
                headers={'User-Agent': self._get_user_agent()}
            )
        return self.session

    def _generate_device_id(self) -> str:
        """Generate realistic device ID"""
        timestamp = str(int(time.time() * 1000))
        random_str = ''.join(random.choices('0123456789abcdef', k=16))
        return random_str

    async def get_auth_signature(self, retries=5, delay=2) -> Optional[str]:
        """Enhanced signature retrieval with multiple methods"""
        current_time = int(time.time() * 1000)
        device_id = self._generate_device_id()
        
        # Method 1: LOKKE Browser
        data_lokke = {
            "token": "",
            "reason": "app-blur",
            "locale": "de",
            "theme": "dark",
            "metadata": {
                "device": {
                    "type": "Handset",
                    "brand": "LOKKE",
                    "model": "Browser",
                    "name": "LOKKE_Browser",
                    "uniqueId": device_id
                },
                "os": {
                    "name": "android",
                    "version": "13",
                    "abis": ["arm64-v8a"],
                    "host": "android"
                },
                "app": {
                    "platform": "android",
                    "version": "3.1.21",
                    "buildId": "289515000",
                    "engine": "lokke-browser",
                    "signatures": ["6e8a975e3cbf07d5de823a760d4c2547f86c1403105020adee5de67ac510999e"],
                    "installer": "tv.vavoo.lokke"
                },
                "version": {
                    "package": "tv.vavoo.app",
                    "binary": "3.1.21",
                    "js": "3.1.21"
                }
            },
            "appFocusTime": 0,
            "playerActive": False,
            "playDuration": 0,
            "devMode": False,
            "hasAddon": True,
            "castConnected": False,
            "package": "tv.vavoo.app",
            "version": "3.1.21",
            "process": "app",
            "firstAppStart": current_time,
            "lastAppStart": current_time,
            "ipLocation": "",
            "adblockEnabled": True,
            "proxy": {
                "supported": ["ss", "openvpn"],
                "engine": "ss",
                "ssVersion": 1,
                "enabled": True,
                "autoServer": True,
                "id": "de-fra"
            },
            "iap": {"supported": False},
            "lokkeBrowser": True,
            "lokkeVersion": "1.0"
        }
        
        # Method 2: Standard Vavoo App
        data_standard = {
            "token": "",
            "reason": "app-blur",
            "locale": "de",
            "theme": "dark",
            "metadata": {
                "device": {
                    "type": "Handset",
                    "brand": "google",
                    "model": "Pixel",
                    "name": "sdk_gphone64_arm64",
                    "uniqueId": device_id
                },
                "os": {
                    "name": "android",
                    "version": "13",
                    "abis": ["arm64-v8a"],
                    "host": "android"
                },
                "app": {
                    "platform": "android",
                    "version": "3.1.21",
                    "buildId": "289515000",
                    "engine": "hbc85",
                    "signatures": ["6e8a975e3cbf07d5de823a760d4c2547f86c1403105020adee5de67ac510999e"],
                    "installer": "com.android.vending"
                },
                "version": {
                    "package": "tv.vavoo.app",
                    "binary": "3.1.21",
                    "js": "3.1.21"
                }
            },
            "package": "tv.vavoo.app",
            "version": "3.1.21",
            "hasAddon": True,
            "firstAppStart": current_time,
            "lastAppStart": current_time,
        }
        
        methods = [
            ("LOKKE", data_lokke, {
                "user-agent": "LOKKE/1.0 (Android; Mobile)",
                "accept": "application/json",
                "content-type": "application/json; charset=utf-8",
                "accept-encoding": "gzip",
                "x-lokke-browser": "true",
                "x-lokke-version": "1.0"
            }),
            ("Standard", data_standard, {
                "user-agent": "okhttp/4.11.0",
                "accept": "application/json",
                "content-type": "application/json; charset=utf-8",
                "accept-encoding": "gzip"
            }),
            ("MediaHub", data_lokke, {
                "user-agent": "MediaHubMX/2.0",
                "accept": "application/json",
                "content-type": "application/json; charset=utf-8",
                "accept-encoding": "gzip"
            })
        ]
        
        for attempt in range(retries):
            for method_name, data, headers in methods:
                for endpoint in self.API_ENDPOINTS:
                    try:
                        logger.info(f"Attempt {attempt+1}/{retries} - Method: {method_name} - Endpoint: {endpoint}")
                        session = await self._get_session()
                        
                        async with session.post(
                            endpoint,
                            json=data,
                            headers=headers,
                            ssl=False
                        ) as resp:
                            if resp.status == 200:
                                result = await resp.json()
                                addon_sig = result.get("addonSig")
                                
                                if addon_sig:
                                    logger.info(f"✅ SUCCESS with {method_name} at {endpoint}")
                                    return addon_sig
                            else:
                                logger.warning(f"Status {resp.status} for {method_name}")
                                
                    except Exception as e:
                        logger.debug(f"Failed {method_name} at {endpoint}: {str(e)}")
                        continue
            
            # Wait before retry
            if attempt < retries - 1:
                await asyncio.sleep(delay * (attempt + 1))
                # Reset session
                if self.session and not self.session.closed:
                    await self.session.close()
                self.session = None
        
        logger.error("❌ All signature methods failed")
        return None

    async def _resolve_vavoo_link(self, link: str, signature: str) -> Optional[str]:
        """Try multiple resolve methods"""
        
        methods = [
            ("LOKKE", {
                "user-agent": "LOKKE/1.0 (Android; Mobile)",
                "accept": "application/json",
                "content-type": "application/json; charset=utf-8",
                "accept-encoding": "gzip",
                "mediahubmx-signature": signature,
                "x-lokke-browser": "true",
                "referer": "https://www.lokke.app/"
            }, {
                "language": "de",
                "region": "AT",
                "url": link,
                "clientVersion": "3.1.21",
                "lokkeBrowser": True
            }),
            ("MediaHub", {
                "user-agent": "MediaHubMX/2",
                "accept": "application/json",
                "content-type": "application/json; charset=utf-8",
                "accept-encoding": "gzip",
                "mediahubmx-signature": signature
            }, {
                "language": "de",
                "region": "AT",
                "url": link,
                "clientVersion": "3.1.21"
            }),
            ("Standard", {
                "user-agent": "okhttp/4.11.0",
                "accept": "application/json",
                "content-type": "application/json; charset=utf-8",
                "mediahubmx-signature": signature
            }, {
                "language": "de",
                "url": link,
                "clientVersion": "3.1.21"
            })
        ]
        
        for method_name, headers, data in methods:
            for endpoint in self.RESOLVE_ENDPOINTS:
                try:
                    logger.info(f"Resolving with {method_name} at {endpoint}")
                    session = await self._get_session()
                    
                    async with session.post(
                        endpoint,
                        json=data,
                        headers=headers,
                        ssl=False
                    ) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            
                            # Try different response formats
                            url = None
                            if isinstance(result, list) and result:
                                url = result[0].get("url")
                            elif isinstance(result, dict):
                                url = result.get("url")
                            
                            if url:
                                logger.info(f"✅ Resolved with {method_name}: {url}")
                                return url
                        else:
                            logger.warning(f"Status {resp.status} for {method_name}")
                            
                except Exception as e:
                    logger.debug(f"Failed {method_name} at {endpoint}: {str(e)}")
                    continue
        
        logger.error("❌ All resolve methods failed")
        return None

    async def extract(self, url: str, **kwargs) -> Dict[str, Any]:
        if "vavoo.to" not in url:
            raise ExtractorError("Not a valid Vavoo URL")

        logger.info(f"🔍 Extracting Vavoo URL: {url}")
        
        signature = await self.get_auth_signature()
        if not signature:
            raise ExtractorError("Failed to obtain Vavoo signature after all attempts")

        resolved_url = await self._resolve_vavoo_link(url, signature)
        if not resolved_url:
            raise ExtractorError("Failed to resolve Vavoo URL after all attempts")

        stream_headers = {
            "user-agent": self._get_user_agent(),
            "referer": "https://www.lokke.app/",
        }

        return {
            "destination_url": resolved_url,
            "request_headers": stream_headers,
            "mediaflow_endpoint": self.mediaflow_endpoint,
        }

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
