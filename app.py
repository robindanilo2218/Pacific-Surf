from flask import Flask, request, render_template_string
import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Estilo Blueprint Adaptable con letra más grande (1.4rem)
UI_STYLE = """
    font-family: 'Courier New', Courier, monospace;
    background-color: #003366;
    color: #E0FFFF;
    line-height: 1.6;
    padding: 5%;
    margin: 0;
    font-size: 1.4rem; 
"""

@app.route('/')
def home():
    return render_template_string(f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
        <title>PACIFIC-SURF</title>
    </head>
    <body style="{UI_STYLE} text-align: center; display: flex; align-items: center; justify-content: center; height: 100vh;">
        <div style="border: 3px solid #E0FFFF; padding: 30px; width: 95%; max-width: 500px;">
            <h1 style="font-size: 2rem; margin:0;">PACIFIC-SURF</h1>
            <p style="font-size: 0.9rem; color:#00FFFF;">[ BLUEPRINT_V1.7_LIVE ]</p>
            <hr style="border: 1px dashed #E0FFFF; margin: 20px 0;">
            <form action="/nav" method="get">
                <input type="text" name="url" style="width: 100%; background: #001122; color: #00FFFF; border: 1px solid #00FFFF; padding: 15px; font-size: 1.2rem;" placeholder="Escribe una URL directa...">
                <br><br>
                <button type="submit" style="width: 100%; background: #E0FFFF; color: #003366; border: none; padding: 15px; font-weight: bold; font-size: 1.2rem; cursor: pointer;">EJECUTAR</button>
            </form>
            <p style="font-size: 0.8rem; margin-top: 15px;">Tip: Usa URLs directas para evitar bloqueos.</p>
        </div>
    </body></html>
    """)

@app.route('/nav')
def proxy():
    target_url = request.args.get('url')
    if not target_url: return home()
    
    if not target_url.startswith('http'):
        target_url = "https://" + target_url

    # Cabecera de móvil para forzar versiones ligeras
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'}

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for tag in soup(["script", "style", "nav", "footer", "header", "img", "video", "iframe"]):
            tag.decompose()
        
        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"
            a['style'] = "color: #00FFFF; font-weight: bold; text-decoration: underline;"
        
        text_data = soup.get_text(separator='\n\n')
        text_data = re.sub(r'\n\s*\n', '\n\n', text_data)

        return f"""
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body style="{UI_STYLE}">
            <div style="border-bottom: 2px solid #E0FFFF; margin-bottom: 20px; font-size: 1rem;">
                <a href="/" style="color: #E0FFFF; text-decoration: none;">[<< INICIO]</a> | {target_url[:25]}
            </div>
            <div style="white-space: pre-wrap; word-wrap: break-word;">{text_data.strip()}</div>
        </body></html>
        """
    except Exception as e:
        return f"<body style='{UI_STYLE}'>ERROR_DE_ACCESO: El sitio bloqueó la conexión. <br><br> <a href='/' style='color:#00FFFF;'>VOLVER</a></body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
