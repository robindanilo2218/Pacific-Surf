from flask import Flask, request, render_template_string
import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Estilo Blueprint con soporte para Paneles Laterales
UI_STYLE = """
    font-family: 'Courier New', Courier, monospace;
    background-color: #003366;
    color: #E0FFFF;
    line-height: 1.5;
    padding: 0;
    margin: 0;
    font-size: 1.4rem; 
"""

@app.route('/')
def home():
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="{UI_STYLE} text-align: center; display: flex; align-items: center; justify-content: center; height: 100vh;">
        <div style="border: 3px solid #E0FFFF; padding: 30px; width: 90%; max-width: 500px;">
            <h1>PACIFIC-SURF</h1>
            <p>[SIDEBAR_SUPPORT_ENABLED]</p>
            <form action="/nav" method="get">
                <input type="text" name="url" style="width: 100%; background: #001122; color: #00FFFF; border: 1px solid #00FFFF; padding: 15px; font-size: 1.2rem;" placeholder="Pega URL (ej: bbc.com)">
                <br><br>
                <button type="submit" style="width: 100%; background: #E0FFFF; color: #003366; border: none; padding: 15px; font-weight: bold; cursor: pointer;">EXPLORAR</button>
            </form>
        </div>
    </body></html>
    """)

@app.route('/nav')
def proxy():
    target_url = request.args.get('url')
    if not target_url: return home()
    if not target_url.startswith('http'): target_url = "https://" + target_url

    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'}

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # YA NO BORRAMOS 'nav' ni 'aside' para mantener menús
        for tag in soup(["script", "style", "img", "video", "iframe", "footer", "header"]):
            tag.decompose()

        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"
            a['style'] = "color: #00FFFF; text-decoration: underline;"

        # Estilizamos los paneles laterales/menús para que resalten
        for sidebar in soup.find_all(['nav', 'aside']):
            sidebar['style'] = "border: 1px dashed #E0FFFF; padding: 10px; margin-bottom: 20px; background: #002244; font-size: 1.1rem;"

        return f"""
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body style="{UI_STYLE}">
            <div style="border-bottom: 2px solid #E0FFFF; padding: 10px; position: sticky; top: 0; background: #003366; z-index: 100;">
                <a href="/" style="color: #E0FFFF;">[<< HOME]</a> | {target_url[:20]}...
            </div>
            <div style="padding: 15px; white-space: pre-wrap; word-wrap: break-word;">{soup.prettify()}</div>
        </body></html>
        """
    except Exception as e:
        return f"<body style='{UI_STYLE}'>ERROR: {str(e)} <br><a href='/'>REINTENTAR</a></body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
