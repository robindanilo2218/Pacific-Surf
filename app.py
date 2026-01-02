from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Interfaz inicial limpia
HOME_HTML = """
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: 'Courier New', monospace; background: #001a33; color: #e0ffff; text-align: center; padding: 50px; }
        .terminal { border: 2px solid #00ffff; padding: 20px; display: inline-block; background: #002b4d; }
        input { background: #000; color: #00ffff; border: 1px solid #00ffff; padding: 10px; width: 80%; margin-bottom: 10px; }
        button { background: #00ffff; color: #001a33; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="terminal">
        <h1>PACIFIC SURF v3.3</h1>
        <p>[ NAVEGACIÓN NATURAL ]</p>
        <form action="/nav" method="get">
            <input type="text" name="url" placeholder="URL o Búsqueda..." required>
            <br>
            <button type="submit">INICIAR SESIÓN</button>
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

    target_url = query if query.startswith('http') else f"https://www.google.com/search?q={query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
    }

    try:
        # Iniciamos sesión para manejar persistencia
        session = requests.Session()
        response = session.get(target_url, headers=headers, timeout=15)
        
        # FIX DE CARACTERES: Forzamos UTF-8 para evitar "FranÃ§ais"
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # FIX DE RUTAS: Inyectamos <base> para que el navegador busque estilos en el sitio original
        base_tag = soup.new_tag('base', href=target_url)
        if soup.head:
            soup.head.insert(0, base_tag)
        else:
            new_head = soup.new_tag('head')
            new_head.insert(0, base_tag)
            soup.insert(0, new_head)

        # REESCRITURA DE ENLACES: Para no salir nunca del proxy
        for a in soup.find_all('a', href=True):
            full_url = urljoin(target_url, a['href'])
            a['href'] = f"/nav?{urlencode({'url': full_url})}"

        # BARRA DE HERRAMIENTAS INTEGRADA
        top_bar = f"""
        <div style="background:#000; color:#0ff; padding:8px; font-family:monospace; position:fixed; top:0; width:100%; z-index:999999; border-bottom:1px solid #0ff; opacity:0.9;">
            <a href="/" style="color:#0ff; text-decoration:none;">[ NUEVA_BÚSQUEDA ]</a> | 
            <span style="font-size:10px;">CONECTADO_A: {target_url[:35]}...</span>
        </div>
        <div style="height:40px;"></div>
        """

        return top_bar + soup.prettify()

    except Exception as e:
        return f"<html><body style='background:#000; color:red;'>ERROR_DE_SISTEMA: {str(e)}<br><a href='/'>REINTENTAR</a></body></html>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
