import os
import requests
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# ESTILO BLUEPRINT V4.0 ORIGINAL
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PACIFIC SURF v5.0</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            background-color: #001220; /* Azul Marino Oscuro */
            color: #00FBFF; /* Cian Neón */
            font-family: 'Courier New', monospace;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        }
        .container {
            border: 2px solid #00FBFF;
            padding: 40px;
            text-align: center;
            width: 80%;
            max-width: 400px;
            box-shadow: 0 0 20px rgba(0, 251, 255, 0.3);
        }
        h1 { font-size: 2.5rem; letter-spacing: 8px; margin: 0; }
        h2 { font-size: 1.5rem; letter-spacing: 5px; margin: 20px 0; }
        .version { font-size: 2rem; margin-bottom: 30px; }
        .tagline { font-size: 0.9rem; margin-bottom: 20px; text-transform: uppercase; }
        input[type="text"] {
            width: 100%;
            background: #000;
            border: 1px solid #00FBFF;
            color: #00FBFF;
            padding: 10px;
            margin-bottom: 10px;
            box-sizing: border-box;
            outline: none;
        }
        button {
            width: 100%;
            background: #00FBFF;
            color: #001220;
            border: none;
            padding: 12px;
            font-weight: bold;
            cursor: pointer;
            text-transform: uppercase;
        }
        button:hover { background: #fff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>PACIFIC</h1>
        <h2>SURF</h2>
        <div class="version">v5.0</div>
        <div class="tagline">[ MODO LYNX + BLUEPRINT ]</div>
        <form action="/nav">
            <input type="text" name="url" placeholder="Wikipedia, Google o URL..." autofocus>
            <button type="submit">EJECUTAR</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/nav')
def nav():
    url = request.args.get('url')
    if not url: return home()

    # CAMBIO A BUSCADOR GOOGLE
    if not url.startswith('http'):
        target_url = f"https://www.google.com/search?q={url}"
    else:
        target_url = url

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(target_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        # FILTRADO QUIRÚRGICO (MODO LECTURA)
        # Eliminamos menús (nav), cabeceras (header) y pies de página (footer)
        for tag in soup(["script", "style", "img", "video", "nav", "header", "footer", "aside"]):
            tag.decompose()

        # Re-escribir enlaces para que sigan pasando por nuestro proxy
        for a in soup.find_all('a', href=True):
            absolute_url = urljoin(target_url, a['href'])
            a['href'] = f"/nav?{urlencode({'url': absolute_url})}"

        # Estética para el contenido de lectura
        content_style = "<style>body{background:#001220;color:#00FBFF;font-family:monospace;padding:20px;} a{color:#fff;}</style>"
        return content_style + soup.prettify()

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
