from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Interfaz de inicio simple
HOME_HTML = """
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; text-align: center; padding: 50px; background: #f0f0f0; }
        .box { background: white; padding: 30px; display: inline-block; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input { width: 80%; padding: 10px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="box">
        <h1>Navegador Base v3.0</h1>
        <form action="/nav" method="get">
            <input type="text" name="url" placeholder="Escribe una URL o busca en Google..." required>
            <br>
            <button type="submit">Navegar</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/nav')
def proxy():
    query = request.args.get('url')
    if not query: return home()

    # Si no es URL, busca en Google
    if not (query.startswith('http://') or query.startswith('https://')):
        target_url = f"https://www.google.com/search?q={query}&gbv=1"
    else:
        target_url = query

    # Identificación para que los sitios nos dejen pasar
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # REESCRITURA DE LINKS: Para navegar naturalmente
        for a in soup.find_all('a', href=True):
            original_href = a['href']
            # Limpiar redirecciones de Google si es necesario
            if '/url?q=' in original_href:
                original_href = original_href.split('/url?q=')[1].split('&')[0]
            
            full_url = urljoin(target_url, original_href)
            a['href'] = f"/nav?{urlencode({'url': full_url})}"

        # Barra de control superior
        control_bar = f"""
        <div style="background:#333; color:white; padding:10px; font-family:sans-serif; position:sticky; top:0; z-index:9999;">
            <a href="/" style="color:white; text-decoration:none;">[ INICIO ]</a> | 
            <span>Navegando en: {target_url[:40]}...</span>
        </div>
        """

        return control_bar + soup.prettify()

    except Exception as e:
        return f"<h3>Error al acceder al sitio:</h3><p>{str(e)}</p><a href='/'>Volver</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
