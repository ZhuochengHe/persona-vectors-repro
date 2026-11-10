"""Render the Assistant Axis collection; requests initialize a NEW empty tab only.

Native tables, heading links and landscape sections require live-structure edits.
Never replay initialization over an existing reading tab.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/papers/assistant-axis"


def utf16(text):
    return len(text.encode("utf-16-le")) // 2


def render(data):
    rows = data["papers"]
    by_id = {r["ID"]: r for r in rows}
    assert len(by_id) == len(rows)
    grouped = [i for g in data["groups"] for i in g["ids"]]
    assert len(grouped) == len(set(grouped)) and set(grouped) == set(by_id)
    ps = []

    def add(text, style="NORMAL_TEXT", bold=False, url=None, key=None):
        ps.append(dict(text=text, style=style, bold=bold, url=url, key=key))

    add('Assistant Axis: Citing Papers', "TITLE")
    add('Default identity · Representation geometry · Persona drift · Behavioral control and agent transfer', "SUBTITLE")
    add('Reading guide', "HEADING_1")
    add('Navigate through research questions or the paper index. IDs open notes; short titles open papers. Abstract findings are separate from body-level methodological evidence. Additional think is reserved for the user.')
    add(data["scope_note"])
    add('Assistant Axis direct-citation list', url="https://mlsanity.com/paper/2601.10387/")
    add('This tab shares the Persona Google Doc. AA IDs and reading data remain separate, with no local Excel synchronization or architecture columns.')
    add('Browse by research question', "HEADING_2")
    for g in data["groups"]:
        add(g["title"] + ' | ' + ', '.join(g["ids"]), key="nav:" + g["key"])
    add('Browse by paper type', "HEADING_2")
    for category in ["Method", "Benchmark", "Survey", "Analysis", "Theory"]:
        ids = [r["ID"] for r in rows if category in r["paper_type"].split("; ")]
        add(category + ': ' + (', '.join(ids) or 'None in the current close-reading set'), key="type:" + category)
    add('Theory is reserved for formal statements and proofs; Analysis may include equations and geometric experiments. Unmarked is the user’s reading status, not the depth of the notes.')
    add('Suggested reading paths', "HEADING_2")
    for text in data["synthesis"]:
        add(text)
    add('Paper index', "HEADING_1", key="index")
    add('Task describes the experiment; Major finding summarizes the abstract; Benchmark / Validation specifies tasks, metrics, and key conditions. Detailed contributions, limitations, and citation evidence are in the notes.')
    add("", key="table-insertion")
    for g in data["groups"]:
        add(g["title"], "HEADING_1", key="group:" + g["key"])
        for identifier in g["ids"]:
            r = by_id[identifier]
            add(identifier + ' | ' + r["title"], "HEADING_2", key="paper:" + identifier)
            add(r["paper_type"] + "　|　Reading status: " + r.get("read_status", 'Unmarked') + "　|　Priority: " + r.get("priority", 'Foundation'))
            add('Paper', url=r["link"])
            if r.get("original_reading_id"):
                add('Original Persona collection ID ' + str(r["original_reading_id"]) + '; notes here are maintained separately, without automatic bidirectional synchronization.')
            for label, key in [('Relation to Assistant Axis', "axis_relation"), ("Research question", "rq")]:
                add(label, bold=True)
                add(r[key])
            add('Methods and contributions', bold=True)
            for n, text in enumerate(r["contributions"], 1):
                add(f"{n}. {text}")
            add("Limitation", bold=True)
            for n, text in enumerate(r["limitations"], 1):
                add(f"{n}. {text}")
            add("Future work", bold=True)
            add('Author-proposed: ' + r["future_work"]["author"])
            add('Reading-derived: ' + r["future_work"]["reading"])
            add('Additional think | User notes', bold=True)
            add(r.get("additional_think") or '(Reserved for user notes)')
            add('Related papers: ' + ', '.join(r.get("related_ids", [])))
            ev = r["reference_evidence"]
            add('Citation relation: ' + ev["status"] + "；" + ev["location"])
            add('Citation evidence', url=ev["url"])
            add('Reading evidence: ' + r["source_version"] + "；" + r["reading_scope"])
            add('Return to paper index', key="back")
    text = "".join(p["text"] + "\n" for p in ps)
    reqs = [{"insertText": {"location": {"index": 1}, "text": text}},
            {"updateTextStyle": {"range": {"startIndex": 1, "endIndex": 1 + utf16(text)},
                                 "textStyle": {"fontSize": {"magnitude": 11, "unit": "PT"}}, "fields": "fontSize"}},
            {"updateParagraphStyle": {"range": {"startIndex": 1, "endIndex": 1 + utf16(text)},
                                      "paragraphStyle": {"spaceBelow": {"magnitude": 6, "unit": "PT"}, "lineSpacing": 110}, "fields": "spaceBelow,lineSpacing"}}]
    md, positions = [], {}
    index = 1
    for p in ps:
        end = index + utf16(p["text"])
        rng = dict(startIndex=index, endIndex=max(index + 1, end))
        if p["key"]:
            positions[p["key"]] = dict(start=index, end=end)
        if p["style"] != "NORMAL_TEXT":
            reqs.append({"updateParagraphStyle": {"range": rng, "paragraphStyle": {"namedStyleType": p["style"], "keepWithNext": True}, "fields": "namedStyleType,keepWithNext"}})
            size = {"TITLE": 22, "SUBTITLE": 13, "HEADING_1": 18, "HEADING_2": 16}[p["style"]]
            reqs.append({"updateTextStyle": {"range": rng, "textStyle": {"fontSize": {"magnitude": size, "unit": "PT"}}, "fields": "fontSize"}})
        elif p["bold"]:
            reqs.extend([
                {"updateTextStyle": {"range": rng, "textStyle": {"bold": True}, "fields": "bold"}},
                {"updateParagraphStyle": {"range": rng, "paragraphStyle": {"keepWithNext": True}, "fields": "keepWithNext"}}])
        elif p["url"]:
            reqs.append({"updateTextStyle": {"range": rng, "textStyle": {"link": {"url": p["url"]}}, "fields": "link"}})
        prefix = {"TITLE": "# ", "SUBTITLE": "", "HEADING_1": "## ", "HEADING_2": "### ", "NORMAL_TEXT": ""}[p["style"]]
        value = prefix + p["text"]
        if p["bold"]:
            value = "**" + p["text"] + "**"
        if p["url"]:
            value = "[" + p["text"] + "](" + p["url"] + ")"
        if p["key"] and p["key"].startswith("paper:"):
            value = '<a id="' + p["key"].split(":")[1] + '"></a>\n\n' + value
        if p["key"] == "back":
            value = '[Return to paper index](#paper-index)'
        md.append(value)
        index = end + 1
    grid = [["ID", 'Short title', 'Type', 'Status', "Task", 'Major finding (abstract)', "Benchmark / Validation"]]
    grid += [[r["ID"], r["short_title"], r["paper_type"], r.get("read_status", 'Unmarked'), r["task"], r["major_finding"], r["validation"]] for r in rows]
    table = ["| " + " | ".join(grid[0]) + " |", "| " + " | ".join(["---"] * 7) + " |"]
    for cells in grid[1:]:
        identifier = cells[0]
        cells = [f"[{identifier}](#{identifier})", f'[{cells[1]}]({by_id[identifier]["link"]})'] + cells[2:]
        table.append("| " + " | ".join(c.replace("|", "\\|").replace("\n", "<br>") for c in cells) + " |")
    pos = next(i for i, p in enumerate(ps) if p["key"] == "table-insertion")
    md[pos] = "\n".join(table)
    return dict(requests=reqs, index_rows=grid, expected_text=text, positions=positions,
                native_index_pass_required=True), "\n\n".join(md) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requests-output", type=Path)
    args = parser.parse_args()
    data = json.loads((BASE / "reading.json").read_text())
    payload, markdown = render(data)
    (BASE / "reading.md").write_text(markdown)
    if args.requests_output:
        args.requests_output.write_text(json.dumps(payload, ensure_ascii=False))
    print(f'Rendered {len(data["papers"])} papers; {len(payload["requests"])} new-document requests.')
