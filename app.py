from flask import Flask, request, render_template_string
import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Paleta Blueprint Optimizada
UI_STYLE = """
    font-family: 'Courier New', Courier, monospace;
    background-color: #003366;
    color: #E0FFFF;
    line-height: 1.5;
    padding: 20px;
"""

@app.route('/')
def home():
    return render_template_string(f"""
    <html><body style="{UI_STYLE} text-align: center;">
        <div style="border: 2px solid #E0FFFF; padding: 20px; display: inline-block;">
            <h1>PACIFIC-SURF v1.5</h1>
            <p>[STATUS: ENCRYPTED_TUNNEL_ACTIVE]</p>
            <form action="/nav" method="get">
                <input type="text" name="url" style="width: 80%; background: #001122; color: #00FFFF; border: 1px solid #00FFFF; padding: 10px;" placeholder="URL o Búsqueda...">
                <button type="submit" style="background: #E0FFFF; color: #003366; border: none; padding: 10px; cursor: pointer;">EJECUTAR</button>
            </form>
        </div>
    </body></html>
    """)

@app.route('/nav')
def proxy():
    query = request.args.get('url')
    if not query: return home()

    target_url = query if query.startswith('http') else f"https://www.google.com/search?q={query}&gbv=1"
    
    # CABECERAS AVANZADAS: Emulando un navegador Chrome Real en Windows
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }

    try:
        # Iniciamos una sesión para manejar cookies automáticamente
        session = requests.Session()
        response = session.get(target_url, headers=headers, timeout=15)
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Limpiar basura visual
        for tag in soup(["script", "style", "nav", "footer", "header", "img", "video", "iframe", "ad"]):
            tag.decompose()

        # Reescritura de enlaces
        for a in soup.find_all('a', href=True):
            full_url = urljoin(target_url, a['href'])
            a['href'] = f"/nav?{urlencode({'url': full_url})}"
            a['style'] = "color: #00FFFF;"

        text_data = soup.get_text(separator='\n')
        text_data = re.sub(r'\n\s*\n', '\n\n', text_data)

        return f"""
        <html><body style="{UI_STYLE}">
            <div style="border-bottom: 2px solid #E0FFFF; margin-bottom: 20px;">
                <a href="/" style="color: #E0FFFF;">[<< RESET]</a> | VIEWING: {target_url[:40]}...
            </div>
            <div style="white-space: pre-wrap;">{text_data.strip()}</div>
        </body></html>
        """
    except Exception as e:
        return f"<body style='{UI_STYLE}'>ACCESS_DENIED: {str(e)} <br><a href='/'>RETRY</a></body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
