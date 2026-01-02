from flask import Flask, request, render_template_string
import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# CONFIGURACIÓN VISUAL (Consolidada de versiones anteriores)
BLUEPRINT_STYLE = """
<style>
    * { 
        background-color: #003366 !important; 
        color: #E0FFFF !important; 
        font-family: 'Courier New', Courier, monospace !important;
        box-sizing: border-box !important;
    }
    html { font-size: 1.4rem !important; } /* Letra grande solicitada */
    body { margin: 0; padding: 15px; line-height: 1.5; }
    
    /* Mantiene paneles en su lugar pero con nuestro estilo */
    div, section, aside, nav { border: 1px solid #00FFFF !important; padding: 5px; }
    
    /* Enlaces Blueprint */
    a { color: #00FFFF !important; text-decoration: underline !important; }
    
    /* Imágenes blueprintizadas */
    img { filter: cyan(100%) opacity(0.5); max-width: 100%; height: auto; }
</style>
"""

@app.route('/')
def home():
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="background:#003366; color:#E0FFFF; font-family:monospace; text-align:center; padding-top:100px;">
        <div style="border:2px solid #E0FFFF; padding:30px; display:inline-block; width:90%; max-width:500px;">
            <h1>PACIFIC-SURF v2.3</h1>
            <p>[SYSTEM_STABLE_REVISION]</p>
            <form action="/nav" method="get">
                <input type="text" name="url" style="width:100%; padding:10px; background:#001122; color:#00FFFF; border:1px solid #00FFFF;" placeholder="URL (ej: bbc.com)">
                <br><br>
                <button type="submit" style="width:100%; padding:10px; background:#E0FFFF; color:#003366; font-weight:bold;">EJECUTAR</button>
            </form>
        </div>
    </body></html>
    """)

@app.route('/nav')
def proxy():
    target_url = request.args.get('url')
    if not target_url: return home()
    if not target_url.startswith('http'): target_url = "https://" + target_url

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. REESCRITURA DE ENLACES (Para navegación interna)
        for a in soup.find_all('a', href=True):
            original_link = urljoin(target_url, a['href'])
            a['href'] = f"/nav?{urlencode({'url': original_link})}"

        # 2. INYECCIÓN DE ESTILO (Sin romper la estructura original)
        if soup.head:
            soup.head.append(BeautifulSoup(BLUEPRINT_STYLE, 'html.parser'))
        else:
            new_head = soup.new_tag("head")
            new_head.append(BeautifulSoup(BLUEPRINT_STYLE, 'html.parser'))
            soup.insert(0, new_head)

        # 3. BARRA DE CONTROL SUPERIOR
        nav_bar = f"""
        <div style="background:#001122; border-bottom:2px solid #00FFFF; padding:10px; position:sticky; top:0; z-index:9999; font-family:monospace; font-size:1rem;">
            <a href="/" style="color:#00FFFF;">[<< RESET]</a> | <span>{target_url[:25]}...</span>
        </div>
        """

        return f"""
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        {nav_bar}
        {soup.prettify()}
        </html>
        """
    except Exception as e:
        return f"ERROR: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
