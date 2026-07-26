from __future__ import annotations
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class ContextMarker:
    id: str
    position: int
    note: str
    created_at: str

    @classmethod
    def new(cls, position: int, note: str) -> ContextMarker:
        return cls(
            id=uuid.uuid4().hex[:12],
            position=position,
            note=note,
            created_at=datetime.now(timezone.utc).isoformat(),
        )


class MarkerStore:
    def __init__(self):
        self._markers: list[ContextMarker] = []

    def add(self, position: int, note: str) -> ContextMarker:
        marker = ContextMarker.new(position, note)
        self._markers.append(marker)
        return marker

    def list(self) -> list[ContextMarker]:
        return sorted(self._markers, key=lambda m: m.position)

    def clear(self):
        self._markers.clear()
