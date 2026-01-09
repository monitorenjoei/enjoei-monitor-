import requests
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

BUSCA_URL = "https://www.enjoei.com.br/search"
PALAVRA_CHAVE = "grêmio"
PRECO_MAX = 350
ARQUIVO_VISTOS = "vistos.json"

# Email (SMTP)
SMTP_HOST = os.environ["SMTP_HOST"]
SMTP_PORT = int(os.environ["SMTP_PORT"])
EMAIL_REMETENTE = os.environ["EMAIL_REMETENTE"]
EMAIL_SENHA = os.environ["EMAIL_SENHA"]
EMAIL_DESTINO = os.environ["EMAIL_DESTINO"]

def carregar_vistos():
    if os.path.exists(ARQUIVO_VISTOS):
        with open(ARQUIVO_VISTOS, "r") as f:
            return set(json.load(f))
    return set()

def salvar_vistos(vistos):
    with open(ARQUIVO_VISTOS, "w") as f:
        json.dump(list(vistos), f)

def enviar_email(assunto, corpo):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = EMAIL_DESTINO
    msg["Subject"] = assunto

    msg.attach(MIMEText(corpo, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)
        server.send_message(msg)

def buscar_anuncios():
    params = {
        "q": PALAVRA_CHAVE,
        "price_max": PRECO_MAX,
        "page": 1
    }
    r = requests.get(BUSCA_URL, params=params)
    r.raise_for_status()
    return r.json()["products"]

def main():
    vistos = carregar_vistos()
    produtos = buscar_anuncios()

    novos = []

    for p in produtos:
        titulo = p["title"].lower()
        preco = p["price_cents"] / 100
        link = f"https://www.enjoei.com.br/p/{p['id']}"

        if PALAVRA_CHAVE in titulo and preco <= PRECO_MAX:
            if link not in vistos:
                novos.append((p["title"], preco, link))
                vistos.add(link)

    if novos:
        corpo = ""
        for titulo, preco, link in novos:
            corpo += (
                f"📌 {titulo}\n"
                f"💰 R$ {preco:.2f}\n"
                f"{link}\n"
                f"{'-'*40}\n"
            )

        enviar_email(
            assunto="🛍️ Novo item do Grêmio no Enjoei",
            corpo=corpo
        )

    salvar_vistos(vistos)

if __name__ == "__main__":
    main()
