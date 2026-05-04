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
    from sozd_parser import SozdParser
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


def main():
    print("="*40)
    print(" 🏛  Дума на цифровой кухне (Парсер СОЗД)")
    print("="*40)

    if not PARSER_AVAILABLE or not HTML_AVAILABLE:
        print("\n[FATAL] Программа собрана некорректно — отсутствуют ключевые модули.")
        print("Пожалуйста, сообщите об ошибке разработчику.")
        print("="*40)
        input("Нажмите Enter, чтобы закрыть это окно...")
        return

    try:
        print("\n[1/3] Собираю свежие законопроекты с сайта Госдумы...")
        parser = SozdParser()
        laws = parser.get_latest_laws(limit=20)

        if not laws:
            print("Новых законопроектов не найдено. Попробуйте позже.")
            return

        print(f"Успешно загружено законопроектов: {len(laws)}")

        print("[2/3] Готовлю кухонный интерфейс (HTML)...")
        html_path = os.path.join(application_path, 'index.html')
        save_almighty_html(html_path, laws)

        print("[3/3] Проверка Telegram...")
        if TELEGRAM_AVAILABLE:
            token = os.environ.get('TELEGRAM_BOT_TOKEN')
            chat_id = os.environ.get('TELEGRAM_CHAT_ID')
            if token and chat_id:
                try:
                    bot = SozdTelegramBot(token, chat_id)
                    bot.send_digest(laws[:5])
                    print("Telegram: дайджест успешно отправлен!")
                except Exception as e:
                    print(f"Telegram: ошибка отправки: {e}")
            else:
                print("Telegram: токены не найдены в .env (пропускаем).")
        else:
            print("Telegram: модуль деактивирован, пропускаем.")

        print("\nУСПЕШНО! Файл index.html создан рядом с программой.")

        file_url = 'file://' + os.path.realpath(html_path)
        print("Открываю законы в вашем браузере...")
        webbrowser.open(file_url)

    except Exception as e:
        print(f"\nКРИТИЧЕСКАЯ ОШИБКА: {e}")
        traceback.print_exc()
    finally:
        print("\n" + "="*40)
        input("Нажмите Enter, чтобы закрыть это окно...")

if __name__ == '__main__':
    main()
