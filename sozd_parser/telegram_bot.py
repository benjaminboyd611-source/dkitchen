import os
import asyncio
from telegram import Bot


def is_enabled() -> bool:
    return bool(os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'))


def build_digest(bills):
    lines = ['🏛️ Дума на цифровой кухне', 'Свежие законопроекты СОЗД:', '']
    for i, b in enumerate(bills[:5], 1):
        title = (b.title or 'Без названия').strip()
        summary = (b.summary or '').strip().replace('
', ' ')
        if len(summary) > 220:
            summary = summary[:217] + '...'
        lines.append(f'{i}. {title}')
        if b.status:
            lines.append(f'Статус: {b.status[:120]}')
        if summary:
            lines.append(summary)
        if b.url:
            lines.append(b.url)
        lines.append('')
    return '
'.join(lines).strip()


async def _send(text: str):
    bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
    await bot.send_message(chat_id=os.environ['TELEGRAM_CHAT_ID'], text=text, disable_web_page_preview=True)


def send_digest(bills):
    if not is_enabled() or not bills:
        return False
    text = build_digest(bills)
    asyncio.run(_send(text))
    return True
