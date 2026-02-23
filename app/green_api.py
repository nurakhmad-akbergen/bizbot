import requests
from .config import settings

def send_message(chat_id: str, text: str) -> None:
    url = f"https://api.green-api.com/waInstance{settings.GREEN_API_ID_INSTANCE}/sendMessage/{settings.GREEN_API_TOKEN}"
    payload = {"chatId": chat_id, "message": text}
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception:
        # в MVP просто глотаем ошибку; позже можно логировать
        pass