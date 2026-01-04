import os, requests, random
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

AGENTES = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"]

INICIO_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>PACIFIC SURF v5.0</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background-color: #001220; color: #00FBFF; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { border: 2px solid #00FBFF; padding: 40px; text-align: center; width: 320px; box-shadow: 0 0 25px #00FBFF; }
        input { width: 100%; background: #000; border: 1px solid #00FBFF; color: #00FBFF; padding: 12px; margin-bottom: 15px; }
        button { width: 100%; background: #00FBFF; color: #001220; border: none; padding: 12px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="box">
        <h1>PACIFIC SURF</h1>
        <div style="font-size: 1.5rem; margin: 10px;">v5.0</div>
        <form action="/nav">
            <input type="text" name="url" placeholder="Buscar..." autofocus required>
            <button type="submit">EJECUTAR</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(INICIO_HTML)

@app.route('/nav')
def nav():
    url = request.args.get('url')
    if not url: return home()
    target_url = url if url.startswith('http') else f"https://html.duckduckgo.com/html/?q={url}"

    try:
        headers = {'User-Agent': random.choice(AGENTES)}
        r = requests.get(target_url, headers=headers, timeout=12)
        # Si la respuesta no es texto, lanzamos error controlado
        if 'text/html' not in r.headers.get('Content-Type', ''):
            raise Exception("El destino no es una página web legible.")

        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup(["script", "style", "img", "nav", "header", "footer", "aside", "form"]): tag.decompose()

        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"

        # BLINDAJE TOTAL CONTRA CUADROS BLANCOS
        estilo_v5 = f"""
        <html>
        <head>
            <style>
                * {{ background-color: #001220 !important; color: #00FBFF !important; }}
                body {{ padding: 25px; font-family: monospace; line-height: 1.6; }}
                a {{ color: #FFFFFF !important; text-decoration: underline !important; }}
                h1, h2, h3 {{ border-bottom: 2px solid #00FBFF; padding-bottom: 8px; }}
                .btn {{ border: 2px solid #00FBFF; padding: 8px 15px; text-decoration: none; display: inline-block; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <a href="/" class="btn">[ VOLVER ]</a>
            <div>{soup.prettify()}</div>
        </body>
        </html>
        """
        return render_template_string(estilo_v5)
    except Exception as e:
        return f"<body style='background:#001220; color:red; font-family:monospace; padding:20px;'>[ ERROR ] No se pudo cargar el enlace.<br>Motivo: {str(e)}<br><a href='/' style='color:white;'>[ VOLVER ]</a></body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
