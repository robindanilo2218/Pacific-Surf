from flask import Flask, request, render_template_string
import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Estilo Blueprint con letra grande y adaptable
UI_STYLE = """
    font-family: 'Courier New', Courier, monospace;
    background-color: #003366;
    color: #E0FFFF;
    line-height: 1.6;
    padding: 20px;
    margin: 0;
    font-size: 1.4rem; 
"""

@app.route('/')
def home():
    return render_template_string(f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PACIFIC-SURF</title>
    </head>
    <body style="{UI_STYLE} text-align: center;">
        <div style="border: 3px solid #E0FFFF; padding: 30px; margin-top: 50px; display: inline-block; width: 90%; max-width: 600px;">
            <h1>PACIFIC-SURF</h1>
            <p style="font-size: 0.9rem;">[BLUEPRINT_V1.7_LIVE]</p>
            <hr style="border: 1px dashed #E0FFFF; margin: 20px 0;">
            <form action="/nav" method="get">
                <input type="text" name="url" style="width: 100%; background: #001122; color: #00FFFF; border: 1px solid #00FFFF; padding: 15px; font-size: 1.2rem;" placeholder="Pega una URL (ej: wikipedia.org)">
                <br><br>
                <button type="submit" style="width: 100%; background: #E0FFFF; color: #003366; border: none; padding: 15px; font-weight: bold; font-size: 1.2rem; cursor: pointer;">EJECUTAR</button>
            </form>
            <p style="font-size: 0.8rem; margin-top: 20px; color: #00FFFF;">Nota: Evita buscar palabras sueltas para no ser bloqueado por Google. Usa URLs directas.</p>
        </div>
    </body></html>
    """)

@app.route('/nav')
def proxy():
    query = request.args.get('url')
    if not query: return home()

    # Si no tiene protocolo, se lo ponemos
    target_url = query if query.startswith('http') else f"https://{query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Limpieza de basura
        for tag in soup(["script", "style", "nav", "footer", "header", "img", "video", "iframe"]):
            tag.decompose()

        # Reescritura de enlaces
        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"
            a['style'] = "color: #00FFFF; font-weight: bold; text-decoration: underline;"

        text_data = soup.get_text(separator='\n\n')
        text_data = re.sub(r'\n\s*\n', '\n\n', text_data)

        return f"""
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body style="{UI_STYLE}">
            <div style="border-bottom: 2px solid #E0FFFF; margin-bottom: 20px; padding-bottom: 10px; font-size: 1rem;">
                <a href="/" style="color: #E0FFFF; text-decoration: none;">[<< INICIO]</a> | URL: {target_url[:25]}...
            </div>
            <div style="white-space: pre-wrap; word-wrap: break-word;">{text_data.strip()}</div>
        </body></html>
        """
    except Exception as e:
        return f"<body style='{UI_STYLE}'>ERROR: No se pudo cargar la página. Es posible que el sitio bloquee proxies. <br><br> <a href='/' style='color:#00FFFF;'>VOLVER</a></body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
