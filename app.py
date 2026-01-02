from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Plantilla HTML Minimalista (Estilo Block de Notas)
HOME_HTML = """
<html>
<body style='font-family: monospace; padding: 50px; text-align: center;'>
    <h1>TEXT BROWSER v1.0</h1>
    <p>Ingresa una URL o un término de búsqueda:</p>
    <form action="/nav" method="get">
        <input type="text" name="url" style="width: 80%; padding: 10px;" placeholder="https://... o buscar algo">
        <br><br>
        <input type="submit" value="NAVEGAR / BUSCAR">
    </form>
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

    # Si no empieza con http, lo enviamos a DuckDuckGo
    if not query.startswith('http'):
        target_url = f"https://duckduckgo.com/html/?q={query}"
    else:
        target_url = query

    try:
        response = requests.get(target_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')

        # Limpieza
        for tag in soup(["script", "style", "nav", "footer", "header", "img", "video"]):
            tag.decompose()

        # Reescritura de enlaces
        for a in soup.find_all('a', href=True):
            full_url = urljoin(target_url, a['href'])
            a['href'] = f"/nav?{urlencode({'url': full_url})}"

        content = soup.find('body')
        return f"""
        <html>
        <body style='font-family: monospace; padding: 20px; max-width: 800px; margin: auto;'>
            <div style='border-bottom: 2px solid #000; margin-bottom: 10px;'>
                <a href="/">[ INICIO ]</a> | Viendo: {target_url}
            </div>
            <pre style='white-space: pre-wrap;'>{content.get_text() if content else "Sin contenido"}</pre>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(port=5000)
