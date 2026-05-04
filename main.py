import os
import sys
import traceback
import webbrowser
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

# === БЕЗОПАСНЫЙ ИМПОРТ ВСЕХ МОДУЛЕЙ ===

try:
    from sozd_parser import SozdParser
    PARSER_AVAILABLE = True
except ImportError as e:
    PARSER_AVAILABLE = False
    print(f"[FATAL] Не найден модуль парсера: {e}")

try:
    from sozd_parser.html_generator import HtmlGenerator
    HTML_AVAILABLE = True
except ImportError as e:
    HTML_AVAILABLE = False
    print(f"[FATAL] Не найден модуль HTML-генератора: {e}")

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

    # Критическая проверка — без этих модулей работа невозможна
    if not PARSER_AVAILABLE or not HTML_AVAILABLE:
        print("\n[FATAL] Программа собрана некорректно — отсутствуют ключевые модули.")
        print("Пожалуйста, сообщите об ошибке разработчику.")
        print("="*40)
        input("Нажмите Enter, чтобы закрыть это окно...")
        return

    try:
        # 1. Парсинг данных
        print("\n[1/3] Собираю свежие законопроекты с сайта Госдумы...")
        parser = SozdParser()
        laws = parser.get_latest_laws(limit=20)

        if not laws:
            print("Новых законопроектов не найдено. Попробуйте позже.")
            return

        print(f"Успешно загружено законопроектов: {len(laws)}")

        # 2. Генерация HTML
        print("[2/3] Готовлю кухонный интерфейс (HTML)...")
        html_gen = HtmlGenerator()
        html_gen.generate(laws, os.path.join(application_path, 'index.html'))

        # 3. Отправка в Telegram (если доступно и настроено)
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

        # 4. Автоматическое открытие браузера
        html_path = 'file://' + os.path.realpath(
            os.path.join(application_path, 'index.html')
        )
        print("Открываю законы в вашем браузере...")
        webbrowser.open(html_path)

    except Exception as e:
        print(f"\nКРИТИЧЕСКАЯ ОШИБКА: {e}")
        traceback.print_exc()
    finally:
        print("\n" + "="*40)
        input("Нажмите Enter, чтобы закрыть это окно...")

if __name__ == '__main__':
    main()
