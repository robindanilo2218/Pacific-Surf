from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# CSS que fuerza el "Look Notepad Blueprint" en TODO el sitio
BLUEPRINT_INJECTION = """
<style>
    * { 
        background-color: #003366 !important; 
        color: #E0FFFF !important; 
        font-family: 'Courier New', Courier, monospace !important;
        border-color: #00FFFF !important;
    }
    a { color: #00FFFF !important; text-decoration: underline !important; }
    input, button, select, textarea { 
        border: 1px solid #E0FFFF !important; 
        background: #002244 !important; 
        padding: 5px !important;
    }
    img, video { opacity: 0.3; filter: grayscale(100%) brightness(1.5) sepia(100%) hue-rotate(180deg); }
    /* Ajuste para letra grande y responsive */
    html { font-size: 1.4rem !important; }
    body { padding: 15px !important; line-height: 1.4 !important; }
</style>
"""

@app.route('/')
def home():
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="background:#003366; color:#E0FFFF; font-family:monospace; text-align:center; padding-top:100px;">
        <div style="border:2px solid #E0FFFF; padding:30px; display:inline-block; width:90%; max-width:500px;">
            <h1>PACIFIC-SURF v2.0</h1>
            <p>[FULL_STRUCTURE_BLUEPRINT]</p>
            <form action="/nav" method="get">
                <input type="text" name="url" style="width:100%; padding:10px;" placeholder="URL (ej: bbc.com)">
                <br><br>
                <button type="submit" style="width:100%; padding:10px; cursor:pointer;">INICIAR SISTEMA</button>
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

        # 1. Inyectamos nuestro ADN Blueprint en el <head>
        if soup.head:
            soup.head.append(BeautifulSoup(BLUEPRINT_INJECTION, 'html.parser'))
        else:
            # Si no hay head, lo creamos
            new_head = soup.new_tag("head")
            new_head.append(BeautifulSoup(BLUEPRINT_INJECTION, 'html.parser'))
            soup.insert(0, new_head)

        # 2. Reescritura de enlaces para no salir del proxy
        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"

        # 3. Mantenemos Scripts y Estilos originales pero con nuestra capa encima
        return f"""
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <div style="background:#002244; border-bottom:1px solid #00FFFF; padding:10px; position:sticky; top:0; z-index:9999;">
            <a href="/" style="color:#00FFFF; font-family:monospace;">[<< REBOOT]</a> | 
            <span style="color:#E0FFFF; font-family:monospace; font-size:0.8rem;">{target_url[:30]}</span>
        </div>
        {soup.prettify()}
        </html>
        """
    except Exception as e:
        return f"<html><body style='background:#003366; color:white;'>ERROR: {str(e)}</body></html>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
