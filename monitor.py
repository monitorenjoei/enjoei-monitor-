import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.mime.text import MIMEText
from pathlib import Path

SEARCH_URL = "https://www.enjoei.com.br/s?q=grêmio"

EMAIL_FROM = "SEU_EMAIL@gmail.com"
EMAIL_TO = "SEU_EMAIL@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_PASSWORD = "SENHA_DO_APP"

SEEN_FILE = Path("seen_ads.json")
SEEN_FILE.touch(exist_ok=True)

seen_ads = json.loads(SEEN_FILE.read_text() or "[]")

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(SEARCH_URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

new_ads = []

for item in soup.select("a[data-testid='product-card']"):
    title = item.get_text(strip=True)
    link = "https://www.enjoei.com.br" + item["href"]

    if "grêmio" in title.lower() and link not in seen_ads:
        new_ads.append((title, link))
        seen_ads.append(link)

if new_ads:
    body = "\n\n".join([f"{t}\n{l}" for t, l in new_ads])

    msg = MIMEText(body)
    msg["Subject"] = "🟦 Novo anúncio do Grêmio no Enjoei"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)

SEEN_FILE.write_text(json.dumps(seen_ads))
