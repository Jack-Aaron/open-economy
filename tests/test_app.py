from fastapi.testclient import TestClient

from app.main import app
from app.repository import load_graph

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_graph_loads():
    response = client.get("/api/graph")
    assert response.status_code == 200
    body = response.json()
    assert len(body["entities"]) >= 8
    assert any(flow["id"] == "payroll" for flow in body["flows"])
    assert any(flow["layer"] == "political" for flow in body["flows"])


def test_layer_filter():
    response = client.get("/api/graph?layer=political")
    assert response.status_code == 200
    body = response.json()
    assert body["flows"]
    assert {flow["layer"] for flow in body["flows"]} == {"political"}


def test_households_detail_contains_payroll():
    response = client.get("/api/entities/households")
    assert response.status_code == 200
    body = response.json()
    assert any(flow["id"] == "payroll" for flow in body["incoming"])
    assert any(flow["id"] == "consumption" for flow in body["outgoing"])


def test_all_flow_endpoints_exist():
    graph = load_graph()
    ids = {entity.id for entity in graph.entities}
    for flow in graph.flows:
        assert flow.source in ids, flow.id
        assert flow.target in ids, flow.id


def test_all_provenance_ids_exist():
    graph = load_graph()
    source_ids = {source.id for source in graph.sources}
    for flow in graph.flows:
        assert set(flow.source_ids) <= source_ids, flow.id


def test_residual_is_explicit():
    graph = load_graph()
    residuals = [flow for flow in graph.flows if flow.status.value == "residual"]
    assert residuals
    assert all(flow.amount is not None for flow in residuals)
