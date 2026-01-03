from flask import Flask, request, render_template_string
import requests, re, urllib.parse as up
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# UI Maestra: Blueprint + Controles
UI_BASE = """
<style>
    :root { --fsize: 1.3rem; }
    body.blue-mode, body.blue-mode * { background:#001a33 !important; color:#00ffff !important; font-family:monospace !important; font-size: var(--fsize) !important; }
    .edit-active *:hover { outline: 2px solid red !important; cursor: crosshair !important; }
    #gear { position:fixed; bottom:20px; right:20px; z-index:99; background:#0ff; border-radius:50%; width:45px; height:45px; display:flex; align-items:center; justify-content:center; cursor:pointer; }
    #menu { position:fixed; bottom:70px; right:20px; z-index:99; background:#000; border:1px solid #0ff; padding:15px; display:none; flex-direction:column; gap:10px; }
</style>
<script>
    function togM() { const m=document.getElementById('menu'); m.style.display=m.style.display==='flex'?'none':'flex'; }
    function setS(v) { document.documentElement.style.setProperty('--fsize', v+'rem'); }
    function togE() { 
        document.body.classList.toggle('edit-active');
        if(document.body.classList.contains('edit-active')) {
            document.onclick = (e) => { if(document.body.classList.contains('edit-active')){ e.preventDefault(); e.target.remove(); } };
        }
    }
</script>
"""

@app.route('/')
def home():
    return render_template_string(f"<html><head>{UI_BASE}</head><body class='blue-mode'><h1>PACIFIC SURF v4.7</h1><form action='/nav'><input name='url' placeholder='Buscar o URL...' style='width:80%;padding:10px;'><button>GO</button></form></body></html>")

@app.route('/nav')
def proxy():
    url = request.args.get('url')
    if not url: return home()

    # --- PARCHE DE REDIRECCIÓN (FIX DUCKDUCKGO) ---
    if 'uddg=' in url: url = up.unquote(url.split('uddg=')[1].split('&')[0])
    elif 'url?q=' in url: url = up.unquote(url.split('url?q=')[1].split('&')[0])
    
    t_url = url if url.startswith('http') else f"https://html.duckduckgo.com/html/?q={url}"

    try:
        r = requests.get(t_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        s = BeautifulSoup(r.text, 'html.parser')
        for tag in s(["script", "style", "img", "video", "iframe"]): tag.decompose()
        for a in s.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(t_url, a['href'])})}"

        ctrl = f'<div id="gear" onclick="togM()">⚙️</div><div id="menu"><button onclick="togE()">MODO BORRAR</button><input type="range" min="1" max="3" step="0.1" oninput="setS(this.value)"><a href="/" style="color:#0ff">NUEVA BUSQUEDA</a></div>'
        return f"<html><head>{UI_BASE}</head><body class='blue-mode'>{ctrl}{s.body.prettify() if s.body else s.prettify()}</body></html>"
    except Exception as e:
        return f"Error: {str(e)} <br> <a href='/'>Volver</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
