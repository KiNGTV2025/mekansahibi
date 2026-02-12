from gevent import monkey
monkey.patch_all()

from flask import Flask, request, Response, render_template_string, jsonify
import requests
from urllib.parse import urlparse, urljoin, quote, unquote
import re
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import logging

# Minimal logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'streamflow-fast')

# Basit metrikler
metrics = {
    'total_requests': 0,
    'active_streams': 0,
    'start_time': time.time()
}

# Minimal HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StreamFlow Proxy - Fast</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --bg: #0f172a;
            --card: #1e293b;
            --text: #f1f5f9;
            --border: #334155;
            --success: #22c55e;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .header {
            text-align: center;
            margin-bottom: 3rem;
            padding-top: 2rem;
        }
        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .logo-icon {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            width: 60px;
            height: 60px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
            color: white;
        }
        .logo-text {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .badge {
            display: inline-block;
            background: rgba(34, 197, 94, 0.2);
            color: var(--success);
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-left: 0.5rem;
        }
        .card {
            background: var(--card);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid var(--border);
        }
        .card-title {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin-bottom: 1.5rem;
            font-size: 1.3rem;
        }
        .input-group {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .input {
            flex: 1;
            background: rgba(30, 41, 59, 0.8);
            border: 2px solid var(--border);
            border-radius: 10px;
            padding: 0.9rem 1.2rem;
            color: var(--text);
            font-size: 0.95rem;
        }
        .input:focus {
            outline: none;
            border-color: var(--primary);
        }
        .btn {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            border: none;
            padding: 0.9rem 1.8rem;
            border-radius: 10px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        .btn:hover { opacity: 0.9; }
        .endpoints {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
        }
        .endpoint {
            background: rgba(30, 41, 59, 0.5);
            border-radius: 10px;
            padding: 1.2rem;
            border: 1px solid var(--border);
        }
        .endpoint-title {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            margin-bottom: 0.6rem;
            font-weight: 600;
        }
        .endpoint-url {
            background: rgba(15, 23, 42, 0.8);
            padding: 0.6rem;
            border-radius: 6px;
            font-family: monospace;
            font-size: 0.8rem;
            color: #cbd5e1;
            word-break: break-all;
            margin-top: 0.5rem;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }
        .stat {
            text-align: center;
            padding: 1.2rem;
            background: rgba(99, 102, 241, 0.1);
            border-radius: 12px;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-label {
            color: #94a3b8;
            font-size: 0.8rem;
            text-transform: uppercase;
        }
        .footer {
            text-align: center;
            margin-top: 3rem;
            padding: 1.5rem;
            border-top: 1px solid var(--border);
            color: #64748b;
            font-size: 0.85rem;
        }
        @media (max-width: 768px) {
            .container { padding: 1rem; }
            .input-group { flex-direction: column; }
            .endpoints { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <div class="logo-icon"><i class="fas fa-bolt"></i></div>
                <h1 class="logo-text">StreamFlow Fast<span class="badge">v3.0</span></h1>
            </div>
            <p style="color: #94a3b8;">Ultra-fast streaming proxy</p>
        </div>

        <div class="card">
            <h2 class="card-title">
                <i class="fas fa-play-circle"></i>
                Quick Proxy
            </h2>
            <div class="input-group">
                <input type="text" 
                       class="input" 
                       id="url" 
                       placeholder="Enter stream URL..."
                       value="">
                <button class="btn" onclick="go()">
                    <i class="fas fa-rocket"></i>
                    Proxy
                </button>
            </div>
        </div>

        <div class="card">
            <h2 class="card-title">
                <i class="fas fa-plug"></i>
                API Endpoints
            </h2>
            <div class="endpoints">
                <div class="endpoint">
                    <div class="endpoint-title">
                        <i class="fas fa-stream"></i>
                        M3U8 Proxy
                    </div>
                    <div class="endpoint-url">/proxy/m3u?url=URL</div>
                </div>
                <div class="endpoint">
                    <div class="endpoint-title">
                        <i class="fas fa-wrench"></i>
                        Auto Resolve
                    </div>
                    <div class="endpoint-url">/proxy/resolve?url=URL</div>
                </div>
                <div class="endpoint">
                    <div class="endpoint-title">
                        <i class="fas fa-file-video"></i>
                        Segment Proxy
                    </div>
                    <div class="endpoint-url">/proxy/ts?url=URL</div>
                </div>
            </div>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-number" id="requests">0</div>
                <div class="stat-label">Requests</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="streams">0</div>
                <div class="stat-label">Active</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="uptime">0h</div>
                <div class="stat-label">Uptime</div>
            </div>
        </div>

        <div class="footer">
            <p>StreamFlow Fast v3.0 • Ultra Performance Edition</p>
            <p style="margin-top: 0.5rem;"><i class="fas fa-code"></i> by Ümitm0d</p>
        </div>
    </div>

    <script>
        function go() {
            const url = document.getElementById('url').value.trim();
            if (!url) { alert('Enter URL'); return; }
            window.open(`/proxy/resolve?url=${encodeURIComponent(url)}`, '_blank');
        }
        document.getElementById('url').addEventListener('keypress', e => {
            if (e.key === 'Enter') go();
        });
        async function update() {
            try {
                const r = await fetch('/api/stats');
                const d = await r.json();
                document.getElementById('requests').textContent = d.requests;
                document.getElementById('streams').textContent = d.streams;
                document.getElementById('uptime').textContent = d.uptime + 'h';
            } catch(e) {}
        }
        update();
        setInterval(update, 10000);
    </script>
</body>
</html>
'''

# Session pool - bir kere oluştur, hep kullan
SESSION_POOL = None

def get_session():
    """Global session pool"""
    global SESSION_POOL
    if SESSION_POOL is None:
        SESSION_POOL = requests.Session()
        retry = Retry(total=2, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(
            pool_connections=100,
            pool_maxsize=100,
            max_retries=retry,
            pool_block=False
        )
        SESSION_POOL.mount('http://', adapter)
        SESSION_POOL.mount('https://', adapter)
    return SESSION_POOL

# Pattern'ler - compile edilmiş
PATTERNS = {
    'channel_key': re.compile(r'channelKey\s*=\s*"([^"]*)"'),
    'auth_ts': re.compile(r'authTs\s*=\s*"([^"]*)"'),
    'auth_rnd': re.compile(r'authRnd\s*=\s*"([^"]*)"'),
    'auth_sig': re.compile(r'authSig\s*=\s*"([^"]*)"'),
    'auth_host': re.compile(r'\}\s*fetchWithRetry\(\s*[\'"]([^\'"]*)[\'"]'),
    'server_lookup': re.compile(r'n\s+fetchWithRetry\(\s*[\'"]([^\'"]*)[\'"]'),
    'host': re.compile(r'm3u8\s*=.*?[\'"]([^\'"]*)[\'"]'),
    'iframe': re.compile(r'iframe\s+src=[\'"]([^\'"]+)[\'"]')
}

def resolve_fast(url, headers=None):
    """Hızlı URL çözümleme - cache yok, direkt işlem"""
    if not url:
        return {"resolved_url": None, "headers": {}}

    h = headers or {'User-Agent': 'Mozilla/5.0'}
    is_vavoo = "vavoo.to" in url
    s = get_session()
    
    try:
        resp = s.get(url, headers=h, allow_redirects=True, timeout=(2, 5))
        content = resp.text
        final = resp.url

        if is_vavoo or content[:10].strip().startswith('#EXTM3U'):
            return {"resolved_url": final, "headers": h}

        # Iframe yakala
        iframe = PATTERNS['iframe'].search(content)
        if not iframe:
            return {"resolved_url": final if content[:10].strip().startswith('#EXTM3U') else url, "headers": h}

        url2 = iframe.group(1)
        parsed = urlparse(url2)
        h.update({
            'Referer': f"{parsed.scheme}://{parsed.netloc}/",
            'Origin': f"{parsed.scheme}://{parsed.netloc}"
        })
        
        resp2 = s.get(url2, headers=h, timeout=(2, 5))
        txt = resp2.text

        # Pattern matching
        m = {k: p.search(txt) for k, p in PATTERNS.items()}
        
        if not all(m.get(k) for k in ['channel_key', 'auth_ts', 'auth_rnd', 'auth_sig', 'auth_host', 'server_lookup', 'host']):
            return {"resolved_url": final if content[:10].strip().startswith('#EXTM3U') else url, "headers": h}

        ck = m['channel_key'].group(1)
        ts = m['auth_ts'].group(1)
        rnd = m['auth_rnd'].group(1)
        sig = quote(m['auth_sig'].group(1))
        ah = m['auth_host'].group(1)
        sl = m['server_lookup'].group(1)
        host = m['host'].group(1)

        # Auth
        s.get(f'{ah}{ck}&ts={ts}&rnd={rnd}&sig={sig}', headers=h, timeout=(2, 4))

        # Server lookup
        srv = s.get(f"https://{parsed.netloc}{sl}{ck}", headers=h, timeout=(2, 4))
        sk = srv.json().get('server_key')
        
        if not sk:
            return {"resolved_url": url, "headers": h}

        stream = f'https://{sk}{host}{sk}/{ck}/mono.m3u8'
        
        return {
            "resolved_url": stream,
            "headers": {'User-Agent': h['User-Agent'], 'Referer': h.get('Referer', ''), 'Origin': h.get('Origin', '')}
        }

    except Exception as e:
        logger.warning(f"Resolve error: {e}")
        return {"resolved_url": url, "headers": h}

@app.route('/proxy/m3u')
def proxy_m3u():
    """Ultra-fast M3U8 proxy"""
    url = request.args.get('url', '').strip()
    if not url:
        return "No URL", 400

    metrics['total_requests'] += 1

    # Headers
    h = {"User-Agent": "Mozilla/5.0", "Referer": "https://vavoo.to/", "Origin": "https://vavoo.to"}
    for k, v in request.args.items():
        if k.startswith('h_'):
            h[unquote(k[2:]).replace("_", "-")] = unquote(v).strip()

    # URL transform
    url = url.replace('/stream/stream-', '/embed/stream-')
    pm = re.search(r'/premium(\d+)/mono\.m3u8$', url)
    if pm:
        url = f"https://daddylive.dad/embed/stream-{pm.group(1)}.php"

    try:
        metrics['active_streams'] += 1
        
        result = resolve_fast(url, h)
        if not result["resolved_url"]:
            return "Failed to resolve", 500

        s = get_session()
        resp = s.get(result["resolved_url"], headers=result["headers"], timeout=(2, 8))
        content = resp.text
        final = resp.url

        # Direkt M3U ise döndür
        if "#EXTM3U" in content[:100] and "#EXTINF" not in content[:300]:
            return Response(content, content_type="application/vnd.apple.mpegurl")

        # M3U8 rewrite
        parsed = urlparse(final)
        base = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rsplit('/', 1)[0]}/"
        hq = "&".join([f"h_{quote(k)}={quote(v)}" for k, v in result["headers"].items()])

        lines = []
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                lines.append(line)
            elif line.startswith("#EXT-X-KEY"):
                # Key rewrite
                m = re.search(r'URI="([^"]+)"', line)
                if m:
                    line = line.replace(m.group(1), f"/proxy/key?url={quote(m.group(1))}&{hq}")
                lines.append(line)
            elif line[0] != '#':
                # Segment rewrite
                seg = urljoin(base, line)
                lines.append(f"/proxy/ts?url={quote(seg)}&{hq}")
            else:
                lines.append(line)

        metrics['active_streams'] -= 1
        return Response('\n'.join(lines), content_type="application/vnd.apple.mpegurl")

    except Exception as e:
        metrics['active_streams'] -= 1
        logger.error(f"M3U error: {e}")
        return f"Error: {e}", 500

@app.route('/proxy/resolve')
def proxy_resolve():
    """Fast resolve"""
    url = request.args.get('url', '').strip()
    if not url:
        return "No URL", 400

    metrics['total_requests'] += 1

    h = {}
    for k, v in request.args.items():
        if k.startswith('h_'):
            h[unquote(k[2:]).replace("_", "-")] = unquote(v).strip()

    try:
        result = resolve_fast(url, h)
        if not result["resolved_url"]:
            return "Failed", 500
            
        hq = "&".join([f"h_{quote(k)}={quote(v)}" for k, v in result["headers"].items()])
        
        return Response(
            f"#EXTM3U\n#EXTINF:-1,Stream\n/proxy/m3u?url={quote(result['resolved_url'])}&{hq}",
            content_type="application/vnd.apple.mpegurl"
        )
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/proxy/ts')
def proxy_ts():
    """Ultra-fast segment proxy - zero buffer"""
    url = request.args.get('url', '').strip()
    if not url:
        return "No URL", 400

    h = {}
    for k, v in request.args.items():
        if k.startswith('h_'):
            h[unquote(k[2:]).replace("_", "-")] = unquote(v).strip()

    try:
        s = get_session()
        resp = s.get(url, headers=h, stream=True, timeout=(2, 20))
        
        def generate():
            try:
                # Direkt stream - minimum buffer
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        yield chunk
            finally:
                try:
                    resp.close()
                except:
                    pass
        
        return Response(
            generate(),
            content_type="video/mp2t",
            headers={
                'Cache-Control': 'public, max-age=3600',
                'X-Accel-Buffering': 'no'
            }
        )
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/proxy/key')
def proxy_key():
    """Fast key proxy"""
    url = request.args.get('url', '').strip()
    if not url:
        return "No URL", 400

    h = {}
    for k, v in request.args.items():
        if k.startswith('h_'):
            h[unquote(k[2:]).replace("_", "-")] = unquote(v).strip()

    try:
        s = get_session()
        resp = s.get(url, headers=h, timeout=(2, 5))
        return Response(resp.content, content_type="application/octet-stream")
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats')
def stats():
    uptime = (time.time() - metrics['start_time']) / 3600
    return jsonify({
        "requests": metrics['total_requests'],
        "streams": metrics['active_streams'],
        "uptime": f"{uptime:.1f}"
    })

@app.route('/health')
def health():
    return jsonify({"status": "ok", "version": "3.0"})

if __name__ == '__main__':
    logger.info("StreamFlow Fast v3.0 starting...")
    app.run(host="0.0.0.0", port=7860, debug=False, threaded=True)
