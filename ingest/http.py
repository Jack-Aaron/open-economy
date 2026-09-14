from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "data" / "raw"
_SECRET_QUERY_KEYS = {
    "api_key",
    "apikey",
    "key",
    "registrationkey",
    "userid",
    "user_id",
}


@dataclass(frozen=True)
class Artifact:
    source_id: str
    dataset_id: str
    path: str
    url: str
    retrieved_at: str
    sha256: str
    bytes: int
    content_type: str | None = None


def redact_url(url: str) -> str:
    split = urlsplit(url)
    query = []
    for key, value in parse_qsl(split.query, keep_blank_values=True):
        query.append((key, "REDACTED" if key.lower() in _SECRET_QUERY_KEYS else value))
    return urlunsplit((split.scheme, split.netloc, split.path, urlencode(query), split.fragment))


class DownloadClient:
    def __init__(
        self,
        raw_root: Path = RAW_ROOT,
        user_agent: str | None = None,
        timeout_seconds: float = 120,
    ) -> None:
        self.raw_root = raw_root
        self.user_agent = user_agent or os.getenv(
            "OPEN_ECONOMY_USER_AGENT",
            "OpenEconomy/0.2 (+https://github.com/Jack-Aaron/open-economy)",
        )
        self._client = httpx.Client(
            headers={"User-Agent": self.user_agent, "Accept-Encoding": "gzip, deflate"},
            timeout=httpx.Timeout(timeout_seconds),
            follow_redirects=True,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "DownloadClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        response = self._client.request(
            method,
            url,
            params=params,
            json=json_body,
            headers=headers,
        )
        response.raise_for_status()
        return response

    def save_response(
        self,
        source_id: str,
        dataset_id: str,
        response: httpx.Response,
        *,
        filename: str | None = None,
    ) -> Artifact:
        retrieved_at = datetime.now(UTC)
        date_dir = retrieved_at.strftime("%Y-%m-%d")
        target_dir = self.raw_root / source_id / dataset_id / date_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        if not filename:
            filename = Path(response.url.path).name or "response.bin"
        target = target_dir / filename
        target.write_bytes(response.content)

        digest = hashlib.sha256(response.content).hexdigest()
        try:
            artifact_path = str(target.relative_to(ROOT))
        except ValueError:
            artifact_path = str(target.relative_to(self.raw_root))

        artifact = Artifact(
            source_id=source_id,
            dataset_id=dataset_id,
            path=artifact_path,
            url=redact_url(str(response.url)),
            retrieved_at=retrieved_at.isoformat(),
            sha256=digest,
            bytes=len(response.content),
            content_type=response.headers.get("content-type"),
        )
        meta = target.with_name(target.name + ".meta.json")
        meta.write_text(
            json.dumps(
                {
                    **asdict(artifact),
                    "etag": response.headers.get("etag"),
                    "last_modified": response.headers.get("last-modified"),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return artifact

    def get_and_save(
        self,
        source_id: str,
        dataset_id: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        filename: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> Artifact:
        response = self.request("GET", url, params=params, headers=headers)
        return self.save_response(source_id, dataset_id, response, filename=filename)

    def post_json_and_save(
        self,
        source_id: str,
        dataset_id: str,
        url: str,
        body: dict[str, Any],
        *,
        filename: str = "response.json",
        headers: dict[str, str] | None = None,
    ) -> Artifact:
        response = self.request("POST", url, json_body=body, headers=headers)
        return self.save_response(source_id, dataset_id, response, filename=filename)
