from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

HOME_HTML = """
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; text-align: center; padding: 50px; background: #f8f9fa; color: #333; }
        .container { border: 1px solid #dee2e6; padding: 40px; display: inline-block; background: white; border-radius: 10px; }
        input { width: 80%; padding: 12px; border: 1px solid #ced4da; border-radius: 5px; margin-bottom: 15px; }
        button { padding: 12px 25px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>PACIFIC SURF v3.1</h1>
        <p>Navegación Natural y Directa</p>
        <form action="/nav" method="get">
            <input type="text" name="url" placeholder="Escribe URL (ej: wikipedia.org) o busca..." required>
            <br>
            <button type="submit">ENTRAR</button>
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

    target_url = query if query.startswith('http') else f"https://www.google.com/search?q={query}&gbv=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- LA CLAVE PARA LA NAVEGACIÓN NATURAL ---
        # Añadimos <base> para que el CSS y JS carguen desde el sitio original automáticamente
        base_tag = soup.new_tag('base', href=target_url)
        if soup.head:
            soup.head.insert(0, base_tag)
        else:
            new_head = soup.new_tag('head')
            new_head.insert(0, base_tag)
            soup.insert(0, new_head)

        # Reescritura de enlaces para no perder la sesión del proxy
        for a in soup.find_all('a', href=True):
            full_url = urljoin(target_url, a['href'])
            a['href'] = f"/nav?{urlencode({'url': full_url})}"

        # Barra de navegación minimalista para volver al inicio
        top_bar = f"""
        <div style="background:#000; color:#fff; padding:10px; font-family:sans-serif; position:fixed; top:0; width:100%; z-index:999999; font-size:12px; opacity:0.8;">
            <a href="/" style="color:#fff; text-decoration:none; font-weight:bold;">[ NUEVA BÚSQUEDA ]</a> | 
            <span>Sitio: {target_url[:30]}...</span>
        </div>
        <div style="height:40px;"></div>
        """

        return top_bar + soup.prettify()

    except Exception as e:
        return f"Error: {str(e)} <br><a href='/'>Regresar</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
