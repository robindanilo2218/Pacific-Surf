import os, requests, random
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# --- ESTILOS Y PLANTILLAS (Configuracion Visual) ---
ESTILO_NOTEPAD = """
<style>
    * { background-color: #001220 !important; color: #00FBFF !important; font-family: 'Courier New', Courier, monospace !important; }
    body { padding: 30px; line-height: 1.6; }
    a { color: #FFFFFF !important; text-decoration: underline !important; font-weight: bold; }
    h1, h2, h3 { border-bottom: 2px solid #00FBFF; padding-bottom: 10px; }
    .btn-nav { border: 1px solid #00FBFF; padding: 10px; text-decoration: none; display: inline-block; margin-bottom: 20px; }
    pre, code { white-space: pre-wrap !important; }
</style>
"""

INICIO_HTML = f"""
<!DOCTYPE html>
<html>
<head><title>PACIFIC SURF v5.3</title></head>
<body style="background:#001220; color:#00FBFF; font-family:monospace; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
    <div style="border:3px solid #00FBFF; padding:50px; text-align:center; box-shadow: 0 0 20px #00FBFF;">
        <h1 style="letter-spacing:10px;">PACIFIC SURF</h1>
        <p>MODO LYNX v5.3.1</p>
        <form action="/nav">
            <input name="url" style="background:#000; border:1px solid #00FBFF; color:#00FBFF; padding:15px; width:100%; font-family:monospace;" placeholder="Buscar o URL..." autofocus required>
            <br><br>
            <button type="submit" style="background:#00FBFF; color:#001220; border:none; padding:15px; width:100%; font-weight:bold; cursor:pointer;">EJECUTAR</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(INICIO_HTML)

@app.route('/nav')
def nav():
    url = request.args.get('url')
    if not url: return home()
    
    # Motor de busqueda DuckDuckGo HTML (No JS)
    target = url if url.startswith('http') else f"https://html.duckduckgo.com/html/?q={url}"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(target, headers=headers, timeout=12)
        
        # Procesar con BeautifulSoup
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Limpieza Quirurgica: Quitamos lo que rompe el diseño
        for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "img"]):
            tag.decompose()

        # Corregir los enlaces para que no se salgan de Pacific Surf
        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target, a['href'])})}"

        # Construccion de la respuesta final
        cuerpo = soup.find('body') or soup
        final_html = f"""
        <html>
        <head>{ESTILO_NOTEPAD}</head>
        <body>
            <a href="/" class="btn-nav">[ VOLVER AL INICIO ]</a>
            <hr style="border: 1px solid #00FBFF;">
            <div>{cuerpo.prettify()}</div>
        </body>
        </html>
        """
        return render_template_string(final_html)

    except Exception as e:
        return f"<body style='background:#001220; color:red; font-family:monospace; padding:20px;'>[ ERROR SISTEMA ]: {str(e)}<br><br><a href='/' style='color:#fff;'>REINTENTAR</a></body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
