import json
from pathlib import Path
from typing import List
from .models import Bill

def save_json(path: str, bills: List[Bill]):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump([b.to_dict() for b in bills], f, ensure_ascii=False, indent=2)

def save_markdown(path: str, bills: List[Bill]):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    lines = ['# Свежие законопроекты СОЗД', '']
    for b in bills:
        lines.append(f'## {b.title}')
        lines.append(f'- Номер: {b.number}')
        lines.append(f'- URL: {b.url}')
        if b.status:
            lines.append(f'- Статус: {b.status}')
        if b.summary:
            lines.append(f'- Кратко: {b.summary[:500]}')
        lines.append('')
    
    # 100% надежный способ записи файла
    with open(path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')
