from typing import Any, Dict, Optional

def extract_text(payload: Dict[str, Any]) -> Optional[str]:
    md = payload.get("messageData") or {}
    # текст
    t = (((md.get("textMessageData") or {}).get("textMessage")) if isinstance(md, dict) else None)
    if t:
        return t.strip()

    # иногда может быть extendedTextMessageData
    t2 = (((md.get("extendedTextMessageData") or {}).get("text")) if isinstance(md, dict) else None)
    if t2:
        return t2.strip()

    return None

def extract_chat_id(payload: Dict[str, Any]) -> Optional[str]:
    sd = payload.get("senderData") or {}
    cid = sd.get("chatId")
    if cid:
        return str(cid)
    return None

def extract_timestamp(payload: Dict[str, Any]) -> Optional[int]:
    ts = payload.get("timestamp")
    if ts is None:
        return None
    try:
        return int(ts)
    except Exception:
        return None