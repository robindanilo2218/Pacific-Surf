from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Interfaz de usuario minimalista
HOME_HTML = """
<html>
<body style='font-family: monospace; padding: 30px; background-color: #f4f4f4; color: #333;'>
    <div style='max-width: 600px; margin: auto; border: 2px solid #000; padding: 20px; background: #fff;'>
        <h1 style='text-align: center;'>PACIFIC-SURF v1.1</h1>
        <p style='text-align: center;'>Text-Only Web Proxy</p>
        <form action="/nav" method="get" style='text-align: center;'>
            <input type="text" name="url" style="width: 90%; padding: 10px; border: 1px solid #000;" placeholder="Search or enter URL...">
            <br><br>
            <input type="submit" value="GO" style='padding: 10px 20px; background: #000; color: #fff; border: none; cursor: pointer;'>
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

    # Detectar si es búsqueda o URL directa
    if not (query.startswith('http://') or query.startswith('https://')):
        target_url = f"https://html.duckduckgo.com/html/?q={query}"
    else:
        target_url = query

    # Cabeceras profesionales para evitar bloqueos de bots
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Limpieza profunda de ruido visual
        for tag in soup(["script", "style", "nav", "footer", "header", "img", "video", "iframe", "noscript", "svg"]):
            tag.decompose()

        # Reescritura de enlaces para navegación continua
        for a in soup.find_all('a', href=True):
            full_url = urljoin(target_url, a['href'])
            a['href'] = f"/nav?{urlencode({'url': full_url})}"

        content = soup.find('body')
        text_data = content.get_text(separator='\n\n') if content else "No content found."

        return f"""
        <html>
        <body style='font-family: monospace; line-height: 1.6; padding: 20px; max-width: 800px; margin: auto; background: #fff;'>
            <div style='border-bottom: 2px solid #000; margin-bottom: 20px; padding-bottom: 10px;'>
                <a href="/">[ HOME ]</a> | <strong>Viewing:</strong> {target_url[:50]}...
            </div>
            <div style='white-space: pre-wrap;'>{text_data}</div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>Navigation Error</h1><p>{str(e)}</p><a href='/'>Go Back</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
