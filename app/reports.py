import datetime as dt
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from .models import Record

def format_money(x) -> str:
    if x is None:
        return "-"
    # простое форматирование
    return f"{float(x):,.0f}".replace(",", " ")

def daily_report(db: Session, business_id: int, day: dt.date) -> str:
    start = dt.datetime(day.year, day.month, day.day, 0, 0, 0)
    end = start + dt.timedelta(days=1)

    stmt = select(Record).where(
        and_(
            Record.business_id == business_id,
            Record.occurred_at >= start,
            Record.occurred_at < end
        )
    ).order_by(Record.occurred_at.asc())

    rows = db.execute(stmt).scalars().all()

    if not rows:
        return f"Отчет за {day.isoformat()}\n\nЗаписей нет."

    lines = [f"Отчет за {day.isoformat()}\n"]
    total_sales = 0.0
    total_expenses = 0.0

    for r in rows:
        t = r.occurred_at.strftime("%H:%M")
        if r.type == "sale":
            amount = float(r.amount) if r.amount is not None else 0.0
            total_sales += amount
            lines.append(f"{t} — SALE — {r.item_name or '-'} — {r.qty or '-'} — {format_money(r.unit_price)} — {format_money(r.amount)}")
        elif r.type == "expense":
            amount = float(r.amount) if r.amount is not None else 0.0
            total_expenses += amount
            lines.append(f"{t} — EXPENSE — {r.note or r.item_name or '-'} — {format_money(r.amount)}")
        else:
            lines.append(f"{t} — {r.type.upper()} — {r.item_name or '-'} — {r.qty or '-'} — {format_money(r.amount)}")

    lines.append("\nИтоги:")
    lines.append(f"Продажи: {format_money(total_sales)} KZT")
    lines.append(f"Расходы: {format_money(total_expenses)} KZT")
    lines.append(f"Чистыми (упрощенно): {format_money(total_sales - total_expenses)} KZT")

    return "\n".join(lines)