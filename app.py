from flask import Flask, request, render_template_string
import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

HOME_HTML = """
<html>
<body style='font-family: monospace; padding: 20px; background: #fff;'>
    <div style='border: 1px solid #000; padding: 15px;'>
        <h3>PACIFIC-SURF v1.2 [ULTRA-COMPACT]</h3>
        <form action="/nav" method="get">
            <input type="text" name="url" style="width: 100%;" placeholder="Search or URL...">
            <br><br>
            <button type="submit">LOAD TEXT</button>
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

    target_url = query if query.startswith('http') else f"https://html.duckduckgo.com/html/?q={query}"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0 Safari/537.36'}

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Limpieza agresiva
        for tag in soup(["script", "style", "nav", "footer", "header", "img", "video", "iframe", "ad"]):
            tag.decompose()

        # Reescritura de enlaces
        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"

        # COMPRESIÓN EXTREMA: Limpiar saltos de línea duplicados
        raw_text = soup.get_text(separator=' ')
        clean_text = re.sub(r'\n\s*\n', '\n', raw_text) # Elimina líneas vacías
        clean_text = re.sub(r' +', ' ', clean_text)     # Elimina espacios dobles

        return f"""
        <html>
        <body style='font-family: monospace; font-size: 12px; padding: 10px; background: #fff; color: #000;'>
            <div style='border-bottom: 1px solid #000; margin-bottom: 10px;'>
                <a href="/">[TOP]</a> | SRC: {target_url[:30]}...
            </div>
            <div style='white-space: pre-wrap;'>{clean_text.strip()}</div>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
