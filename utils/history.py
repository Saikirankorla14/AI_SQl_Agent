"""
utils/history.py
In-memory query history with optional JSON persistence.
Stores every (question, sql, row_count) triple for the session.
"""

import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime


@dataclass
class HistoryEntry:
    question: str
    sql: str
    row_count: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    error: str | None = None


class QueryHistory:
    def __init__(self, persist_path: str | None = None):
        self._entries: list[HistoryEntry] = []
        self._path = persist_path
        if persist_path and os.path.exists(persist_path):
            self._load()

    def add(self, question: str, sql: str, row_count: int, error: str | None = None):
        entry = HistoryEntry(question=question, sql=sql,
                             row_count=row_count, error=error)
        self._entries.append(entry)
        if self._path:
            self._save()

    def all(self) -> list[HistoryEntry]:
        return list(self._entries)

    def last(self, n: int = 5) -> list[HistoryEntry]:
        return self._entries[-n:]

    def clear(self):
        self._entries.clear()
        if self._path and os.path.exists(self._path):
            os.remove(self._path)

    def _save(self):
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        with open(self._path, "w") as f:
            json.dump([asdict(e) for e in self._entries], f, indent=2)

    def _load(self):
        with open(self._path) as f:
            data = json.load(f)
        self._entries = [HistoryEntry(**d) for d in data]
