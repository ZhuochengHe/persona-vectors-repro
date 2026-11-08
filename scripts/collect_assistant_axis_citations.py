"""Freeze Assistant Axis direct citers and official abstracts; never overwrite."""
from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from collect_persona_citations import ATOM, clean, fetch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/papers/assistant-axis/sources"
SEED = "2601.10387"


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    requests, totals, raw, cursors = [], [], [], set()

    def snapshot(url, name):
        data = fetch(url)
        (OUT / name).write_bytes(data)
        requests.append(dict(url=url, file=name, sha256=hashlib.sha256(data).hexdigest(),
                             retrieved_at=datetime.now(timezone.utc).isoformat()))
        return data

    cursor = None
    while True:
        params = dict(sort="cited", area="all")
        if cursor is not None:
            params["cursor"] = cursor
        url = f"https://mlsanity.com/api/papers/{SEED}/citers?" + urllib.parse.urlencode(params)
        page = json.loads(snapshot(url, f"citers_{len(totals):02d}.json"))
        totals.append(page["total"])
        raw.extend(page["rows"])
        cursor = page.get("next_cursor")
        if cursor is None:
            break
        if cursor in cursors:
            raise RuntimeError("Repeated citation cursor")
        cursors.add(cursor)
    unique = {re.sub(r"v\d+$", "", row["id"]): row for row in raw}
    if len(set(totals)) != 1 or len(unique) != totals[0]:
        raise RuntimeError("Unstable/incomplete citation snapshot")
    metadata = {}
    ids = list(unique)
    for start in range(0, len(ids), 100):
        if start:
            time.sleep(3.1)
        batch = ids[start:start + 100]
        url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
            dict(id_list=",".join(batch), max_results=len(batch)))
        root = ET.fromstring(snapshot(url, f"arxiv_{start:03d}.xml"))
        for entry in root.findall("a:entry", ATOM):
            identifier = re.sub(r"v\d+$", "", entry.findtext("a:id", "", ATOM).split("/abs/")[-1])
            if identifier not in unique:
                raise RuntimeError(f"Unexpected metadata ID: {identifier}")
            metadata[identifier] = dict(
                title=clean(entry.findtext("a:title", "", ATOM)),
                abstract=clean(entry.findtext("a:summary", "", ATOM)),
                authors=[a.findtext("a:name", "", ATOM) for a in entry.findall("a:author", ATOM)],
                published=entry.findtext("a:published", "", ATOM),
                updated=entry.findtext("a:updated", "", ATOM))
    if set(metadata) != set(unique):
        raise RuntimeError("Official metadata is incomplete")
    candidates = [dict(record_id=f"AA-C{i:03d}", arxiv_id=identifier,
                       paper_url=f"https://arxiv.org/abs/{identifier}",
                       citation_relation_status="source_listed_direct_citer",
                       **metadata[identifier])
                  for i, identifier in enumerate(ids, 1)]
    (OUT / "candidates.json").write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n")
    manifest = dict(seed_arxiv_id=SEED, reported_totals=totals, raw_rows=len(raw),
                    unique_arxiv_ids=len(unique), metadata_count=len(metadata), requests=requests,
                    scope="mlsanity direct-citer snapshot; not cross-database completeness or independent reference verification")
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Frozen {len(candidates)} direct-citer records and official abstracts in {OUT}")


if __name__ == "__main__":
    main()
