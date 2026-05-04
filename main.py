import os
import sys
import traceback
from dotenv import load_dotenv

# Правильно загружаем .env даже если программа скомпилирована в .exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

env_path = os.path.join(application_path, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Загружены настройки из: {env_path}")

from sozd_parser import SozdParser
from sozd_parser.export import save_almighty_html
#from sozd_parser.telegram_bot import send_digest, is_enabled

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
    try:
        print("Начинаем парсинг СОЗД Думы...")
        parser = SozdParser(delay=2.0)
        bills = parser.get_recent_bills(limit=10)
        enriched = []

        for i, bill in enumerate(bills):
            print(f"Обработка {i+1}/{len(bills)}: {bill.number}...")
            try:
                b = parser.enrich_bill(bill)
                b.assist_prompt = generate_prompt(b).replace('\n', '\\n')
                enriched.append(b)
            except Exception as e:
                print(f" Ошибка при обработке {bill.number}: {e}")
                bill.assist_prompt = generate_prompt(bill).replace('\n', '\\n')
                enriched.append(bill)

        out_html = os.path.join(application_path, 'index.html')
        print(f"Генерируем файл {out_html}...")
        save_almighty_html(out_html, enriched)

#        if is_enabled():
#           print("Отправляем дайджест в Telegram...")
#            try:
#                send_digest(enriched)
#                print("Telegram: успешно отправлено!")
#            except Exception as e:
#                print(f"Telegram: ошибка отправки: {e}")
#        else:
#            print("Telegram-бот не настроен (пропускаем).")

        print("\nУСПЕШНО! Файл index.html создан рядом с программой.")

    except Exception as e:
        print(f"\nКРИТИЧЕСКАЯ ОШИБКА: {e}")
        traceback.print_exc()
    finally:
        print("\n" + "="*40)
        input("Нажмите Enter, чтобы закрыть это окно...")

if __name__ == '__main__':
    main()
