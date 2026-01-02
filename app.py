from flask import Flask, request, render_template_string
import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

# Estilo Blueprint Adaptable
UI_STYLE = """
    font-family: 'Courier New', Courier, monospace;
    background-color: #003366;
    color: #E0FFFF;
    line-height: 1.5;
    padding: 5vw;
    margin: 0;
    font-size: 1.2rem;
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
        <div style="border: 2px solid #E0FFFF; padding: 20px; display: inline-block; width: 90%; max-width: 600px;">
            <h1 style="font-size: 1.8rem; margin:0;">PACIFIC-SURF v1.6</h1>
            <p style="font-size: 0.8rem;">[READY_TO_SURF]</p>
            <hr style="border: 1px dashed #E0FFFF;">
            <form action="/nav" method="get">
                <input type="text" name="url" style="width: 100%; background: #001122; color: #00FFFF; border: 1px solid #00FFFF; padding: 15px; font-size: 1rem;" placeholder="Search or URL...">
                <br><br>
                <button type="submit" style="width: 100%; background: #E0FFFF; color: #003366; border: none; padding: 15px; font-weight: bold; cursor: pointer; font-size: 1rem;">EXECUTE_COMMAND</button>
            </form>
        </div>
    </body></html>
    """)

@app.route('/nav')
def proxy():
    query = request.args.get('url')
    if not query: return home()
    target_url = query if query.startswith('http') else f"https://www.google.com/search?q={query}&gbv=1"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}

    try:
        session = requests.Session()
        response = session.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style", "nav", "footer", "header", "img", "video", "iframe"]):
            tag.decompose()
        for a in soup.find_all('a', href=True):
            a['href'] = f"/nav?{urlencode({'url': urljoin(target_url, a['href'])})}"
            a['style'] = "color: #00FFFF; font-weight: bold;"
        
        text_data = soup.get_text(separator='\n')
        text_data = re.sub(r'\n\s*\n', '\n\n', text_data)

        return f"""
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body style="{UI_STYLE}">
            <div style="border-bottom: 2px solid #E0FFFF; margin-bottom: 20px; font-size: 0.9rem;">
                <a href="/" style="color: #E0FFFF;">[<< BACK]</a> | VIEW: {target_url[:20]}...
            </div>
            <div style="white-space: pre-wrap; word-wrap: break-word; width: 100%;">{text_data.strip()}</div>
        </body></html>
        """
    except Exception as e:
        return f"<body style='{UI_STYLE}'>ERROR: {str(e)} <br><a href='/'>RETRY</a></body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
