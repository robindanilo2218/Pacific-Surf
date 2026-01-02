from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# CSS de alta precisión para evitar solapamientos y ordenar paneles
BLUEPRINT_FIX = """
<style>
    /* Forzar fondo y color en TODO */
    * { 
        background-color: #003366 !important; 
        color: #E0FFFF !important; 
        font-family: 'Courier New', Courier, monospace !important;
        box-sizing: border-box !important;
        max-width: 100% !important;
    }
    
    /* Evitar que las cosas se monten (Normalización de bloques) */
    div, section, article, aside, nav, header { 
        display: block !important; 
        position: relative !important; 
        float: none !important; 
        width: 100% !important; 
        margin: 10px 0 !important;
        padding: 10px !important;
        border: 1px solid #005588 !important;
        top: 0 !important;
        left: 0 !important;
    }

    /* Imágenes: Mejoramos visibilidad manteniendo el tono azul */
    img { 
        filter: cyan(100%) contrast(150%) brightness(80%) !important;
        opacity: 0.6 !important;
        height: auto !important;
    }

    /* Letra grande y legible */
    html { font-size: 1.3rem !important; }
    
    /* Enlaces brillantes */
    a { color: #00FFFF !important; font-weight: bold !important; }

    /* Ocultar elementos que suelen causar ruido visual */
    iframe, script, noscript, video, canvas { display: none !important; }
</style>
"""

@app.route('/')
def home():
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="background:#003366; color:#E0FFFF; font-family:monospace; text-align:center; padding:50px 20px;">
        <div style="border:2px solid #E0FFFF; padding:20px; display:inline-block; width:100%; max-width:450px;">
            <h1>PACIFIC-SURF v2.1</h1>
            <p>[STRUCTURE_FIX_DEPLOYED]</p>
            <form action="/nav" method="get">
                <input type="text" name="url" style="width:100%; padding:15px; background:#001122; color:#00FFFF; border:1px solid #00FFFF;" placeholder="URL o Búsqueda...">
                <br><br>
                <button type="submit" style="width:100%; padding:15px; background:#E0FFFF; color:#003366; font-weight:bold; cursor:pointer;">EJECUTAR</button>
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

        # Inyectamos el CSS corrector
        if soup.head:
            soup.head.append(BeautifulSoup(BLUEPRINT_FIX, 'html.parser'))
        else:
            new_head = soup.new_tag("head")
            new_head.append(BeautifulSoup(BLUEPRINT_FIX, 'html.parser'))
            soup.insert(0, new_head)

        # Reescritura de enlaces
        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"

        return f"""
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <div style="background:#001122; border-bottom:2px solid #00FFFF; padding:10px; position:sticky; top:0; z-index:10000; font-family:monospace;">
            <a href="/" style="color:#00FFFF;">[<< RESET]</a> | <span style="font-size:0.7rem;">{target_url[:25]}</span>
        </div>
        {soup.body.prettify() if soup.body else soup.prettify()}
        </html>
        """
    except Exception as e:
        return f"<html><body style='background:#003366; color:white;'>ERROR_RESOURCES: {str(e)}</body></html>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
