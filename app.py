from flask import Flask, request, render_template_string
import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

HOME_HTML = """
<html>
<body style='font-family: monospace; padding: 20px; background: #fff;'>
    <div style='border: 2px solid #000; padding: 15px;'>
        <h2 style='margin:0;'>PACIFIC-SURF v1.3</h2>
        <p style='font-size:10px;'>[ULTRA-COMPACT MODE]</p>
        <form action="/nav" method="get">
            <input type="text" name="url" style="width: 100%; border:1px solid #000;" placeholder="Busca en Google o pega URL...">
            <br><br>
            <button type="submit" style='width:100%; background:#000; color:#fff; border:none; padding:10px;'>NAVEGAR</button>
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

    # Si no es URL, usamos Google Search (es más difícil que bloquee texto plano)
    if not (query.startswith('http://') or query.startswith('https://')):
        target_url = f"https://www.google.com/search?q={query}&gbv=1" # gbv=1 pide versión sin JS
    else:
        target_url = query
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', # Disfraz de bot de Google
        'Accept-Language': 'es-ES,es;q=0.9'
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Limpieza de elementos molestos
        for tag in soup(["script", "style", "nav", "footer", "header", "img", "video", "iframe", "ad", "button", "input"]):
            tag.decompose()

        # Reescritura de enlaces
        for a in soup.find_all('a', href=True):
            # Limpiar redirecciones de Google en los enlaces
            actual_href = a['href']
            if '/url?q=' in actual_href:
                actual_href = actual_href.split('/url?q=')[1].split('&')[0]
            
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, actual_href)})}"

        # Compresión de texto
        text_data = soup.get_text(separator=' ')
        text_data = re.sub(r'\n\s*\n', '\n', text_data)
        text_data = re.sub(r' +', ' ', text_data)

        return f"""
        <html>
        <body style='font-family: monospace; font-size: 13px; line-height: 1.2; padding: 10px; background: #fff;'>
            <div style='border-bottom: 1px dotted #000; margin-bottom: 10px;'>
                <a href="/">[ INICIO ]</a> | SRC: {target_url[:25]}...
            </div>
            <div style='white-space: pre-wrap;'>{text_data.strip()}</div>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error: {str(e)} <br> <a href='/'>Volver</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
