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
            "User-Agent": "Mozilla/5.0 (compatible; SozdParser/1.0)",
            "Accept-Language": "ru-RU,ru;q=0.9",
        })

    def get_recent_bills(self, limit: int = 20) -> List[Bill]:
        html = self._get(SOZD_SEARCH, params={"sort_by": "RegisterDate", "direction": "desc"})
        bills = self._parse_search(html)
        return bills[:limit]

    def enrich_bill(self, bill: Bill) -> Bill:
        html = self._get(bill.url)
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(" ", strip=True)

        if not bill.summary:
            bill.summary = self._extract_summary(soup, text)
        if not bill.status:
            bill.status = self._find_near(text, ["Последнее событие", "Статус"])
        return bill

    def _extract_summary(self, soup: BeautifulSoup, text: str) -> str:
        selectors = [
            ".lawtext",
            ".bill-annotation",
            ".document-card__annotation",
            ".editor",
        ]
        for selector in selectors:
            node = soup.select_one(selector)
            if node:
                cleaned = node.get_text(" ", strip=True)
                if cleaned:
                    return cleaned[:2000]
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
        links = soup.select('a[href^="/bill/"]')
        seen = set()
        for a in links:
            href = a.get('href', '').strip()
            if not href or href in seen:
                continue
            seen.add(href)
            title = a.get_text(' ', strip=True)
            bill_id = href.strip('/').split('/')[-1]
            number = bill_id
            row_text = a.find_parent().get_text(' ', strip=True) if a.find_parent() else title
            bills.append(Bill(
                bill_id=bill_id,
                number=number,
                title=title,
                url=urljoin(SOZD_BASE, href),
                status=row_text[:180],
            ))
        return bills

    def _get(self, url: str, params: Optional[dict] = None) -> str:
        r = self.session.get(url, params=params, timeout=30)
        r.raise_for_status()
        time.sleep(self.delay)
        return r.text
