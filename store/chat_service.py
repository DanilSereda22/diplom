
import requests
import urllib3
import uuid
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GIGACHAT_AUTH = "MDE5ZGYzYTUtNWRmZC03NjQ4LWJiNzUtNGYzZDA2ZGNmMDY4OjM5NjYxZWQxLTI2ZjQtNGQzOS1iNjU0LTQxZGU0NDZlMmU0Mw=="


# ================= TOKEN =================
def get_access_token():
    try:
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {GIGACHAT_AUTH}"
        }

        payload = {
            "scope": "GIGACHAT_API_PERS",
            "grant_type": "client_credentials"
        }

        res = requests.post(url, headers=headers, data=payload, verify=False, timeout=10)

        if res.status_code != 200:
            print("TOKEN ERROR:", res.text)
            return None

        return res.json().get("access_token")

    except Exception as e:
        print("TOKEN EXCEPTION:", e)
        return None


# ================= AI =================
def ask_gigachat(message):
    token = get_access_token()

    if not token:
        return "❌ AI временно недоступен"

    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "system", "content": "Ты помощник магазина сладостей. Отвечай коротко."},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    res = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)

    if res.status_code != 200:
        print("GIGA ERROR:", res.text)
        return "❌ Ошибка AI"

    return res.json()["choices"][0]["message"]["content"]


# ================= ЛОГИКА =================

def extract_budget(text):
    match = re.search(r'(\d+)\s*(₽|руб|рублей)?', text.lower())
    return int(match.group(1)) if match else None


def get_products_for_budget(budget):
    from .models import Product

    products = Product.objects.filter(available=True, stock__gt=0).order_by('price')

    total = 0
    result = []

    for p in products:
        if total + p.final_price <= budget:
            result.append({
                "slug": p.slug,
                "name": p.name,
                "price": float(p.final_price),
                "quantity": 1
            })
            total += p.final_price

    return result, total


def find_products_by_text(text):
    from .models import Product

    words = text.lower().split()
    products = Product.objects.filter(available=True)

    result = []

    for p in products:
        for w in words:
            if w in p.name.lower():
                result.append({
                    "slug": p.slug,
                    "name": p.name,
                    "price": float(p.price),
                    "quantity": 1
                })
                break

    return result[:5]


def get_gift_set():
    from .models import Product

    products = Product.objects.filter(available=True, stock__gt=0)[:4]

    return [{
        "slug": p.slug,
        "name": p.name,
        "price": float(p.price),
        "quantity": 1
    } for p in products]