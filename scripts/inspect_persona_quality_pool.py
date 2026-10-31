"""Save bounded official-paper evidence for a contribution-focused second pass."""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/papers/citation_screening_sources"
POOL = [1, 3, 8, 9, 10, 11, 12, 14, 17, 18, 21, 30, 33, 37, 41, 43, 63,
        69, 71, 96, 103, 104, 105, 118, 119, 127, 144, 147, 152, 153,
        180, 185, 196, 199, 202, 303, 329, 334, 344, 348, 353, 355, 375]
NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}


class PaperParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[dict] = []
        self.affiliations: list[str] = []
        self.blocks: list[dict[str, str]] = []
        self.section = "frontmatter"
        self.header = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"br", "hr", "img", "meta", "link", "input", "source", "wbr"}:
            return
        self.stack.append({"tag": tag, "attrs": dict(attrs), "text": []})

    def handle_data(self, data: str) -> None:
        if any(frame["tag"] in {"script", "style"} for frame in self.stack):
            return
        for frame in self.stack:
            frame["text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        index = next((i for i in range(len(self.stack)-1, -1, -1) if self.stack[i]["tag"] == tag), None)
        if index is None:
            return
        frame = self.stack[index]
        self.stack = self.stack[:index]
        text = " ".join(" ".join(frame["text"]).split())
        classes = frame["attrs"].get("class", "") or ""
        if "ltx_role_affiliation" in classes:
            self.affiliations.append(text.removeprefix("Affiliation:").strip())
        if tag == "div" and classes == "ltx_authors":
            self.header = text
        if tag in {"h2", "h3", "h4"}:
            self.section = text
        if tag == "p" and "ltx_p" in classes:
            self.blocks.append({"section": self.section, "id": frame["attrs"].get("id", ""), "text": text})


def main() -> None:
    with (ROOT / "docs/papers/citation_screening_working.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    metadata = {}
    for path in SOURCE.glob("arxiv_*.xml"):
        for entry in ET.fromstring(path.read_bytes()).findall("a:entry", NS):
            identifier = re.sub(r"v\d+$", "", entry.findtext("a:id", "", NS).split("/abs/")[-1])
            metadata[identifier] = {"comment": entry.findtext("x:comment", "", NS),
                                    "journal_ref": entry.findtext("x:journal_ref", "", NS)}
    output = SOURCE / "quality_evidence.json"
    if output.exists():
        raise SystemExit("Existing evidence snapshot: do not overwrite.")
    records = []
    for number in POOL:
        row = rows[number-1]
        url = f"https://arxiv.org/html/{row['arxiv_id']}"
        item = {"record_id": row["record_id"], "arxiv_id": row["arxiv_id"], "title": row["title"],
                "source_url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata.get(row["arxiv_id"], {}), "review_scope": "affiliations and selected body sections, not full-paper audit"}
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                raw = response.read(6_000_000).decode("utf-8", errors="replace")
            parser = PaperParser()
            parser.feed(raw)
            item["affiliations"] = list(dict.fromkeys(parser.affiliations))
            item["author_header"] = parser.header[:5500]
            conclusions = [block for block in parser.blocks if re.search(r"limit|discussion|conclusion", block["section"], re.I)]
            contributions = [block for block in parser.blocks if re.search(r"contribut|we (?:find|show|demonstrate|propose|introduce)", block["text"], re.I)
                             and not re.search(r"append|abstract", block["section"], re.I)]
            experiments = [block for block in parser.blocks if re.search(r"experimental setup|experimental results|evaluation|results", block["section"], re.I)]
            def bounded(blocks: list[dict], count: int, size: int) -> list[dict]:
                return [{**block, "text": block["text"][:size]} for block in blocks[:count]]
            item["contribution_excerpts"] = bounded(contributions, 2, 1700)
            item["evaluation_excerpts"] = bounded(experiments, 2, 1700)
            item["limitations_conclusion_excerpts"] = bounded(conclusions, 3, 1800)
            item["html_status"] = "available" if parser.blocks else "no_article_paragraphs"
        except Exception as exc:
            item.update(html_status="unavailable", error=str(exc))
        records.append(item)
        output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
        print(item["record_id"], item["html_status"], "; ".join(item.get("affiliations", []))[:180], flush=True)
        time.sleep(1.5)


if __name__ == "__main__":
    main()
