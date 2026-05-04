import re
import time
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .models import Bill

SOZD_BASE = "https://sozd.duma.gov.ru"
SOZD_SEARCH = f"{SOZD_BASE}/search"


class SozdParser:
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })

    def get_recent_bills(self, limit: int = 20) -> List[Bill]:
        html = self._get(SOZD_SEARCH, params={"sort_by": "RegisterDate", "direction": "desc"})
        bills = self._parse_search(html)
        return bills[:limit]

    def enrich_bill(self, bill: Bill) -> Bill:
        try:
            html = self._get(bill.url)
            soup = BeautifulSoup(html, "lxml")
            text = soup.get_text(" ", strip=True)

            # Пытаемся найти настоящее название закона на странице карточки
            title_selectors = [
                "h1.bill-title",
                ".bill-card__title",
                ".document-card__title",
                "h1",
            ]
            for sel in title_selectors:
                node = soup.select_one(sel)
                if node:
                    t = node.get_text(" ", strip=True)
                    if t and len(t) > 10 and t != bill.bill_id:
                        bill.title = t[:300]
                        break

            if not bill.summary:
                bill.summary = self._extract_summary(soup, text)
            if not bill.status or bill.status == bill.bill_id:
                bill.status = self._find_near(text, ["Последнее событие", "Статус", "Стадия"])
        except Exception as e:
            print(f"    [WARN] Не удалось обогатить {bill.bill_id}: {e}")
        return bill

    def _extract_summary(self, soup: BeautifulSoup, text: str) -> str:
        selectors = [
            ".lawtext",
            ".bill-annotation",
            ".document-card__annotation",
            ".editor",
            ".annotation",
            ".bill-description",
        ]
        for selector in selectors:
            node = soup.select_one(selector)
            if node:
                cleaned = node.get_text(" ", strip=True)
                if cleaned and len(cleaned) > 50:
                    return cleaned[:2000]

        # Ищем параграфы с содержательным текстом
        for p in soup.select("p"):
            t = p.get_text(" ", strip=True)
            if len(t) > 100:
                return t[:2000]

        return text[:2000]

    def _find_near(self, text: str, labels) -> str:
        for label in labels:
            m = re.search(rf'{re.escape(label)}[:\\s]+(.{{1,200}})', text)
            if m:
                return m.group(1).strip()
        return ''

    def _parse_search(self, html: str) -> List[Bill]:
        soup = BeautifulSoup(html, "lxml")
        bills = []
        seen = set()

        # Попытка 1: ищем строки таблицы или списка
        rows = soup.select("tr, .bill-item, .search-result-item, li.result-item")
        for row in rows:
            link = row.select_one('a[href^="/bill/"]')
            if not link:
                continue
            href = link.get("href", "").strip()
            if not href or href in seen:
                continue
            seen.add(href)

            bill_id = href.strip("/").split("/")[-1]
            row_text = row.get_text(" ", strip=True)

            title = link.get_text(" ", strip=True)
            if not title or title == bill_id or len(title) < 5:
                title = row_text[:200] if len(row_text) > 10 else f"Законопроект №{bill_id}"

            bills.append(Bill(
                bill_id=bill_id,
                number=bill_id,
                title=title,
                url=urljoin(SOZD_BASE, href),
                status=row_text[:180],
            ))

        # Попытка 2 (fallback): прямой поиск всех ссылок на законопроекты
        if not bills:
            for a in soup.select('a[href^="/bill/"]'):
                href = a.get("href", "").strip()
                if not href or href in seen:
                    continue
                seen.add(href)

                bill_id = href.strip("/").split("/")[-1]
                title = a.get_text(" ", strip=True)
                if not title or title == bill_id or len(title) < 5:
                    title = f"Законопроект №{bill_id}"

                parent = a.find_parent()
                parent_text = parent.get_text(" ", strip=True) if parent else title

                bills.append(Bill(
                    bill_id=bill_id,
                    number=bill_id,
                    title=title,
                    url=urljoin(SOZD_BASE, href),
                    status=parent_text[:180],
                ))

        return bills

    def _get(self, url: str, params: Optional[dict] = None) -> str:
        r = self.session.get(url, params=params, timeout=30)
        r.raise_for_status()
        time.sleep(self.delay)
        return r.text
