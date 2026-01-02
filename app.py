from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Estilos Blueprint con corrección de solapamiento
BLUEPRINT_CORE = """
<style>
    * { 
        background-color: #003366 !important; 
        color: #E0FFFF !important; 
        font-family: 'Courier New', Courier, monospace !important;
        box-sizing: border-box !important;
    }
    div, section, article, aside, nav, header { 
        display: block !important; 
        width: 100% !important; 
        position: relative !important;
        margin-bottom: 10px !important;
        padding: 10px !important;
        border: 1px solid #005588 !important;
    }
    a { color: #00FFFF !important; font-weight: bold !important; text-decoration: underline !important; }
    img { filter: cyan(100%) brightness(80%); opacity: 0.5; max-width: 100%; height: auto; }
    html { font-size: 1.4rem; }
</style>
"""

@app.route('/')
def home():
    return render_template_string("""
    <body style="background:#003366; color:#E0FFFF; font-family:monospace; text-align:center; padding-top:50px;">
        <div style="border:2px solid #E0FFFF; padding:20px; display:inline-block; width:90%; max-width:400px;">
            <h1>PACIFIC-SURF v2.2</h1>
            <p>[INFINITE_NAV_ENABLED]</p>
            <form action="/nav" method="get">
                <input type="text" name="url" style="width:100%; padding:10px;" placeholder="URL (ej: bbc.com)">
                <br><br>
                <button type="submit" style="width:100%; padding:10px;">EJECUTAR</button>
            </form>
        </div>
    </body>
    """)

@app.route('/nav')
def proxy():
    target_url = request.args.get('url')
    if not target_url: return home()
    if not target_url.startswith('http'): target_url = "https://" + target_url

    try:
        response = requests.get(target_url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- EL SECRETO DE LA NAVEGACIÓN DENTRO DE PACIFIC-SURF ---
        for a in soup.find_all('a', href=True):
            # 1. Convertimos el link en una ruta completa (absoluta)
            original_link = urljoin(target_url, a['href'])
            # 2. Re-escribimos el link para que apunte de nuevo a nuestro proxy
            a['href'] = f"/nav?{urlencode({'url': original_link})}"
        # ---------------------------------------------------------

        if soup.head:
            soup.head.append(BeautifulSoup(BLUEPRINT_CORE, 'html.parser'))
        
        return f"""
        <div style="background:#001122; border-bottom:1px solid #00FFFF; padding:10px; position:sticky; top:0; z-index:999;">
            <a href="/">[<< EXIT]</a> | <span style="font-size:0.7rem;">{target_url[:30]}</span>
        </div>
        {soup.body.prettify() if soup.body else soup.prettify()}
        """
    except Exception as e:
        return f"ERROR: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
