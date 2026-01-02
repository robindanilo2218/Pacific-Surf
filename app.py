from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Estilos base del sistema y el Panel de Ajustes
CORE_ASSETS = """
<style>
    :root { --font-size: 1.2rem; }
    
    /* Modo Blueprint Forzado */
    body.blueprint-on, body.blueprint-on * { 
        background-color: #001a33 !important; 
        color: #00ffff !important; 
        font-family: 'Courier New', monospace !important;
        font-size: var(--font-size) !important;
    }
    body.blueprint-on a { color: #e0ffff !important; }

    /* UI del Engranaje y Panel */
    #gear-btn { 
        position: fixed; bottom: 20px; right: 20px; z-index: 100000;
        background: #00ffff; border-radius: 50%; width: 45px; height: 45px;
        display: flex; align-items: center; justify-content: center; cursor: pointer;
    }
    #settings-panel {
        position: fixed; bottom: 75px; right: 20px; z-index: 100000;
        background: #000; border: 2px solid #00ffff; padding: 15px;
        display: none; flex-direction: column; gap: 10px; color: #00ffff;
    }
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

    function toggleBlue(btn) {
        document.body.classList.toggle('blueprint-on');
        localStorage.setItem('p-mode', document.body.classList.contains('blueprint-on') ? 'on' : 'off');
    }

    // Aplicar persistencia al cargar
    window.addEventListener('DOMContentLoaded', () => {
        if(localStorage.getItem('p-mode') !== 'off') document.body.classList.add('blueprint-on');
        const savedSize = localStorage.getItem('p-size') || '1.2';
        updateSize(savedSize);
        document.getElementById('size-slider').value = savedSize;
    });
</script>
"""

@app.route('/')
def home():
    return render_template_string("<h1>PACIFIC SURF v3.5</h1><form action='/nav'><input name='url'><button>GO</button></form>")

@app.route('/nav')
def proxy():
    target_url = request.args.get('url')
    if not target_url: return home()
    if not target_url.startswith('http'): target_url = "https://" + target_url

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

# --- ALGORITMO DE AHORRO DE DATOS (90% SAVING) ---
# Eliminamos todo lo que consume datos antes de enviar al móvil
for heavy_tag in soup(["img", "video", "iframe", "audio", "canvas", "svg"]):
    heavy_tag.decompose() # Esto borra el objeto y evita que se descargue

# Eliminamos scripts pesados de publicidad y rastreo
for script in soup(["script", "noscript"]):
    script.decompose()
# -------------------------------------------------


        # Inyección de Base y Links
        base_tag = soup.new_tag('base', href=target_url)
        if soup.head: soup.head.insert(0, base_tag)
        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"

        # Construcción de la UI de Control
        ui_html = f"""
        <div id="gear-btn" onclick="togglePanel()">⚙️</div>
        <div id="settings-panel">
            <strong>AJUSTES</strong>
            <label>Tamaño Letra: <input type="range" id="size-slider" min="0.8" max="2.5" step="0.1" oninput="updateSize(this.value)"></label>
            <button onclick="toggleBlue()" style="background:#00ffff; border:none; cursor:pointer;">Alternar Blueprint</button>
        </div>
        """

        return f"<html><head>{CORE_ASSETS}</head><body>{ui_html}{soup.body.prettify() if soup.body else soup.prettify()}</body></html>"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
