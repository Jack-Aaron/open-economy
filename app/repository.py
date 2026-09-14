import json
from functools import lru_cache
from pathlib import Path

from .models import GraphPayload

ROOT = Path(__file__).resolve().parents[1]
DATA_PATHS = {
    "reported": ROOT / "data" / "reported.json",
    "prototype": ROOT / "data" / "prototype.json",
}


@lru_cache(maxsize=2)
def load_graph(mode: str = "reported") -> GraphPayload:
    if mode not in DATA_PATHS:
        raise ValueError(f"Unknown graph mode: {mode}")
    raw = json.loads(DATA_PATHS[mode].read_text(encoding="utf-8"))
    return GraphPayload.model_validate(raw)


def entity_detail(entity_id: str, mode: str = "reported") -> dict | None:
    graph = load_graph(mode)
    entities = {entity.id: entity for entity in graph.entities}
    entity = entities.get(entity_id)
    if not entity:
        return None

    children = [item for item in graph.entities if item.parent_id == entity_id]
    incoming = [flow for flow in graph.flows if flow.target == entity_id]
    outgoing = [flow for flow in graph.flows if flow.source == entity_id]
    source_map = {source.id: source for source in graph.sources}
    relevant_source_ids = {sid for flow in incoming + outgoing for sid in flow.source_ids}

    return {
        "entity": entity,
        "children": children,
        "incoming": incoming,
        "outgoing": outgoing,
        "sources": [source_map[sid] for sid in sorted(relevant_source_ids) if sid in source_map],
    }
