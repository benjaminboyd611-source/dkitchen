import json
from pathlib import Path
from typing import List
from datetime import datetime
from .models import Bill

HTML_TEMPLATE = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>🏛️ Дума на цифровой кухне</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 16px; background: #f6f8fa; color: #24292e; }
    .bill { background: #fff; border: 1px solid #e1e4e8; border-radius: 8px; padding: 24px; margin: 20px 0; box-shadow: 0 1px 3px rgba(27,31,35,0.04); }
    .muted { color: #586069; font-size: 0.9em; margin-bottom: 12px; }
    .btn { background: #0366d6; color: #fff; border: 1px solid rgba(27,31,35,0.2); padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500; margin-top: 12px; transition: 0.2s; }
    .btn:hover { background: #005cc5; }
    .btn-success { background: #2ea44f; }
    .btn-success:hover { background: #2c974b; }
    .prompt-box { display: none; background: #f6f8fa; padding: 16px; border-radius: 6px; margin-top: 12px; white-space: pre-wrap; border: 1px solid #e1e4e8; font-size: 13px; font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace; line-height: 1.45; }
    a { color: #0366d6; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .header { text-align: center; margin-bottom: 40px; }
    .footer { text-align: center; color: #8b949e; font-size: 12px; margin-top: 50px; border-top: 1px solid #e1e4e8; padding-top: 20px; }
  </style>
</head>
<body>
  <div class="header">
      <h1>🏛️ Дума на цифровой кухне</h1>
      <p class="muted" style="font-size: 16px;">Свежие законопроекты. Нажми <b>Assist Mode</b>, скопируй текст и вставь в любой ИИ-чат (Алису, GigaChat, ChatGPT), чтобы получить понятный разбор.</p>
  </div>

  <div id="app"></div>

  <div class="footer">
      Обновлено: __DATE__
  </div>

  <script>
    const bills = __BILLS_JSON__;

    const app = document.getElementById('app');
    app.innerHTML = bills.map((b, i) => `
      <div class="bill">
        <h2 style="margin-top:0; font-size: 20px;">${b.title || 'Без названия'}</h2>
        <div class="muted">Номер: ${b.number || '-'} | Статус: ${b.status || '-'} | <a href="${b.url}" target="_blank">📄 Карточка в СОЗД</a></div>
        <p style="line-height: 1.6;">${(b.summary || '').substring(0, 400)}...</p>
        <button class="btn" onclick="togglePrompt(${i})">✨ Assist Mode: получить промпт</button>
        <button class="btn btn-success" onclick="copyPrompt(${i})" style="display:none" id="copy-${i}">📋 Скопировать</button>
        <div class="prompt-box" id="prompt-${i}">${b.assist_prompt}</div>
      </div>
    `).join('');

    function togglePrompt(idx) {
      const el = document.getElementById('prompt-' + idx);
      const copyBtn = document.getElementById('copy-' + idx);
      if(el.style.display === 'block') {
        el.style.display = 'none';
        copyBtn.style.display = 'none';
      } else {
        el.style.display = 'block';
        copyBtn.style.display = 'inline-block';
      }
    }

    function copyPrompt(idx) {
      const el = document.getElementById('prompt-' + idx);
      navigator.clipboard.writeText(el.innerText).then(() => {
        const btn = document.getElementById('copy-' + idx);
        btn.innerText = '✅ Скопировано!';
        setTimeout(() => btn.innerText = '📋 Скопировать', 2000);
      });
    }
  </script>
</body>
</html>"""

def save_almighty_html(path: str, bills: List[Bill]):
    bills_dicts = [b.to_dict() for b in bills]
    bills_json = json.dumps(bills_dicts, ensure_ascii=False)

    # Экранируем символы для безопасной вставки в JS
    bills_json = bills_json.replace('\\', '\\\\').replace('<', '\\u003c')

    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")

    html = HTML_TEMPLATE.replace('__BILLS_JSON__', bills_json).replace('__DATE__', now_str)

    Path(path).write_text(html, encoding='utf-8')
