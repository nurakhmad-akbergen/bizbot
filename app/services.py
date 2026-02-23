import datetime as dt
from dateutil import parser as dtparser
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import Business, User, Record
from .schemas import ParsedMessage

def get_or_create_business_and_user(db: Session, chat_id: str) -> User:
    # Если юзера нет — создадим бизнес "Default" и юзера-manager
    user = db.execute(select(User).where(User.chat_id == chat_id)).scalar_one_or_none()
    if user:
        return user

    biz = Business(name="Default Business")
    db.add(biz)
    db.flush()

    user = User(business_id=biz.id, chat_id=chat_id, role="manager")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def resolve_occurred_at(parsed: ParsedMessage, message_dt: dt.datetime) -> dt.datetime:
    # 1) если ИИ достал occurred_at — используем
    if parsed.occurred_at:
        try:
            return dtparser.isoparse(parsed.occurred_at)
        except Exception:
            pass
    # 2) иначе — время сообщения (WhatsApp timestamp)
    return message_dt

def compute_amount(parsed: ParsedMessage) -> float | None:
    # Если amount есть — ок
    if parsed.amount is not None:
        return float(parsed.amount)
    # Иначе если qty * unit_price
    if parsed.qty is not None and parsed.unit_price is not None:
        return float(parsed.qty) * float(parsed.unit_price)
    return None

def save_record(db: Session, user: User, parsed: ParsedMessage, raw_text: str, message_dt: dt.datetime) -> Record:
    occurred_at = resolve_occurred_at(parsed, message_dt)
    amount = compute_amount(parsed)

    rec = Record(
        business_id=user.business_id,
        user_id=user.id,
        type=parsed.intent,                 # sale/expense/stock_in/adjust
        occurred_at=occurred_at,
        item_name=parsed.item_name,
        qty=parsed.qty,
        unit_price=parsed.unit_price,
        amount=amount if amount is not None else parsed.amount,
        currency="KZT",
        note=parsed.note,
        raw_text=raw_text,
        extra=parsed.extra or {},
    )

    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec