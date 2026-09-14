from fastapi.testclient import TestClient

from app.main import app
from app.repository import load_graph

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_reported_graph_is_default():
    response = client.get("/api/graph")
    assert response.status_code == 200
    body = response.json()
    assert body["metadata"]["mode"] == "reported"
    assert body["flows"]
    assert {flow["status"] for flow in body["flows"]} == {"reported"}
    assert any(flow["id"] == "private-covered-wages-2025" for flow in body["flows"])


def test_prototype_graph_remains_available():
    response = client.get("/api/graph?mode=prototype")
    assert response.status_code == 200
    body = response.json()
    assert any(flow["id"] == "payroll" for flow in body["flows"])
    assert any(flow["layer"] == "political" for flow in body["flows"])


def test_layer_filter():
    response = client.get("/api/graph?mode=prototype&layer=political")
    assert response.status_code == 200
    body = response.json()
    assert body["flows"]
    assert {flow["layer"] for flow in body["flows"]} == {"political"}


def test_households_reported_detail_contains_wages():
    response = client.get("/api/entities/households")
    assert response.status_code == 200
    body = response.json()
    assert any(flow["id"] == "private-covered-wages-2025" for flow in body["incoming"])
    assert any(flow["id"] == "government-covered-wages-2025" for flow in body["incoming"])


def test_all_flow_endpoints_exist():
    for mode in ("reported", "prototype"):
        graph = load_graph(mode)
        ids = {entity.id for entity in graph.entities}
        for flow in graph.flows:
            assert flow.source in ids, flow.id
            assert flow.target in ids, flow.id


def test_all_provenance_ids_exist():
    for mode in ("reported", "prototype"):
        graph = load_graph(mode)
        source_ids = {source.id for source in graph.sources}
        for flow in graph.flows:
            assert set(flow.source_ids) <= source_ids, flow.id


def test_residual_is_explicit_in_prototype():
    graph = load_graph("prototype")
    residuals = [flow for flow in graph.flows if flow.status.value == "residual"]
    assert residuals
    assert all(flow.amount is not None for flow in residuals)
