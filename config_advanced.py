import os
from pathlib import Path

# ===========================
# 🌐 SERVER CONFIGURATION
# ===========================
PORT = int(os.environ.get('PORT', 7860))
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

# ===========================
# 🛡️ ANTI-BLOCK SETTINGS
# ===========================
ENABLE_ANTI_BLOCK = True
ENABLE_DOMAIN_ROTATION = True
ENABLE_USER_AGENT_ROTATION = True
ENABLE_SSL_BYPASS = True

# Request timeout settings
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Rate limiting (to avoid detection)
MIN_REQUEST_DELAY = 0.1  # seconds
MAX_REQUEST_DELAY = 0.5  # seconds

# ===========================
# 🔐 PROXY SETTINGS
# ===========================
# Enable external proxy support (optional)
USE_EXTERNAL_PROXY = os.environ.get('USE_EXTERNAL_PROXY', 'false').lower() == 'true'
EXTERNAL_PROXY_URL = os.environ.get('EXTERNAL_PROXY_URL', '')

# ===========================
# 📺 VAVOO SPECIFIC SETTINGS
# ===========================
VAVOO_PRIMARY_DOMAIN = 'vavoo.to'
VAVOO_BACKUP_DOMAINS = [
    'vavoo.tv',
    'vavootv.to',
    'vavoo.cc',
]

# Cache settings for domain status
DOMAIN_CACHE_DURATION = 300  # 5 minutes
MAX_FAILED_ATTEMPTS = 3  # Before marking domain as failed

# ===========================
# 🎬 STREAMING SETTINGS
# ===========================
CHUNK_SIZE = 128 * 1024  # 128KB chunks for streaming
BUFFER_SIZE = 1024 * 1024  # 1MB buffer
MAX_CONNECTIONS = 100

# HLS/DASH settings
ENABLE_HLS_PROXY = True
ENABLE_DASH_PROXY = True
ENABLE_SEGMENT_CACHING = True

SEGMENT_CACHE_SIZE = 50  # Number of segments to cache
SEGMENT_CACHE_DURATION = 600  # 10 minutes

# ===========================
# 📹 DVR/RECORDING SETTINGS
# ===========================
DVR_ENABLED = os.environ.get('DVR_ENABLED', 'false').lower() == 'true'
RECORDINGS_DIR = Path(os.environ.get('RECORDINGS_DIR', 'recordings'))
MAX_RECORDING_DURATION = int(os.environ.get('MAX_RECORDING_DURATION', 14400))  # 4 hours
RECORDINGS_RETENTION_DAYS = int(os.environ.get('RECORDINGS_RETENTION_DAYS', 7))

# Create recordings directory if enabled
if DVR_ENABLED and not RECORDINGS_DIR.exists():
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

# ===========================
# 🔧 ADVANCED SETTINGS
# ===========================
# FFmpeg settings
FFMPEG_ENABLED = True
FFMPEG_TIMEOUT = 300  # 5 minutes
FFMPEG_QUALITY = 'copy'  # or 'high', 'medium', 'low'

# DRM/Encryption
ENABLE_DRM_DECRYPTION = True
ENABLE_AES_DECRYPTION = True

# Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_REQUESTS = DEBUG  # Log all requests in debug mode

# Security
ENABLE_CORS = True
ALLOWED_ORIGINS = ['*']  # Restrict in production
MAX_REQUEST_SIZE = 1024 * 1024 * 1024  # 1GB

# ===========================
# 🚀 PERFORMANCE SETTINGS
# ===========================
# Worker settings (for Gunicorn)
WORKERS = int(os.environ.get('WORKERS', 2))
WORKER_CLASS = 'aiohttp.GunicornWebWorker'
WORKER_CONNECTIONS = 1000
KEEPALIVE = 60

# Connection pooling
CONNECTION_POOL_SIZE = 100
CONNECTION_POOL_MAXSIZE = 200

# ===========================
# 📊 MONITORING & STATS
# ===========================
ENABLE_STATS = True
STATS_INTERVAL = 60  # 1 minute
ENABLE_HEALTH_CHECK = True

# ===========================
# 🎨 UI SETTINGS
# ===========================
THEME = 'dark'  # or 'light'
SHOW_BANNER = True
CUSTOM_TITLE = 'Advanced HLS Proxy - Anti-Block Edition'

# ===========================
# 🔍 EXTRACTOR SETTINGS
# ===========================
EXTRACTORS = [
    'vavoo',
    'streamwish',
    'filemoon',
    'doodstream',
    'mixdrop',
    'vidoza',
    'streamtape',
    'generic',
]

ENABLE_AUTO_EXTRACTOR_DETECTION = True
EXTRACTOR_TIMEOUT = 30

# ===========================
# 💾 CACHE SETTINGS
# ===========================
ENABLE_CACHE = True
CACHE_TYPE = 'memory'  # or 'redis', 'memcached'
CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
CACHE_THRESHOLD = 500  # max items

# ===========================
# 📱 MOBILE OPTIMIZATION
# ===========================
ENABLE_MOBILE_OPTIMIZATION = True
MOBILE_CHUNK_SIZE = 64 * 1024  # 64KB for mobile
MOBILE_BUFFER_SIZE = 512 * 1024  # 512KB for mobile

# ===========================
# 🌍 CDN & PROXY SERVICES
# ===========================
CDN_ENABLED = False
CDN_URL = os.environ.get('CDN_URL', '')

# Cloudflare settings
CLOUDFLARE_BYPASS = True
CLOUDFLARE_TIMEOUT = 30

# ===========================
# 🔔 NOTIFICATIONS
# ===========================
ENABLE_NOTIFICATIONS = False
NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL', '')
NOTIFICATION_WEBHOOK = os.environ.get('NOTIFICATION_WEBHOOK', '')

# ===========================
# 🐛 DEBUG & DEVELOPMENT
# ===========================
if DEBUG:
    print("=" * 60)
    print("⚠️ DEBUG MODE ENABLED")
    print(f"Port: {PORT}")
    print(f"DVR: {DVR_ENABLED}")
    print(f"Anti-Block: {ENABLE_ANTI_BLOCK}")
    print(f"Domain Rotation: {ENABLE_DOMAIN_ROTATION}")
    print("=" * 60)

# ===========================
# 🎯 FEATURE FLAGS
# ===========================
FEATURES = {
    'anti_block': ENABLE_ANTI_BLOCK,
    'domain_rotation': ENABLE_DOMAIN_ROTATION,
    'user_agent_rotation': ENABLE_USER_AGENT_ROTATION,
    'ssl_bypass': ENABLE_SSL_BYPASS,
    'hls_proxy': ENABLE_HLS_PROXY,
    'dash_proxy': ENABLE_DASH_PROXY,
    'dvr': DVR_ENABLED,
    'ffmpeg': FFMPEG_ENABLED,
    'drm_decryption': ENABLE_DRM_DECRYPTION,
    'cache': ENABLE_CACHE,
    'stats': ENABLE_STATS,
    'mobile_optimization': ENABLE_MOBILE_OPTIMIZATION,
}

def get_feature_status():
    """Feature durumunu döndür"""
    return {k: '✅' if v else '❌' for k, v in FEATURES.items()}

def print_config():
    """Config bilgilerini yazdır"""
    print("\n" + "=" * 60)
    print("📋 CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"Server Port: {PORT}")
    print(f"Debug Mode: {DEBUG}")
    print(f"DVR Enabled: {DVR_ENABLED}")
    print("\nFeatures:")
    for feature, status in get_feature_status().items():
        print(f"  {status} {feature.replace('_', ' ').title()}")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    print_config()
