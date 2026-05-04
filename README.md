# Дума на цифровой кухне — парсер СОЗД Думы

Максимально простой open-source парсер открытых страниц СОЗД Государственной Думы с GitHub Actions, GitHub Pages и опциональной отправкой дайджеста в Telegram.

## Что умеет
- получает список свежих законопроектов из СОЗД;
- заходит в карточки законопроектов;
- сохраняет JSON и Markdown;
- публикует статический сайт через GitHub Pages;
- по желанию отправляет свежий дайджест в Telegram-чат или канал.

## Быстрый старт локально

```bash
pip install -r requirements.txt
python main.py
```

После запуска появятся файлы:
- `data/bills.json`
- `data/latest.md`
- `data/meta.json`

## Telegram

Чтобы бот отправлял короткий дайджест в Telegram, добавь переменные окружения:

```bash
TELEGRAM_BOT_TOKEN=токен_бота
TELEGRAM_CHAT_ID=id_чата_или_канала
```

### Как получить
1. Создай бота через [@BotFather](https://t.me/BotFather).
2. Получи токен.
3. Добавь бота в свой чат или канал.
4. Узнай `chat_id` и добавь его в secrets.

## Запуск на GitHub

1. Создай новый репозиторий.
2. Загрузи все файлы.
3. В **Settings → Pages** выбери **GitHub Actions**.
4. Открой вкладку **Actions**.
5. Нажми **Run workflow**.

### Secrets для Telegram
Если нужен Telegram-дайджест, добавь в **Settings → Secrets and variables → Actions**:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Если не добавить эти secrets, проект все равно работает: просто без Telegram.

## Что делает workflow
- запускает парсер;
- обновляет `data/bills.json`;
- обновляет `data/latest.md`;
- при наличии secrets отправляет Telegram-дайджест;
- публикует `public/` в GitHub Pages.
