import os, requests, random
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Agentes para simular un navegador real y evitar bloqueos
AGENTES = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"]

# INTERFAZ PRINCIPAL BLUEPRINT v5.1
INICIO_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>PACIFIC SURF v5.1</title>
    <style>
        body { background-color: #001220; color: #00FBFF; font-family: 'Courier New', Courier, monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { border: 3px solid #00FBFF; padding: 50px; text-align: center; width: 350px; box-shadow: 0 0 30px #00FBFF; }
        h1 { letter-spacing: 10px; margin: 0; font-size: 2.5rem; }
        .v { font-size: 1.5rem; margin: 20px 0; color: #fff; }
        input { width: 100%; background: #000; border: 1px solid #00FBFF; color: #00FBFF; padding: 12px; margin-bottom: 20px; font-family: monospace; outline: none; }
        button { width: 100%; background: #00FBFF; color: #001220; border: none; padding: 15px; font-weight: bold; cursor: pointer; font-family: monospace; }
    </style>
</head>
<body>
    <div class="box">
        <h1>PACIFIC</h1>
        <h1>SURF</h1>
        <div class="v">v5.1</div>
        <form action="/nav">
            <input type="text" name="url" placeholder="Escribe aqui..." autofocus required>
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
    
    # Motor de busqueda alternativo para evitar bloqueos
    target = url if url.startswith('http') else f"https://html.duckduckgo.com/html/?q={url}"

    try:
        r = requests.get(target, headers={'User-Agent': random.choice(AGENTES)}, timeout=10)
        # Verificamos que sea contenido procesable
        if "text/html" not in r.headers.get("Content-Type", ""):
            return f"<body style='background:#001220;color:red;font-family:monospace;'>Archivo no legible. <a href='/'>Volver</a></body>"

        soup = BeautifulSoup(r.text, 'html.parser')

        # LIMPIEZA TOTAL (MODO LECTURA)
        for s in soup(["script", "style", "nav", "footer", "header", "img", "video", "form"]):
            s.decompose()

        # REESCRITURA DE ENLACES
        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target, a['href'])})}"

        # DISEÑO EXQUISITO DE RESULTADOS (BLINDADO)
        blueprint_ui = f"""
        <html>
        <head>
            <style>
                * {{ background-color: #001220 !important; color: #00FBFF !important; border-color: #00FBFF !important; }}
                body {{ font-family: 'Courier New', monospace; padding: 40px; line-height: 1.7; }}
                a {{ color: #FFFFFF !important; text-decoration: underline !important; }}
                h1, h2, h3 {{ border-bottom: 2px solid #00FBFF; padding-bottom: 10px; color: #00FBFF !important; }}
                .nav-link {{ border: 1px solid #00FBFF; padding: 10px; text-decoration: none; display: inline-block; margin-bottom: 30px; }}
            </style>
        </head>
        <body>
            <a href="/" class="nav-link">[ VOLVER AL INICIO ]</a>
            <div id="content">{soup.prettify()}</div>
        </body>
        </html>
        """
        return render_template_string(blueprint_ui)

    except Exception as e:
        return f"<body style='background:#001220;color:red;font-family:monospace;'>Error: {str(e)} <a href='/'>Volver</a></body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
