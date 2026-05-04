from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class Bill:
    bill_id: str
    number: str
    title: str
    url: str
    status: str = ''
    committee: str = ''
    introduced_by: str = ''
    date_introduced: str = ''
    summary: Optional[str] = None
    assist_prompt: str = ''

    def to_dict(self):
        return asdict(self)
