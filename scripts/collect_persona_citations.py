"""Snapshot direct citers only, then enrich those IDs with official arXiv metadata."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/papers/citation_screening_sources"
TABLE = ROOT / "docs/papers/citation_screening_working.csv"
SEED = "2507.21509"
BASE = f"https://mlsanity.com/api/papers/{SEED}/citers"
ATOM = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "PersonaCitationReview/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def clean(value: str) -> str:
    return " ".join(value.split())


def persona_hit(value: str) -> bool:
    # Do not match personality/personalization as persona.
    return bool(re.search(r"\bpersonas?\b", value, re.IGNORECASE))


def main() -> None:
    if OUT.exists() or len(TABLE.read_text().splitlines()) != 1:
        raise SystemExit("Existing snapshot or populated table: preserve it; do not overwrite.")
    OUT.mkdir()
    started = datetime.now(timezone.utc).isoformat()
    requests = []

    def save_request(url: str, filename: str) -> bytes:
        data = fetch(url)
        (OUT / filename).write_bytes(data)
        requests.append({"url": url, "file": filename, "sha256": hashlib.sha256(data).hexdigest(),
                         "retrieved_at": datetime.now(timezone.utc).isoformat()})
        return data

    cursor = None
    raw_rows = []
    totals = []
    seen_cursors = set()
    while True:
        params = {"sort": "cited", "area": "all"}
        if cursor is not None:
            params["cursor"] = cursor
        page = json.loads(save_request(BASE + "?" + urllib.parse.urlencode(params),
                                       f"citers_{len(totals):02d}.json"))
        totals.append(page["total"])
        raw_rows.extend(page["rows"])
        cursor = page.get("next_cursor")
        if cursor is None:
            break
        if cursor in seen_cursors:
            raise RuntimeError("Repeated cursor")
        seen_cursors.add(cursor)
    by_id = {}
    for row in raw_rows:
        by_id.setdefault(re.sub(r"v\d+$", "", row["id"]), row)
    if len(set(totals)) != 1 or len(by_id) != totals[0]:
        raise RuntimeError(f"Unstable/incomplete citation snapshot: {totals}, {len(by_id)} IDs")
    print(f"Captured {len(raw_rows)} rows, {len(by_id)} unique arXiv IDs", flush=True)

    ids = list(by_id)
    metadata = {}
    for start in range(0, len(ids), 100):
        if start:
            time.sleep(3.1)
        batch = ids[start:start + 100]
        url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
            {"id_list": ",".join(batch), "max_results": len(batch)})
        root = ET.fromstring(save_request(url, f"arxiv_{start:03d}.xml"))
        for entry in root.findall("a:entry", ATOM):
            identifier = entry.findtext("a:id", "", ATOM).split("/abs/")[-1]
            identifier = re.sub(r"v\d+$", "", identifier)
            if identifier not in by_id:
                raise RuntimeError(f"Unexpected arXiv ID: {identifier}")
            metadata[identifier] = {
                "title": clean(entry.findtext("a:title", "", ATOM)),
                "abstract": clean(entry.findtext("a:summary", "", ATOM)),
                "authors": "; ".join(a.findtext("a:name", "", ATOM)
                                      for a in entry.findall("a:author", ATOM)),
                "year": entry.findtext("a:published", "", ATOM)[:4],
                "doi": entry.findtext("x:doi", "", ATOM),
            }
        print(f"Official metadata: {len(metadata)}/{len(ids)}", flush=True)

    with TABLE.open(newline="") as handle:
        fields = next(csv.reader(handle))
    rows = []
    for index, (identifier, item) in enumerate(by_id.items(), 1):
        row = dict.fromkeys(fields, "")
        row.update(metadata.get(identifier, {}))
        row["title"] = row["title"] or item["title"]
        row["year"] = row["year"] or item["created"][:4]
        title_hit, abstract_hit = persona_hit(row["title"]), persona_hit(row["abstract"])
        row.update(record_id=f"PV-C{index:03d}", arxiv_id=identifier,
                   paper_url=f"https://arxiv.org/abs/{identifier}", citation_source="mlsanity",
                   citation_source_record_url=BASE + "?sort=cited&area=all",
                   retrieved_at=started, citation_relation_status="source_listed_direct_citer",
                   citation_evidence=f"Frozen citers_*.json contains arXiv ID {identifier}; seed={SEED}; reference not yet independently checked",
                   abstract_status="official_arxiv" if row["abstract"] else "missing",
                   persona_title_hit=str(title_hit).lower(), persona_abstract_hit=str(abstract_hit).lower(),
                   screening_status="keep" if title_hit or abstract_hit else "pending",
                   relevance_tier="待归类",
                   decision_reason="标题或摘要命中 persona：按硬规则保留" if title_hit or abstract_hit else "待逐篇阅读标题和摘要",
                   review_depth="metadata_rule_only", evidence_location="title; abstract (official arXiv Atom)",
                   rules_version="2026-10-30")
        rows.append(row)
    with TABLE.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    manifest = {"seed_arxiv_id": SEED, "started_at": started,
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "reported_totals": totals, "raw_rows": len(raw_rows), "unique_ids": len(by_id),
                "metadata_count": len(metadata), "missing_metadata_ids": sorted(set(ids) - set(metadata)),
                "source_scope": "Direct citers reported by mlsanity; not a cross-database completeness claim",
                "requests": requests}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Saved table; mandatory persona keeps: {sum(r['screening_status'] == 'keep' for r in rows)}")


if __name__ == "__main__":
    main()
