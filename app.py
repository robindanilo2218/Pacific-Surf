import os, requests, random
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# DISFRACES DE NAVEGADOR (User-Agents)
AGENTES = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"]

# INTERFAZ INICIAL
INICIO = """
<body style="background:#001220;color:#00FBFF;font-family:monospace;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;">
    <div style="border:2px solid #00FBFF;padding:40px;text-align:center;">
        <h1>PACIFIC SURF v5.3</h1>
        <form action="/nav">
            <input name="url" style="background:#000;border:1px solid #00FBFF;color:#00FBFF;padding:10px;width:100%;" placeholder="Escribe aqui..." autofocus>
            <br><br>
            <button style="background:#00FBFF;color:#001220;border:none;padding:10px;width:100%;font-weight:bold;">EJECUTAR</button>
        </form>
    </div>
</body>
"""

@app.route('/')
def home(): return render_template_string(INICIO)

@app.route('/nav')
def nav():
    url = request.args.get('url')
    if not url: return home()
    
    # Motor de busqueda: DuckDuckGo HTML
    target = url if url.startswith('http') else f"https://html.duckduckgo.com/html/?q={url}"

    try:
        # Peticion al sitio web
        h = {'User-Agent': random.choice(AGENTES)}
        r = requests.get(target, headers=h, timeout=10)
        
        # Procesamiento con BeautifulSoup
        s = BeautifulSoup(r.text, 'html.parser')
        
        # Limpieza suave
        for tag in s(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Corregir enlaces
        for a in s.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target, a['href'])})}"

        # DISEÑO NOTEPAD (Fuente: Courier New)
        output = f"""
        <html>
        <head>
            <style>
                * {{ background-color: #001220 !important; color: #00FBFF !important; font-family: 'Courier New', monospace !important; }}
                body {{ padding: 20px; }}
                a {{ color: #FFF !important; }}
                .btn {{ border: 1px solid #00FBFF; padding: 5px; text-decoration: none; }}
            </style>
        </head>
        <body>
            <a href="/" class="btn">[ VOLVER ]</a>
            <hr>
            <div>{s.prettify()}</div>
        </body>
        </html>
        """
        return render_template_string(output)
    except Exception as e:
        return f"<body style='background:#001220;color:red;font-family:monospace;'>ERROR: {str(e)}</body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
