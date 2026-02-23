import datetime as dt
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from .db import Base, engine, SessionLocal
from .config import settings
from .webhook_extract import extract_text, extract_chat_id, extract_timestamp
from .green_api import send_message
from .llm_parser import parse_message
from .services import get_or_create_business_and_user, save_record
from .reports import daily_report

app = FastAPI(title="BizBot (Green API)")

@app.on_event("startup")
def on_startup():
    # MVP: создаем таблицы автоматически
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

def process_message(payload: dict):
    text = extract_text(payload)
    chat_id = extract_chat_id(payload)
    ts = extract_timestamp(payload)

    if not text or not chat_id or ts is None:
        return

    message_dt = dt.datetime.fromtimestamp(ts)
    message_iso = message_dt.isoformat()

    db: Session = SessionLocal()
    try:
        user = get_or_create_business_and_user(db, chat_id)

        parsed = parse_message(text=text, message_iso=message_iso, tz=settings.TIMEZONE)

        # Если ИИ не уверен — задаём уточняющий вопрос
        if parsed.need_clarification:
            q = parsed.clarification_question or "Уточни, пожалуйста: количество и цену?"
            send_message(chat_id, q)
            return

        # Отчёты
        if parsed.intent == "report_request":
            # MVP: поддержим "отчет сегодня" (и любые "отчет" → сегодня)
            report_text = daily_report(db, user.business_id, message_dt.date())
            send_message(chat_id, report_text)
            return

        # Сохранение записи
        rec = save_record(db, user, parsed, raw_text=text, message_dt=message_dt)

        # Ответ менеджеру
        if rec.type == "sale":
            send_message(chat_id, f"✅ Записал продажу: {rec.item_name or '-'} / {rec.qty or '-'} / {rec.amount or '-'} KZT")
        elif rec.type == "expense":
            send_message(chat_id, f"✅ Записал расход: {rec.amount or '-'} KZT ({rec.note or rec.item_name or ''})")
        else:
            send_message(chat_id, f"✅ Записал: {rec.type}")

    finally:
        db.close()

@app.post("/webhook")
async def webhook(request: Request, bg: BackgroundTasks):
    # (Опционально) секрет вебхука — чтобы никто не спамил твой endpoint
    if settings.WEBHOOK_SECRET:
        provided = request.headers.get("X-Webhook-Secret", "")
        if provided != settings.WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Invalid webhook secret")

    payload = await request.json()

    # Быстро отвечаем 200 OK, а обработку делаем в фоне
    bg.add_task(process_message, payload)
    return {"status": "ok"}