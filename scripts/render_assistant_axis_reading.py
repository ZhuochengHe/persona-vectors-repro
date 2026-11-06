"""Render the independent Assistant Axis collection; requests initialize NEW Docs only.

Native tables, heading links and landscape sections require live-structure edits.
Never replay initialization over an existing reading document.
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

    add("Assistant Axis 被引阅读", "TITLE")
    add("默认身份 · 表征几何 · 人格漂移 · 行为控制与agent迁移", "SUBTITLE")
    add("阅读导航", "HEADING_1")
    add("从研究问题或论文总表进入详细笔记；点击ID打开笔记、短标题打开论文。摘要一句话结论与正文方法证据分开。Additional think专留给用户。")
    add(data["scope_note"])
    add("Assistant Axis直接被引列表", url="https://mlsanity.com/paper/2601.10387/")
    add("这份文档独立维护，不与原Persona Vectors表或本地Excel同步；不设置模型架构列。")
    add("按研究问题查找", "HEADING_2")
    for g in data["groups"]:
        add(g["title"] + "｜" + "、".join(g["ids"]), key="nav:" + g["key"])
    add("按论文类型查找", "HEADING_2")
    for category in ["Method", "Benchmark", "Survey", "Analysis", "Theory"]:
        ids = [r["ID"] for r in rows if category in r["paper_type"].split("; ")]
        add(category + "：" + ("、".join(ids) or "当前精读集无此类"), key="type:" + category)
    add("Theory仅用于正式命题与证明；Analysis可以包含公式和几何实验。未标记是用户阅读状态，不等于笔记阅读深度。")
    add("如何串读这些证据", "HEADING_2")
    for text in data["synthesis"]:
        add(text)
    add("论文总表", "HEADING_1", key="index")
    add("Task写实验任务；Major finding提炼自摘要；Benchmark / Validation写任务、指标与关键条件。详细贡献、局限及引用关系见正文。")
    add("", key="table-insertion")
    for g in data["groups"]:
        add(g["title"], "HEADING_1", key="group:" + g["key"])
        for identifier in g["ids"]:
            r = by_id[identifier]
            add(identifier + "｜" + r["title"], "HEADING_2", key="paper:" + identifier)
            add(r["paper_type"] + "　|　阅读状态：" + r.get("read_status", "未标记") + "　|　优先级：" + r.get("priority", "基础"))
            add("论文原文", url=r["link"])
            if r.get("original_reading_id"):
                add("原Persona阅读表ID " + str(r["original_reading_id"]) + "；此处是独立笔记，不自动双向同步。")
            for label, key in [("与Assistant Axis的关系", "axis_relation"), ("Research question", "rq")]:
                add(label, bold=True)
                add(r[key])
            add("方法与贡献", bold=True)
            for n, text in enumerate(r["contributions"], 1):
                add(f"{n}. {text}")
            add("Limitation", bold=True)
            for n, text in enumerate(r["limitations"], 1):
                add(f"{n}. {text}")
            add("Future work", bold=True)
            add("作者提出：" + r["future_work"]["author"])
            add("阅读推演：" + r["future_work"]["reading"])
            add("Additional think｜用户笔记", bold=True)
            add(r.get("additional_think") or "（留空，供用户填写）")
            add("关联论文：" + "、".join(r.get("related_ids", [])))
            ev = r["reference_evidence"]
            add("引用关系：" + ev["status"] + "；" + ev["location"])
            add("引用证据原文", url=ev["url"])
            add("阅读证据：" + r["source_version"] + "；" + r["reading_scope"])
            add("返回论文总表", key="back")
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
            value = "[返回论文总表](#论文总表)"
        md.append(value)
        index = end + 1
    grid = [["ID", "论文短标题", "类型", "阅读状态", "Task", "Major finding（摘要）", "Benchmark / Validation"]]
    grid += [[r["ID"], r["short_title"], r["paper_type"], r.get("read_status", "未标记"), r["task"], r["major_finding"], r["validation"]] for r in rows]
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
