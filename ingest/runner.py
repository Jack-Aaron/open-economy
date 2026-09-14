from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from dotenv import load_dotenv

from ingest.adapters import ADAPTERS
from ingest.http import Artifact, DownloadClient, ROOT

MANIFEST = ROOT / "data" / "raw" / "manifest.jsonl"


def append_manifest(artifacts: list[Artifact]) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("a", encoding="utf-8") as handle:
        for artifact in artifacts:
            handle.write(json.dumps(asdict(artifact), sort_keys=True) + "\n")


def sync_sources(
    source_ids: list[str], *, include_bulk: bool = False, strict: bool = False
) -> tuple[list[Artifact], dict[str, str]]:
    load_dotenv(ROOT / ".env")
    artifacts: list[Artifact] = []
    errors: dict[str, str] = {}
    with DownloadClient() as client:
        for source_id in source_ids:
            adapter_type = ADAPTERS[source_id]
            try:
                fetched = adapter_type().sync(client, include_bulk=include_bulk)
                append_manifest(fetched)
                artifacts.extend(fetched)
            except Exception as exc:
                errors[source_id] = str(exc)
                if strict:
                    raise
    return artifacts, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Download authoritative OpenEconomy source datasets."
    )
    parser.add_argument(
        "--source",
        action="append",
        choices=sorted(ADAPTERS),
        help="Source to sync. Repeat for multiple sources; defaults to all implemented sources.",
    )
    parser.add_argument(
        "--include-bulk",
        action="store_true",
        help="Also download very large bulk archives such as Fed Z.1 and SEC Company Facts.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Stop on the first unavailable or key-missing source.",
    )
    args = parser.parse_args(argv)

    selected = args.source or sorted(ADAPTERS)
    artifacts, errors = sync_sources(
        selected, include_bulk=args.include_bulk, strict=args.strict
    )
    print(f"Downloaded {len(artifacts)} artifact(s).")
    for source_id, message in errors.items():
        print(f"SKIPPED {source_id}: {message}", file=sys.stderr)
    return 1 if args.strict and errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
