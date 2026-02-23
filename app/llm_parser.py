import json
from openai import OpenAI
from .config import settings
from .schemas import ParsedMessage

client = OpenAI(api_key=settings.OPENAI_API_KEY)

JSON_SCHEMA = {
  "name": "bizbot_parse",
  "schema": {
    "type": "object",
    "additionalProperties": False,
    "properties": {
      "intent": {"type": "string", "enum": ["sale", "expense", "stock_in", "adjust", "report_request", "unknown"]},
      "occurred_at": {"type": ["string", "null"], "description": "ISO 8601 datetime in timezone if extracted, else null"},
      "item_name": {"type": ["string", "null"]},
      "qty": {"type": ["number", "null"]},
      "unit_price": {"type": ["number", "null"]},
      "amount": {"type": ["number", "null"]},
      "currency": {"type": "string", "enum": ["KZT"]},
      "note": {"type": ["string", "null"]},
      "extra": {"type": "object"},
      "need_clarification": {"type": "boolean"},
      "clarification_question": {"type": ["string", "null"]}
    },
    "required": ["intent","occurred_at","item_name","qty","unit_price","amount","currency","note","extra","need_clarification","clarification_question"]
  }
}

def parse_message(text: str, message_iso: str, tz: str) -> ParsedMessage:
    """
    message_iso — время сообщения (ISO) как подсказка, если человек пишет "сегодня/вчера".
    tz — таймзона бизнеса.
    """
    instructions = (
        "Ты ассистент-учетчик для малого бизнеса. "
        "Тебе дают сообщение менеджера в WhatsApp. "
        "Верни строго JSON по схеме. "
        f"Таймзона: {tz}. Валюта всегда KZT. "
        f"Время сообщения (если нужно для 'сегодня/вчера'): {message_iso}. "
        "Если это запрос отчета (например 'отчет сегодня', 'отчет 2026-02-21'), ставь intent='report_request'. "
        "Если это продажа — intent='sale'. Расход — 'expense'. Приход на склад — 'stock_in'. Корректировка — 'adjust'. "
        "Если для продажи нет количества или цены (или сумма неясна), попроси уточнение (need_clarification=true). "
        "Если менеджер указал время ('в 10:30', 'вчера', '21.02 в 18:00') — заполни occurred_at. "
        "Если времени в тексте нет — occurred_at = null."
    )

    resp = client.responses.create(
        model=settings.OPENAI_MODEL,
        instructions=instructions,
        input=text,
        text={
            "format": {
                "type": "json_schema",
                "json_schema": JSON_SCHEMA
            }
        },
    )

    data = json.loads(resp.output_text)
    return ParsedMessage(**data)