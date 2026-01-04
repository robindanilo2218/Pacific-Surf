import os
import requests
import random
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Agentes para evitar ser detectados como bots
AGENTES = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
]

INICIO_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>PACIFIC SURF v5.0</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background-color: #001220; color: #00FBFF; font-family: 'Courier New', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { border: 2px solid #00FBFF; padding: 40px; text-align: center; width: 320px; box-shadow: 0 0 25px rgba(0, 251, 255, 0.4); }
        h1 { font-size: 2rem; letter-spacing: 5px; margin: 0; }
        .v { font-size: 1.8rem; margin: 15px 0; color: #fff; }
        input { width: 100%; background: #000; border: 1px solid #00FBFF; color: #00FBFF; padding: 12px; margin-bottom: 15px; box-sizing: border-box; outline: none; }
        button { width: 100%; background: #00FBFF; color: #001220; border: none; padding: 12px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="box">
        <h1>PACIFIC</h1>
        <h1>SURF</h1>
        <div class="v">v5.0</div>
        <form action="/nav">
            <input type="text" name="url" placeholder="Buscar o URL..." autofocus required>
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
    if not url:
        return home()

    # Si no es URL, usamos el buscador DuckDuckGo (modo HTML)
    target_url = url if url.startswith('http') else f"https://html.duckduckgo.com/html/?q={url}"

    try:
        headers = {
            'User-Agent': random.choice(AGENTES),
            'Accept-Language': 'es-ES,es;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        # Usamos sesión para mejor manejo de conexiones
        with requests.Session() as session:
            r = session.get(target_url, headers=headers, timeout=15)
        
        soup = BeautifulSoup(r.text, 'html.parser')

        # Limpieza de elementos innecesarios
        for tag in soup(["script", "style", "img", "video", "nav", "header", "footer", "aside", "form", "iframe"]):
            tag.decompose()

        # Re-escritura de enlaces
        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"

        # Inyección de estilo Blueprint Persistente
        estilo_v5 = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ background-color: #001220 !important; color: #00FBFF !important; font-family: 'Courier New', monospace !important; padding: 25px; line-height: 1.6; }}
                * {{ color: #00FBFF !important; }}
                a {{ color: #FFFFFF !important; text-decoration: underline !important; }}
                h1, h2, h3 {{ border-bottom: 2px solid #00FBFF; padding-bottom: 8px; }}
                .btn {{ border: 2px solid #00FBFF; padding: 8px 15px; text-decoration: none; display: inline-block; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <a href="/" class="btn">[ VOLVER AL INICIO ]</a>
            <div>{soup.prettify()}</div>
        </body>
        </html>
        """
        return render_template_string(estilo_v5)
        
    except Exception as e:
        return f"<body style='background:#001220; color:red; font-family:monospace; padding:20px;'>[ ERROR DE SISTEMA ]<br>{str(e)}<br><br><a href='/' style='color:white;'>[ VOLVER ]</a></body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
