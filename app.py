import os
import requests
import random
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# AGENTES DE NAVEGACIÓN (Para que los servidores crean que eres un humano)
AGENTES = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
]

# INTERFAZ DE INICIO: EL CUADRO HERMOSO v4.0
INICIO_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <title>PACIFIC SURF v5.0</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background-color: #001220; color: #00FBFF; font-family: 'Courier New', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { border: 2px solid #00FBFF; padding: 40px; text-align: center; width: 320px; box-shadow: 0 0 25px rgba(0, 251, 255, 0.4); border-radius: 5px; }
        h1 { font-size: 2.2rem; letter-spacing: 6px; margin: 0; text-shadow: 2px 2px #000; }
        .v { font-size: 1.8rem; margin: 15px 0; color: #fff; }
        .tag { font-size: 0.75rem; margin-bottom: 25px; opacity: 0.8; }
        input { width: 100%; background: #000; border: 1px solid #00FBFF; color: #00FBFF; padding: 12px; margin-bottom: 15px; box-sizing: border-box; outline: none; font-family: monospace; }
        button { width: 100%; background: #00FBFF; color: #001220; border: none; padding: 12px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:hover { background: #fff; box-shadow: 0 0 15px #fff; }
    </style>
</head>
<body>
    <div class="box">
        <h1>PACIFIC</h1>
        <h1>SURF</h1>
        <div class="v">v5.0</div>
        <div class="tag">[ MODO LYNX + STEALTH ]</div>
        <form action="/nav">
            <input type="text" name="url" placeholder="Buscar o pegar URL..." autofocus required>
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

    # Si el usuario no escribe http, usamos DuckDuckGo HTML (evita bloqueos mejor que Google)
    target_url = url if url.startswith('http') else f"https://html.duckduckgo.com/html/?q={url}"

    try:
        # CAPA DE INVISIBILIDAD: Encabezados aleatorios
        headers = {
            'User-Agent': random.choice(AGENTES),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://www.google.com/'
        }
        
        r = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')

        # LIMPIEZA QUIRÚRGICA: Solo texto, nada de basura
        for tag in soup(["script", "style", "img", "video", "nav", "header", "footer", "aside", "form", "iframe", "noscript"]):
            tag.decompose()

        # RE-ESCRITURA DE LINKS: Para navegar siempre dentro del modo azul
        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"

        # INYECCIÓN DE BLUEPRINT PERSISTENTE (El secreto de los colores)
        resultado_estilo = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ 
                    background-color: #001220 !important; 
                    color: #00FBFF !important; 
                    font-family: 'Courier New', monospace !important; 
                    padding: 30px; line-height: 1.6; 
                }}
                /* Forzamos el color cian en todo */
                * {{ color: #00FBFF !important; background-color: transparent !important; }}
                /* Enlaces en Blanco para que se vean */
                a {{ color: #FFFFFF !important; text-decoration: underline !important; font-weight: bold; }}
                h1, h2, h3 {{ border-bottom: 2px solid #00FBFF; padding-bottom: 8px; margin-top: 30px; }}
                .btn-back {{ border: 2px solid #00FBFF; padding: 8px 15px; text-decoration: none; display: inline-block; margin-bottom: 25px; }}
                #container {{ max-width: 850px; margin: auto; }}
            </style>
        </head>
        <body>
            <div id="container">
                <a href="/" class="btn-back">[ VOLVER AL INICIO ]</a>
                <div id="content">{soup.prettify()}</div>
            </div>
        </body>
        </html>
        """
        return render_template_string(resultado_estilo)
        
    except Exception as e:
        return f"<body style='background:#001220; color:red; font-family:monospace; padding:20px;'>[ ERROR DE SISTEMA ]<br>{str(e)}<br><br><a href='/' style='color:white;'>[ VOLVER ]</a></body>"

if __name__ == '__main__':
    # Configuración dinámica para Google Cloud Run
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))