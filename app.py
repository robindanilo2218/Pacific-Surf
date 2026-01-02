from flask import Flask, request, render_template_string
import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Paleta Blueprint: Fondo #003366, Texto #E0FFFF, Enlaces #00FFFF
UI_STYLE = """
    font-family: 'Courier New', Courier, monospace;
    background-color: #003366;
    color: #E0FFFF;
    line-height: 1.4;
    padding: 20px;
    margin: 0;
"""

HOME_HTML = f"""
<html>
<head><title>PACIFIC-SURF TERMINAL</title></head>
<body style="{UI_STYLE} text-align: center; display: flex; flex-direction: column; justify-content: center; height: 90vh;">
    <div style="border: 2px solid #E0FFFF; padding: 30px; display: inline-block; background: #002244; box-shadow: 10px 10px 0px #001122;">
        <h1 style="margin:0; letter-spacing: 5px;">PACIFIC-SURF v1.4</h1>
        <p style="font-size:12px; color: #00FFFF;">[ SYSTEM_READY // BLUEPRINT_MODE ]</p>
        <hr style="border: 1px dashed #E0FFFF; margin: 20px 0;">
        <form action="/nav" method="get">
            <input type="text" name="url" style="width: 100%; background: #001122; color: #00FFFF; border: 1px solid #E0FFFF; padding: 12px; font-family: monospace;" placeholder="ENTER_URL_OR_QUERY..." autofocus>
            <br><br>
            <button type="submit" style="width: 100%; background: #E0FFFF; color: #003366; border: none; padding: 12px; font-weight: bold; font-family: monospace; cursor: pointer;">
                EXECUTE_COMMAND
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

    target_url = query if query.startswith('http') else f"https://www.google.com/search?q={query}&gbv=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Eliminación selectiva de basura visual
        for tag in soup(["script", "style", "nav", "footer", "header", "img", "video", "iframe", "ad", "button", "input"]):
            tag.decompose()

        # Normalización de enlaces con estilo Cyan
        for a in soup.find_all('a', href=True):
            actual_href = a['href']
            if '/url?q=' in actual_href:
                actual_href = actual_href.split('/url?q=')[1].split('&')[0]
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, actual_href)})}"
            a['style'] = "color: #00FFFF; text-decoration: underline;"

        # Limpieza de texto y saltos de línea
        text_data = soup.get_text(separator='\n')
        text_data = re.sub(r'\n\s*\n', '\n\n', text_data)

        return f"""
        <html>
        <body style="{UI_STYLE}">
            <div style="border-bottom: 2px solid #E0FFFF; margin-bottom: 20px; padding-bottom: 10px; display: flex; justify-content: space-between;">
                <a href="/" style="color: #E0FFFF; text-decoration: none;">[<< REBOOT_SYSTEM]</a>
                <span style="color: #00FFFF;">LOG_VIEW: {target_url[:30]}...</span>
            </div>
            <div style="white-space: pre-wrap; font-size: 14px;">{text_data.strip()}</div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<body style='{UI_STYLE}'>CRITICAL_ERROR: {str(e)} <br><br> <a href='/' style='color:#00FFFF;'>[RETRY]</a></body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
