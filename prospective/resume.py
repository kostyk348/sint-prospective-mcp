from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
from .stack import IntentionStack
from .markers import MarkerStore


class ResumeEngine:
    def __init__(self, stack: IntentionStack, markers: MarkerStore):
        self._stack = stack
        self._markers = markers

    def resume(self) -> dict:
        top = self._stack.top
        if top is None:
            return {"has_pending": False, "message": "No pending intentions."}

        created = datetime.fromisoformat(top.created_at)
        now = datetime.now(timezone.utc)
        delta = now - created
        seconds_since_active = int(delta.total_seconds())

        active_intents = self._stack.list("active")
        history_summary = [
            {"id": i.id, "intent": i.intent, "depth": i.depth, "status": i.status}
            for i in sorted(active_intents, key=lambda x: x.depth)
        ]

        markers = [
            {"id": m.id, "position": m.position, "note": m.note, "created_at": m.created_at}
            for m in self._markers.list()
        ]

        return {
            "has_pending": True,
            "top_active_intent": {
                "id": top.id,
                "intent": top.intent,
                "context": top.context,
                "depth": top.depth,
                "created_at": top.created_at,
                "updated_at": top.updated_at,
            },
            "history_summary": history_summary,
            "context_markers": markers,
            "time_since_active_seconds": seconds_since_active,
            "message": f"You were working on: {top.intent}. Continue?",
        }
