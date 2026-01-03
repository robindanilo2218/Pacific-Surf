import os
import requests
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# ESTILO BLUEPRINT V4.0 - PÁGINA DE INICIO
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
        input { width: 100%; background: #000; border: 1px solid #00FBFF; color: #00FBFF; padding: 10px; margin-bottom: 10px; box-sizing: border-box; }
        button { width: 100%; background: #00FBFF; color: #001220; border: none; padding: 12px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="box">
        <h1>PACIFIC</h1>
        <h1>SURF</h1>
        <div class="v">v4.0</div>
        <form action="/nav">
            <input type="text" name="url" placeholder="Buscar..." autofocus>
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

    # Usamos DuckDuckGo para evitar bloqueos, pero forzamos NUESTROS colores
    target_url = url if url.startswith('http') else f"https://html.duckduckgo.com/html/?q={url}"

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(target_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Limpieza de basura
        for tag in soup(["script", "style", "img", "nav", "header", "footer", "form"]):
            tag.decompose()

        # Re-escritura de links
        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"

        # INYECCIÓN AGRESIVA DE COLORES HERMOSOS
        blueprint_results = f"""
        <html>
        <head>
            <style>
                body {{ 
                    background-color: #001220 !important; 
                    color: #00FBFF !important; 
                    font-family: 'Courier New', monospace !important; 
                    padding: 20px; 
                }}
                /* Forzamos que todos los textos sean Cian */
                * {{ color: #00FBFF !important; }}
                /* Los links en Blanco para que resalten */
                a {{ color: #FFFFFF !important; text-decoration: underline !important; }}
                h1, h2, h3 {{ border-bottom: 1px solid #00FBFF; }}
                .home-btn {{ border: 1px solid #00FBFF; padding: 5px; text-decoration: none; display: inline-block; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <a href="/" class="home-btn">[ VOLVER AL INICIO ]</a>
            <div>{soup.prettify()}</div>
        </body>
        </html>
        """
        return render_template_string(blueprint_results)
    except Exception as e:
        return f"<body style='background:#001220;color:red'>Error: {str(e)}</body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
