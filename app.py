from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# CSS que define la identidad visual Blueprint
BLUEPRINT_CSS = """
<style id="pacific-styles">
    body.blueprint, body.blueprint * { 
        background-color: #001a33 !important; 
        color: #00ffff !important; 
        font-family: 'Courier New', monospace !important;
        border-color: #005588 !important;
    }
    body.blueprint a { color: #e0ffff !important; text-decoration: underline !important; }
    
    /* El Engranaje de Ajustes */
    #settings-gear {
        position: fixed; bottom: 20px; right: 20px; z-index: 1000000;
        background: #00ffff; color: #000; border-radius: 50%;
        width: 50px; height: 50px; display: flex; align-items: center;
        justify-content: center; font-size: 24px; cursor: pointer; box-shadow: 0 0 10px #000;
    }
</style>
"""

JS_CONTROLS = """
<script>
    function toggleBlueprint() {
        document.body.classList.toggle('blueprint');
        localStorage.setItem('mode', document.body.classList.contains('blueprint') ? 'blue' : 'nat');
    }
    // Mantener el modo al cargar la página
    window.onload = () => {
        if(localStorage.getItem('mode') === 'blue') document.body.classList.add('blueprint');
    };
</script>
"""

@app.route('/')
def home():
    # ... (Mantenemos tu HOME_HTML actual de la v3.3) ...
    return render_template_string("<h1>PACIFIC SURF v3.4</h1><form action='/nav'><input name='url'><button>GO</button></form>")

@app.route('/nav')
def proxy():
    target_url = request.args.get('url')
    if not target_url: return home()
    if not target_url.startswith('http'): target_url = "https://" + target_url

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # FIX DE RUTAS Y LINKS (Lo que ya funcionaba)
        base_tag = soup.new_tag('base', href=target_url)
        soup.head.insert(0, base_tag) if soup.head else soup.insert(0, base_tag)

        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"

        # INYECCIÓN DEL ENGRANAJE Y ESTILOS STICKY
        settings_html = f'<div id="settings-gear" onclick="toggleBlueprint()">⚙️</div>'
        
        full_body = soup.body.prettify() if soup.body else soup.prettify()
        
        return f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {BLUEPRINT_CSS}
            {JS_CONTROLS}
        </head>
        <body class="blueprint">
            {settings_html}
            <div style="background:#000; color:#0ff; padding:5px; position:sticky; top:0; z-index:99999; font-size:10px; border-bottom:1px solid #0ff;">
                <a href="/" style="color:#0ff;">[NUEVA BÚSQUEDA]</a> | {target_url[:30]}
            </div>
            {full_body}
        </body>
        </html>
        """
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
