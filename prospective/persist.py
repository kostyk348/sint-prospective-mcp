from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
from .stack import IntentionStack, Intention
from .markers import MarkerStore, ContextMarker


PERSIST_DIR = Path.home() / ".config" / "opencode" / "prospective"


class Persistence:
    def __init__(self, stack: IntentionStack, markers: MarkerStore):
        self._stack = stack
        self._markers = markers

    def save(self, name: str = "default") -> str:
        PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "intents": {k: vars(v) for k, v in self._stack._intents.items()},
            "top_id": self._stack._top_id,
            "markers": [vars(m) for m in self._markers._markers],
            "snapshots": {
                k: v for k, v in self._stack._snapshots.items()
            },
        }
        path = PERSIST_DIR / f"{name}.json"
        path.write_text(json.dumps(data, indent=2))
        return str(path)

    def load(self, name: str = "default") -> bool:
        path = PERSIST_DIR / f"{name}.json"
        if not path.exists():
            return False
        data = json.loads(path.read_text())
        self._stack._intents = {
            k: Intention(**v) for k, v in data.get("intents", {}).items()
        }
        self._stack._top_id = data.get("top_id")
        self._stack._snapshots = data.get("snapshots", {})
        self._markers._markers = [
            ContextMarker(**m) for m in data.get("markers", [])
        ]
        return True
