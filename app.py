from flask import Flask, request, render_template_string
import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# CSS Blueprint persistente (Ahora es el ÚNICO estilo que cargará el navegador)
CORE_ASSETS = """
<style>
    :root { --font-size: 1.3rem; }
    body { 
        background-color: #001a33 !important; 
        color: #00ffff !important; 
        font-family: 'Courier New', monospace !important;
        font-size: var(--font-size) !important;
        line-height: 1.6;
        padding: 20px;
        margin: 0;
    }
    a { color: #e0ffff !important; text-decoration: underline !important; font-weight: bold; }
    
    /* Panel de Ajustes y Engranaje */
    #gear-btn { 
        position: fixed; bottom: 20px; right: 20px; z-index: 100000;
        background: #00ffff; border-radius: 50%; width: 50px; height: 50px;
        display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 24px;
    }
    #settings-panel {
        position: fixed; bottom: 80px; right: 20px; z-index: 100000;
        background: #000; border: 2px solid #00ffff; padding: 20px;
        display: none; flex-direction: column; gap: 15px; color: #00ffff;
    }
    input[type=range] { width: 100%; cursor: pointer; }
</style>
<script>
    function togglePanel() {
        const p = document.getElementById('settings-panel');
        p.style.display = p.style.display === 'flex' ? 'none' : 'flex';
    }
    function updateSize(val) {
        document.documentElement.style.setProperty('--font-size', val + 'rem');
        localStorage.setItem('p-size', val);
    }
    window.addEventListener('DOMContentLoaded', () => {
        const savedSize = localStorage.getItem('p-size') || '1.3';
        updateSize(savedSize);
        document.getElementById('size-slider').value = savedSize;
    });
</script>
"""

@app.route('/')
def home():
    return render_template_string(f"""
    <html><head>{CORE_ASSETS}</head>
    <body style="text-align:center; display:flex; align-items:center; justify-content:center; height:100vh;">
        <div style="border:2px solid #00ffff; padding:30px; width:90%; max-width:500px;">
            <h1>PACIFIC SURF v4.0</h1>
            <p>[ MODO LYNX + BLUEPRINT ]</p>
            <form action="/nav" method="get">
                <input type="text" name="url" style="width:100%; background:#000; color:#0ff; border:1px solid #0ff; padding:15px; margin-bottom:15px;" placeholder="URL o Búsqueda..." required>
                <button type="submit" style="width:100%; background:#0ff; color:#001a33; border:none; padding:15px; font-weight:bold; cursor:pointer;">EJECUTAR</button>
            </form>
        </div>
    </body></html>
    """)

@app.route('/nav')
def proxy():
    query = request.args.get('url')
    if not query: return home()

    # MOTOR DE BÚSQUEDA: Usamos DuckDuckGo Lite (HTML puro, sin JS, sin bloqueos)
    if not (query.startswith('http://') or query.startswith('https://')):
        target_url = f"https://html.duckduckgo.com/html/?q={query}"
    else:
        target_url = query

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- EL "EFECTO LYNX": Eliminación masiva de activos pesados ---
        for tag in soup(["script", "style", "link", "img", "video", "iframe", "svg", "noscript"]):
            tag.decompose()

        # Reescritura de enlaces para navegación persistente
        for a in soup.find_all('a', href=True):
            full_url = urljoin(target_url, a['href'])
            a['href'] = f"/nav?{urlencode({'url': full_url})}"

        # Interfaz de Control
        ui_controls = f"""
        <div id="gear-btn" onclick="togglePanel()">⚙️</div>
        <div id="settings-panel">
            <strong>AJUSTES DE LECTURA</strong>
            <label>Tamaño Letra: <input type="range" id="size-slider" min="0.8" max="3.0" step="0.1" oninput="updateSize(this.value)"></label>
            <button onclick="location.href='/'" style="background:#0ff; border:none; padding:10px; cursor:pointer;">NUEVA BÚSQUEDA</button>
        </div>
        """

        return f"<html><head>{CORE_ASSETS}</head><body>{ui_controls}{soup.prettify()}</body></html>"
    except Exception as e:
        return f"<html><head>{CORE_ASSETS}</head><body>ERROR: {str(e)}<br><a href='/'>VOLVER</a></body></html>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
