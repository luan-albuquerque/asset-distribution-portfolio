import requests
import json
from urllib.parse import unquote

COOKIES = {
    "laravel_session": "SEU_LARAVEL_SESSION",
    "XSRF-TOKEN": "SEU_XSRF_TOKEN",
}

WALLET_ID = ""

def get_ativos() -> list[dict]:
    """
    Retorna os ativos da carteira Investidor10
    """

    url = f"https://investidor10.com.br/wallet/api/proxy/wallet-app/summary/actives/{WALLET_ID}/Ticker?raw=1"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "pt-BR,pt;q=0.9",
        "referer": "https://investidor10.com.br/wallet/my-wallet/pro",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",

        "x-requested-with": "XMLHttpRequest",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
    }

    if "XSRF-TOKEN" not in COOKIES:
        raise ValueError("Cookie XSRF-TOKEN é obrigatório")

    headers["X-XSRF-TOKEN"] = unquote(COOKIES["XSRF-TOKEN"])

    session = requests.Session()
    session.headers.update(headers)
    session.cookies.update(COOKIES)

    response = session.get(url)

    # ===== tratamento de erro =====
    if response.status_code == 401:
        raise Exception("401 Unauthorized – sessão inválida")

    if response.status_code == 419:
        raise Exception("419 CSRF inválido")

    if response.status_code == 403:
        raise Exception("403 Forbidden – bloqueio")

    if "text/html" in response.headers.get("content-type", ""):
        raise Exception("Resposta HTML – bloqueio ou redirect")

    try:
        payload = response.json()
    except json.JSONDecodeError:
        raise Exception("Resposta não é JSON")

    ativos = []

    for item in payload.get("data", []):
        ativos.append({
            "ticker": item.get("ticker"),
            "ticker_name": item.get("ticker_name"),
            "current_price": item.get("current_price"),
            "equity_total": item.get("equity_total"),
        })

    return ativos


