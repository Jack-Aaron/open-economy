import json
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .models import EvidenceStatus, Layer
from .repository import entity_detail, load_graph

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
COVERAGE_PATH = ROOT / "data" / "source_coverage.json"
GraphMode = Literal["reported", "prototype"]

app = FastAPI(
    title="OpenEconomy",
    version="0.2.0",
    description="An explorable empirical model of economic and political money flows.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/graph")
def graph(
    mode: GraphMode = "reported",
    layer: list[Layer] | None = Query(default=None),
    status: list[EvidenceStatus] | None = Query(default=None),
) -> dict:
    payload = load_graph(mode)
    flows = payload.flows
    if layer:
        wanted = set(layer)
        flows = [flow for flow in flows if flow.layer in wanted]
    if status:
        wanted_status = set(status)
        flows = [flow for flow in flows if flow.status in wanted_status]

    connected = {flow.source for flow in flows} | {flow.target for flow in flows}
    entities = [
        entity
        for entity in payload.entities
        if entity.id in connected or (not layer and not status)
    ]
    return {
        "entities": entities,
        "flows": flows,
        "sources": payload.sources,
        "metadata": payload.metadata,
    }


@app.get("/api/entities/{entity_id}")
def entity(entity_id: str, mode: GraphMode = "reported") -> dict:
    detail = entity_detail(entity_id, mode)
    if detail is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return detail


@app.get("/api/sources")
def sources(mode: GraphMode = "reported") -> list:
    return load_graph(mode).sources


@app.get("/api/data-coverage")
def data_coverage() -> dict:
    return json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))


if STATIC.exists():
    app.mount("/assets", StaticFiles(directory=STATIC), name="assets")


@app.get("/")
def index():
    index_path = STATIC / "index.html"
    if not index_path.exists():
        return {"name": "OpenEconomy", "status": "API ready"}
    return FileResponse(index_path)
