from datetime import datetime, timezone
from sozd_parser import SozdParser
from sozd_parser.export import save_json, save_markdown
from sozd_parser.storage import write_latest_snapshot
from sozd_parser.telegram_bot import send_digest, is_enabled


def generate_prompt(bill):
    return f"""Ты — независимый аналитик законодательства России.
Задача: кратко и понятно объяснить законопроект обычному человеку.

Нужно дать:
1) Короткое резюме.
2) 3 аргумента ЗА.
3) 3 аргумента ПРОТИВ.
4) Кому это выгодно/невыгодно.
5) На что обратить внимание гражданину.
6) Вывод без политической агитации.

Данные законопроекта:
Название: {bill.title}
Номер: {bill.number}
Статус: {bill.status}
Краткое описание: {bill.summary or 'Нет описания'}
"""


def main():
    parser = SozdParser(delay=2.0)
    bills = parser.get_recent_bills(limit=15)
    enriched = []
    for bill in bills[:10]:
        try:
            b = parser.enrich_bill(bill)
            b.assist_prompt = generate_prompt(b)
            enriched.append(b)
        except Exception:
            bill.assist_prompt = generate_prompt(bill)
            enriched.append(bill)

    save_json('data/bills.json', enriched)
    save_markdown('data/latest.md', enriched)
    write_latest_snapshot('data/meta.json', {
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'count': len(enriched),
        'telegram_enabled': is_enabled(),
    })

    try:
        send_digest(enriched)
    except Exception:
        pass

    print(f'Saved {len(enriched)} bills')


if __name__ == '__main__':
    main()
