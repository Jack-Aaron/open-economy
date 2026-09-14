from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "source_catalog.json"


@dataclass(frozen=True)
class DatasetSpec:
    id: str
    source_id: str
    name: str
    transport: str
    url: str
    auth_env: str | None = None
    bulk: bool = False
    note: str = ""


def load_catalog(path: Path = CATALOG_PATH) -> list[DatasetSpec]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [DatasetSpec(**item) for item in payload["datasets"]]
