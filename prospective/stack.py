from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Intention:
    id: str
    intent: str
    status: str  # active | suspended | completed | abandoned
    depth: int
    parent_id: Optional[str]
    children: list[str]
    context: str
    created_at: str
    updated_at: str

    def touch(self):
        self.updated_at = datetime.now(timezone.utc).isoformat()

    @classmethod
    def new(cls, intent: str, context: str, parent_id: Optional[str] = None, depth: int = 0) -> Intention:
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            id=uuid.uuid4().hex[:12],
            intent=intent,
            status="active",
            depth=depth,
            parent_id=parent_id,
            children=[],
            context=context,
            created_at=now,
            updated_at=now,
        )


class IntentionStack:
    def __init__(self):
        self._intents: dict[str, Intention] = {}
        self._top_id: Optional[str] = None
        self._snapshots: dict[str, dict] = {}

    @property
    def top(self) -> Optional[Intention]:
        if self._top_id is None:
            return None
        return self._intents.get(self._top_id)

    def push(self, intent: str, context: str) -> Intention:
        parent_id = None
        depth = 0
        top = self.top
        if top is not None and top.status == "active":
            parent_id = top.id
            depth = top.depth + 1
        intention = Intention.new(intent, context, parent_id, depth)
        self._intents[intention.id] = intention
        if parent_id and parent_id in self._intents:
            self._intents[parent_id].children.append(intention.id)
        self._top_id = intention.id
        return intention

    def pop(self, intent_id: str) -> Optional[Intention]:
        intention = self._intents.get(intent_id)
        if intention is None:
            return None
        intention.status = "completed"
        intention.touch()
        if self._top_id == intent_id:
            self._top_id = intention.parent_id
        return intention

    def suspend(self, intent_id: str, reason: str) -> Optional[Intention]:
        intention = self._intents.get(intent_id)
        if intention is None:
            return None
        intention.status = "suspended"
        intention.context += f"\n[SUSPENDED: {reason}]"
        intention.touch()
        if self._top_id == intent_id:
            self._top_id = intention.parent_id
        return intention

    def list(self, status_filter: Optional[str] = None) -> list[Intention]:
        if status_filter:
            return [i for i in self._intents.values() if i.status == status_filter]
        return list(self._intents.values())

    def get(self, intent_id: str) -> Optional[Intention]:
        return self._intents.get(intent_id)

    def snapshot(self) -> str:
        snapshot_id = uuid.uuid4().hex[:12]
        self._snapshots[snapshot_id] = {
            "intents": {k: vars(v) for k, v in self._intents.items()},
            "top_id": self._top_id,
        }
        return snapshot_id

    def restore(self, snapshot_id: str) -> bool:
        data = self._snapshots.get(snapshot_id)
        if data is None:
            return False
        self._intents = {k: Intention(**v) for k, v in data["intents"].items()}
        self._top_id = data["top_id"]
        return True
