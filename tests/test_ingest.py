from pathlib import Path

import httpx

from ingest.catalog import load_catalog
from ingest.http import DownloadClient, redact_url


def test_catalog_has_core_source_families():
    specs = load_catalog()
    ids = {item.id for item in specs}
    assert {
        "bea-nipa",
        "bea-input-output",
        "fed-z1",
        "sec-companyfacts",
        "bls-qcew",
        "census-cbp",
        "fec",
        "usaspending",
        "treasury-fiscal-data",
    } <= ids


def test_redact_url_hides_keys():
    redacted = redact_url(
        "https://example.test/data?api_key=secret&UserID=also-secret&year=2026"
    )
    assert "secret" not in redacted
    assert "REDACTED" in redacted
    assert "year=2026" in redacted


def test_download_client_records_hash_and_metadata(tmp_path: Path):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=b"actual-source-bytes",
            headers={"content-type": "text/plain", "etag": "abc"},
            request=request,
        )

    client = DownloadClient(raw_root=tmp_path)
    client._client.close()
    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        headers={"User-Agent": "OpenEconomy-test"},
    )
    try:
        artifact = client.get_and_save(
            "test-source",
            "test-dataset",
            "https://example.test/file.csv?key=secret",
            filename="file.csv",
        )
    finally:
        client.close()

    stored = tmp_path / "test-source" / "test-dataset"
    files = list(stored.rglob("file.csv"))
    assert len(files) == 1
    assert files[0].read_bytes() == b"actual-source-bytes"
    assert artifact.bytes == len(b"actual-source-bytes")
    assert "secret" not in artifact.url
    assert files[0].with_name("file.csv.meta.json").exists()


def test_qcew_curated_snapshot_reconciles():
    import json
    from ingest.http import ROOT

    payload = json.loads(
        (ROOT / "data" / "curated" / "qcew_2025_national_payroll.json").read_text()
    )
    facts = payload["facts"]
    components = sum(
        facts[key]["total_annual_wages_usd"]
        for key in (
            "private",
            "federal-government",
            "state-government",
            "local-government",
        )
    )
    assert components == facts["total-covered"]["total_annual_wages_usd"]
    assert payload["status"] == "reported"
