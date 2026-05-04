import os
import sys
import traceback
import webbrowser
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

env_path = os.path.join(application_path, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Загружены настройки из: {env_path}")

# === БЕЗОПАСНЫЙ ИМПОРТ ВСЕХ МОДУЛЕЙ ===

try:
    from sozd_parser.parser import SozdParser
    PARSER_AVAILABLE = True
except ImportError as e:
    PARSER_AVAILABLE = False
    print(f"[FATAL] Не найден модуль парсера: {e}")

try:
    from sozd_parser.export import save_almighty_html
    HTML_AVAILABLE = True
except ImportError as e:
    HTML_AVAILABLE = False
    print(f"[FATAL] Не найден модуль экспорта: {e}")

try:
    from sozd_parser.telegram_bot import SozdTelegramBot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("[INFO] Telegram-модуль отключен (Сборка для домохозяек).")


def make_assist_prompt(bill) -> str:
    return (
        f"Проанализируй законопроект Госдумы РФ:\n\n"
        f"Название: {bill.title}\n"
        f"Номер: {bill.number}\n"
        f"Статус: {bill.status}\n"
        f"Текст/аннотация: {bill.summary or 'не указана'}\n\n"
        f"Задача:\n"
        f"1. Объясни суть закона простым языком (2-3 предложения).\n"
        f"2. Найди PRO — кому этот закон выгоден и почему.\n"
        f"3. Найди CONTRA — кому он вреден, какие подводные камни.\n"
        f"4. Оцени применимость в реальной жизни: что изменится для обычного человека?\n"
        f"5. Кто является скрытым выгодоприобретателем?"
    )


def main():
    print("=" * 40)
    print(" 🏛  Дума на цифровой кухне (Парсер СОЗД)")
    print("=" * 40)

    if not PARSER_AVAILABLE or not HTML_AVAILABLE:
        print("\n[FATAL] Программа собрана некорректно — отсутствуют ключевые модули.")
        print("Пожалуйста, сообщите об ошибке разработчику.")
        print("=" * 40)
        input("Нажмите Enter, чтобы закрыть это окно...")
        return

    try:
        print("\n[1/3] Собираю свежие законопроекты с сайта Госдумы...")
        try:
            parser = SozdParser(delay=1.5)
            bills = parser.get_recent_bills(limit=20)
        except Exception as e:
            print("\n[ОШИБКА СЕТИ] Не удалось подключиться к сайту Госдумы.")
            print("Возможные причины:")
            print("  • Сайт sozd.duma.gov.ru недоступен из вашей страны или сети")
            print("  • Проверьте подключение к интернету")
            print("  • Попробуйте запустить программу позже")
            print(f"\nТехническая деталь: {e}")
            input("\nНажмите Enter, чтобы закрыть это окно...")
            return

        if not bills:
            print("Новых законопроектов не найдено. Попробуйте позже.")
            input("Нажмите Enter, чтобы закрыть это окно...")
            return

        print(f"Найдено законопроектов: {len(bills)}")

        print("[2/3] Загружаю подробности по каждому законопроекту...")
        enriched = []
        for i, bill in enumerate(bills, 1):
            print(f"  [{i}/{len(bills)}] {bill.title[:60]}...")
            bill = parser.enrich_bill(bill)
            if not bill.assist_prompt:
                bill.assist_prompt = make_assist_prompt(bill)
            enriched.append(bill)

        print("[3/3] Готовлю кухонный интерфейс (HTML)...")
        html_path = os.path.join(application_path, 'index.html')
        save_almighty_html(html_path, enriched)

        if TELEGRAM_AVAILABLE:
            token = os.environ.get('TELEGRAM_BOT_TOKEN')
            chat_id = os.environ.get('TELEGRAM_CHAT_ID')
            if token and chat_id:
                try:
                    bot = SozdTelegramBot(token, chat_id)
                    bot.send_digest(enriched[:5])
                    print("Telegram: дайджест успешно отправлен!")
                except Exception as e:
                    print(f"Telegram: ошибка отправки: {e}")
            else:
                print("Telegram: токены не найдены в .env (пропускаем).")

        print("\nУСПЕШНО! Открываю законы в вашем браузере...")
        webbrowser.open('file://' + os.path.realpath(html_path))

    except Exception as e:
        print(f"\nКРИТИЧЕСКАЯ ОШИБКА: {e}")
        traceback.print_exc()
    finally:
        print("\n" + "=" * 40)
        input("Нажмите Enter, чтобы закрыть это окно...")


if __name__ == '__main__':
    main()
