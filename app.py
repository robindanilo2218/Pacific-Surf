import os
import requests
import random
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# LISTA DE DISFRACES (USER-AGENTS) PARA NO PARECER UN BOT
AGENTES = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

INICIO_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>PACIFIC SURF v4.0</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background-color: #001220; color: #00FBFF; font-family: 'Courier New', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { border: 2px solid #00FBFF; padding: 40px; text-align: center; width: 300px; box-shadow: 0 0 20px rgba(0, 251, 255, 0.3); }
        h1 { font-size: 2rem; letter-spacing: 5px; margin: 0; }
        .v { font-size: 1.8rem; margin: 20px 0; }
        input { width: 100%; background: #000; border: 1px solid #00FBFF; color: #00FBFF; padding: 10px; margin-bottom: 10px; box-sizing: border-box; outline: none; }
        button { width: 100%; background: #00FBFF; color: #001220; border: none; padding: 12px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="box">
        <h1>PACIFIC</h1>
        <h1>SURF</h1>
        <div class="v">v4.0</div>
        <form action="/nav">
            <input type="text" name="url" placeholder="Buscar en Wikipedia..." autofocus>
            <button type="submit">EJECUTAR</button>
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

    # Si no es URL, usamos DuckDuckGo (más amigable que Google para evitar bloqueos)
    target_url = url if url.startswith('http') else f"https://html.duckduckgo.com/html/?q={url}"

    try:
        # CAPA DE INVISIBILIDAD: Elegimos un disfraz aleatorio
        headers = {
            'User-Agent': random.choice(AGENTES),
            'Accept-Language': 'es-ES,es;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        r = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')

        # LIMPIEZA MODO LYNX
        for tag in soup(["script", "style", "img", "nav", "header", "footer", "form", "iframe"]):
            tag.decompose()

        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"

        # BLINDAJE DE COLORES HERMOSOS (AZUL Y CIAN)
        resultado_estilo = f"""
        <html>
        <head>
            <style>
                body {{ background-color: #001220 !important; color: #00FBFF !important; font-family: 'Courier New', monospace !important; padding: 25px; line-height: 1.6; }}
                * {{ color: #00FBFF !important; }}
                a {{ color: #FFFFFF !important; text-decoration: underline !important; }}
                h1, h2, h3 {{ border-bottom: 1px solid #00FBFF; padding-bottom: 10px; }}
                .btn {{ border: 1px solid #00FBFF; padding: 5px; text-decoration: none; display: inline-block; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <a href="/" class="btn">[ VOLVER AL INICIO ]</a>
            <div>{soup.prettify()}</div>
        </body>
        </html>
        """
        return render_template_string(resultado_estilo)
    except Exception as e:
        return f"<body style='background:#001220;color:red;font-family:monospace;'>[ SISTEMA ] Error de conexión: {str(e)}<br><a href='/' style='color:white;'>Reintentar</a></body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
