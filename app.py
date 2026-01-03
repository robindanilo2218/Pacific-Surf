import os
import requests
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# ESTILO BLUEPRINT V4.0 ORIGINAL PARA LA PÁGINA DE INICIO
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
        .tag { font-size: 0.8rem; margin-bottom: 30px; }
        input { width: 100%; background: #000; border: 1px solid #00FBFF; color: #00FBFF; padding: 10px; margin-bottom: 10px; box-sizing: border-box; }
        button { width: 100%; background: #00FBFF; color: #001220; border: none; padding: 12px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="box">
        <h1>PACIFIC</h1>
        <h1>SURF</h1>
        <div class="v">v4.0</div>
        <div class="tag">[ MODO LYNX + BLUEPRINT ]</div>
        <form action="/nav">
            <input type="text" name="url" placeholder="Wikipedia o URL..." autofocus>
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

    # CAMBIO ESTRATÉGICO: Usamos DuckDuckGo para evitar el bloqueo de "Robot" de Google
    target_url = url if url.startswith('http') else f"https://html.duckduckgo.com/html/?q={url}"

    try:
        # User-Agent para parecer un navegador real
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(target_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        # LIMPIEZA TOTAL DE MENÚS (MODO LYNX)
        for tag in soup(["script", "style", "img", "video", "nav", "header", "footer", "aside", "form", "iframe"]):
            tag.decompose()

        # RE-ESCRITURA DE LINKS PARA MANTENERSE EN EL PROXY
        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"

        # INYECCIÓN DEL BLUEPRINT EN LOS RESULTADOS (FONDO AZUL)
        resultado_estilo = f"""
        <html>
        <head>
            <style>
                body {{ background-color: #001220 !important; color: #00FBFF !important; font-family: monospace; padding: 20px; line-height: 1.5; }}
                a {{ color: #FFFFFF !important; }}
                h1, h2, h3 {{ border-bottom: 1px solid #00FBFF; }}
                .back {{ border: 1px solid #00FBFF; padding: 5px; text-decoration: none; display: inline-block; margin-bottom: 20px; color: #00FBFF !important; }}
            </style>
        </head>
        <body>
            <a href="/" class="back">[ VOLVER ]</a>
            <div>{soup.prettify()}</div>
        </body>
        </html>
        """
        return render_template_string(resultado_estilo)
    except Exception as e:
        return f"<body style='background:#001220;color:red'>Error: {str(e)}</body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
