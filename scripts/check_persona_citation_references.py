"""Check selected source-listed citers' references; this is not full-paper review."""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/papers/citation_screening_sources"


class TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.links: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.links.extend(v for k, v in attrs if k == "href" and v is not None)


def main() -> None:
    selected = {1, 3, 37, 63, 92, 104, 155, 198, 303, 310, 334, 371, 148, 173}
    decisions = json.loads((OUT / "review_decisions.json").read_text())
    selected.update(item[0] for item in decisions if item[1] == "待定")
    rows = list(csv.DictReader((ROOT / "docs/papers/citation_screening_working.csv").open()))
    target = OUT / "primary_reference_checks.json"
    if target.exists():
        raise SystemExit("Preserve existing checks rather than overwrite.")
    checks = []
    for number in sorted(selected):
        row = rows[number - 1]
        url = f"https://arxiv.org/html/{row['arxiv_id']}"
        record = {"record_id": row["record_id"], "arxiv_id": row["arxiv_id"],
                  "url": url, "checked_at": datetime.now(timezone.utc).isoformat(),
                  "review_scope": "reference verification and bounded topical excerpts only"}
        try:
            with urllib.request.urlopen(url, timeout=25) as response:
                raw = response.read(4_000_000).decode("utf-8", errors="replace")
            parser = TextParser()
            parser.feed(raw)
            text = " ".join(" ".join(parser.parts).split())
            matches = list(re.finditer(r"2507\.21509|Persona\s+[Vv]ectors\s*:\s*Monitoring", text))
            links = [link for link in parser.links if "2507.21509" in link]
            record.update(status="verified_in_primary_html" if matches or links else "not_found_in_html",
                          seed_links=links,
                          reference_excerpts=[text[max(0, m.start()-180):m.end()+500] for m in matches[:3]])
            excerpt_patterns = [r"(?:^|\s)Abstract", r"persona", r"steering", r"2507\.21509"]
            excerpts = []
            for pattern in excerpt_patterns:
                hits = list(re.finditer(pattern, text, re.I))
                for match in hits[:2]:
                    excerpts.append(text[max(0, match.start()-180):match.end()+1200])
            record["topical_excerpts"] = excerpts
            if number in {148, 173}:
                record["version_excerpts"] = [text[max(0,m.start()-150):m.end()+500]
                    for m in list(re.finditer(r"extend|previous|2605\.26365|2606\.11399", text,re.I))[:8]]
        except Exception as exc:
            record.update(status="html_unavailable", error=str(exc))
        checks.append(record)
        target.write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n")
        print(row["record_id"], record["status"], flush=True)
        time.sleep(1.5)


if __name__ == "__main__":
    main()
