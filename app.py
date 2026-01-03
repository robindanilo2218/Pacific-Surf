from flask import Flask, request, render_template_string
import requests, re, urllib.parse as up
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# UI Maestra: Blueprint + Controles
UI_BASE = """
<style>
    /* El cuadro centralizado */
    .main-frame {
        border: 3px double #00FBFF; /* Doble línea cian */
        padding: 50px;
        background: rgba(0, 18, 32, 0.9);
        box-shadow: 0 0 30px #00FBFF;
        border-radius: 15px; /* Bordes redondeados para elegancia */
    }
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

    # --- PARCHE DE REDIRECCIÓN (FIX google) ---
    if 'uddg=' in url: url = up.unquote(url.split('uddg=')[1].split('&')[0])
    elif 'url?q=' in url: url = up.unquote(url.split('url?q=')[1].split('&')[0])
    
    t_url = url if url.startswith('http') else f"https;//www.google.com/search?q={url}"

    try:
        r = requests.get(t_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        s = BeautifulSoup(r.text, 'html.parser')
        # ELIMINACIÓN AGRESIVA DE MENÚS Y BASURA
        # Eliminamos nav, footer, header y aside para que solo quede el contenido
        for tag in s(["script", "style", "img", "video", "iframe", "nav", "footer", "header", "aside", "form"]): 
            tag.decompose()
        
        # Intentar capturar solo el contenido principal si el sitio es moderno
        main_content = s.find('main') or s.find('article') or s.body

        ctrl = f'<div id="gear" onclick="togM()">⚙️</div><div id="menu"><button onclick="togE()">MODO BORRAR</button><input type="range" min="1" max="3" step="0.1" oninput="setS(this.value)"><a href="/" style="color:#0ff">NUEVA BUSQUEDA</a></div>'
        return f"<html><head>{UI_BASE}</head><body class='blue-mode'>{ctrl}{s.body.prettify() if s.body else s.prettify()}</body></html>"
    except Exception as e:
        return f"Error: {str(e)} <br> <a href='/'>Volver</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
