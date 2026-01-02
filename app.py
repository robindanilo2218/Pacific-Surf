from flask import Flask, request, render_template_string
import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Estilo Blueprint: Fondo Azul Técnico, Letras Blanco-Cian
UI_STYLE = """
    font-family: 'Courier New', Courier, monospace;
    background-color: #003366;
    color: #E0FFFF;
    line-height: 1.3;
    padding: 15px;
"""

HOME_HTML = f"""
<html>
<body style="{UI_STYLE} text-align: center;">
    <div style="border: 2px solid #E0FFFF; padding: 20px; display: inline-block; max-width: 90%;">
        <h2 style="margin:0;">PACIFIC-SURF v1.4</h2>
        <p style="font-size:12px;">[BLUEPRINT ENGINE ACTIVE]</p>
        <hr style="border: 1px dashed #E0FFFF;">
        <form action="/nav" method="get">
            <input type="text" name="url" style="width: 100%; background: #002244; color: #E0FFFF; border: 1px solid #E0FFFF; padding: 10px;" placeholder="Search or URL...">
            <br><br>
            <button type="submit" style="width: 100%; background: #E0FFFF; color: #003366; border: none; padding: 10px; font-weight: bold; cursor: pointer;">
                EXECUTE COMMAND
            </button>
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

    # Fallback a Google Search con interfaz básica (gbv=1)
    target_url = query if query.startswith('http') else f"https://www.google.com/search?q={query}&gbv=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'Accept-Language': 'es-ES,es;q=0.9'
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Limpieza extrema de ruido
        for tag in soup(["script", "style", "nav", "footer", "header", "img", "video", "iframe", "ad", "button", "input"]):
            tag.decompose()

        # Reescritura de enlaces
        for a in soup.find_all('a', href=True):
            actual_href = a['href']
            if '/url?q=' in actual_href:
                actual_href = actual_href.split('/url?q=')[1].split('&')[0]
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, actual_href)})}"
            a['style'] = "color: #00FFFF; font-weight: bold;" # Enlaces en color Cian brillante

        # Procesamiento de texto
        text_data = soup.get_text(separator=' ')
        text_data = re.sub(r'\n\s*\n', '\n', text_data)
        text_data = re.sub(r' +', ' ', text_data)

        return f"""
        <html>
        <body style="{UI_STYLE}">
            <div style="border-bottom: 2px solid #E0FFFF; margin-bottom: 15px; padding-bottom: 5px;">
                <a href="/" style="color: #E0FFFF;">[ BACK_TO_BASE ]</a> | SRC: {target_url[:20]}...
            </div>
            <div style="white-space: pre-wrap;">{text_data.strip()}</div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<body style='{UI_STYLE}'>Error: {str(e)} <br><br> <a href='/' style='color:#E0FFFF;'>Return</a></body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
