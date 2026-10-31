"""Apply recorded individual review decisions and render navigable reading groups."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/papers"
SOURCES = DOCS / "citation_screening_sources"
TABLE = DOCS / "citation_screening_working.csv"


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def paper(row: dict[str, str]) -> str:
    return f"[{escape(row['title'])}]({row['paper_url']})（{row['record_id']}）"


def main() -> None:
    decisions = json.loads((SOURCES / "review_decisions.json").read_text())
    specs = json.loads((SOURCES / "reading_group_specs.json").read_text())
    manifest = json.loads((SOURCES / "manifest.json").read_text())
    checks = {r["record_id"]: r for r in json.loads((SOURCES / "primary_reference_checks.json").read_text())}
    with TABLE.open(newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    by_number = {int(r["record_id"].split("C")[-1]): r for r in rows}
    assert len(decisions) == len(rows) == manifest["unique_ids"]
    assert len({d[0] for d in decisions}) == len(rows)
    starters = {i for group in specs for i in group["start"]}
    for number, tier, cluster, reason, old_priority in decisions:
        row = by_number[number]
        hard_keep = row["persona_title_hit"] == "true" or row["persona_abstract_hit"] == "true"
        assert not (hard_keep and tier in {"排除", "待定"}), row["record_id"]
        row["screening_status"] = {"排除": "exclude", "待定": "pending"}.get(tier, "keep")
        row["relevance_tier"] = tier if tier not in {"排除", "待定"} else "待归类"
        row["primary_cluster"] = cluster if cluster != "范围外" else ""
        row["decision_reason"] = reason
        if hard_keep and "硬保留" not in reason:
            row["decision_reason"] += "；标题/摘要命中persona，按硬规则保留"
        row["reading_priority"] = "P1" if number in starters else ("P2" if old_priority == "P1" else old_priority)
        row["review_depth"] = "title_abstract_review"
        row["evidence_type"] = "title_and_official_abstract; full_text_claims_not_audited"
        tags = []
        if hard_keep:
            tags.append("persona硬保留")
        text = row["title"] + " " + row["abstract"]
        for tag, pattern in [
            ("情绪", r"\b(?:emotion\w*|affect|affective|empathy|sentiment)\b"),
            ("迎合", r"sycophan\w*"), ("价值", r"\b(?:values?|moral\w*|ethical)\b"),
            ("自报与行动", r"self-report|self report|revealed preference"),
            ("多轮", r"multi-turn|long-horizon|long-context|long sessions"),
            ("组合", r"compos\w*|multi-trait|multi-attribute"),
            ("用户模拟", r"user simulat\w*|human simulat\w*"),
        ]:
            if re.search(pattern, text, re.I):
                tags.append(tag)
        row["secondary_tags"] = "; ".join(tags)
        notes = ["主类与优先级为摘要初筛判断；交叉标签由词项辅助生成，未用于自动排除。",
                 "P1=每组起步阅读串；P2=专题延伸；P3=外围应用或待核实。"]
        check = checks.get(row["record_id"])
        if check and check["status"] == "verified_in_primary_html":
            row["citation_relation_status"] = "verified_in_primary_html"
            row["citation_evidence"] = f"Seed citation found in {check['url']}; saved in primary_reference_checks.json; also present in frozen direct-citer list"
            notes.append("额外核对正文引用关系，不代表已完整阅读全文。")
        elif check:
            notes.append("HTML未定位到种子引用，仍以冻结被引列表为来源；不据此断言未引用。")
        if number in {148, 173}:
            notes.append("C148与C173为疑似前作/扩展版，作者和主题重合；未确认版本同一性，暂不合并或计作独立研究。")
        row["notes"] = " ".join(notes)
    write_csv(TABLE, rows, fields)
    keeps = [r for r in rows if r["screening_status"] == "keep"]
    pending = [r for r in rows if r["screening_status"] == "pending"]
    excludes = [r for r in rows if r["screening_status"] == "exclude"]
    write_csv(DOCS / "citation_screening_retained.csv", keeps, fields)
    groups_dir = DOCS / "citation_reading_groups"
    groups_dir.mkdir(exist_ok=True)
    for group in specs:
        members = [r for r in keeps if r["primary_cluster"] == group["name"]]
        lines = [f"# {group['name']}", "", "[返回总导航](../citation_screening_reading_map.md) · [工作表](../citation_screening_working.csv)", "",
                 f"本组 {len(members)} 条保留记录。按标题和官方摘要初步归类，尚未逐篇完成全文审阅。", "",
                 f"要带着读的问题：{group['question']}", "", f"阅读时注意：{group['tension']}", "",
                 "## 起步阅读顺序", ""]
        for index, number in enumerate(group["start"], 1):
            row = by_number[number]
            lines.append(f"{index}. {paper(row)} — {row['decision_reason']}")
        lines += ["", "## 后续延伸（可跨组）", ""]
        for number in group["next"]:
            row = by_number[number]
            lines.append(f"- {paper(row)} — {row['decision_reason']}")
        lines += ["", "## 本组全部保留记录", "", "P1/P2/P3 表示阅读顺序建议，不表示论文质量或结论可信度。编号来自冻结源列表顺序，不是推荐排名。", "",
                  "| 编号 | 论文 | 三档 | 优先级 | 纳入理由 |", "|---|---|---|---|---|"]
        for row in sorted(members, key=lambda r: (r["reading_priority"], r["record_id"])):
            lines.append(f"| {row['record_id']} | [{escape(row['title'])}]({row['paper_url']}) | {row['relevance_tier']} | {row['reading_priority']} | {escape(row['decision_reason'])} |")
        (groups_dir / (group["slug"] + ".md")).write_text("\n".join(lines) + "\n")
    counts = Counter(r["relevance_tier"] for r in keeps)
    primary_count = sum(r["citation_relation_status"] == "verified_in_primary_html" for r in rows)
    lines = ["# Persona Vectors 被引文献阅读导航", "", "更新：2026-10-30。阶段：完整源列表获取与逐篇标题/摘要初筛完成；九个方向为人工初步聚类，可随全文阅读更新。", "",
             "[规则基准](citation_screening_rules.md) · [完整工作CSV](citation_screening_working.csv) · [保留集CSV](citation_screening_retained.csv) · [抓取清单及哈希](citation_screening_sources/manifest.json)", "",
             "## 本批范围与结果", "",
             f"唯一候选来源是种子论文 [2507.21509](https://arxiv.org/abs/2507.21509) 的 [mlsanity直接被引接口](https://mlsanity.com/api/papers/2507.21509/citers?sort=cited&area=all)。获取开始时间：`{manifest['started_at']}`。四页返回总数一致，已保存原始JSON；没有添加主题搜索候选，也没有递归扩展。", "",
             f"- 源列表：{len(rows)} 条，{len({r['arxiv_id'] for r in rows})} 个不同 arXiv ID；官方arXiv标题、作者、摘要补齐 {manifest['metadata_count']} 条。",
             f"- 保留 {len(keeps)} 条：核心相关 {counts['核心相关']}、问题相关 {counts['问题相关']}、方法参考 {counts['方法参考']}。",
             f"- 标题或摘要命中 persona 的 85 条全部保留；另有待定 {len(pending)} 条、排除 {len(excludes)} 条，理由均留在工作表。",
             f"- 抽查 27 条正文引用关系：{primary_count} 条在官方HTML定位到种子引用；其余3条HTML未找到，仍仅按源列表记录。未对376条逐一独立核对参考文献。",
             "- 对规范化arXiv ID、完全一致标题和非空DOI做去重检查，没有发现精确重复。C148/C173疑似前作/扩展版，暂保留关联注记；因此376不是已确认的独立研究数。",
             "- 这是mlsanity这一来源的完整快照，不代表Google Scholar、Semantic Scholar等所有数据库的完整并集。", "",
             "筛选采用宽口径，目的是帮助发现研究问题；用户画像、社会模拟、哲学理论等不会因偏离现有实验被自动排除。论文的经验性主张目前大多依据作者摘要，未完成方法、数据和统计可信度审计。", "",
             "## 按方向逐块读", "", "每组提供5篇起步串、延伸列表、全部保留记录。全局P1共45条，只表示起步导航；不需要先读完45篇才选方向。", "",
             "| 方向 | 主类记录数 | 主要问题 |", "|---|---:|---|"]
    if (DOCS / "citation_screening_shortlist.md").exists():
        lines[2:2] = ["**当前主阅读清单已压缩为[高价值精选30篇（先读10篇）](citation_screening_shortlist.md)。本文保留第一轮宽口径结果，不再作为逐篇必读清单。**", ""]
    for group in specs:
        count = sum(r["primary_cluster"] == group["name"] for r in keeps)
        lines.append(f"| [{group['name']}](citation_reading_groups/{group['slug']}.md) | {count} | {group['question']} |")
    lines += ["", "## 几组适合并读的分歧", ""]
    for title, numbers, why in [
        ("人格向量能组合到什么程度", [37, 104, 310, 334], "对照向量代数、trait干扰、模型默认倾向与曲面几何，避免只看其中一种解释。"),
        ("失配是人格招募、身份失稳还是数据泛化", [155, 214, 303, 283], "这些摘要提出不同解释，应用范围和对照条件应在全文阅读中逐项比较。"),
        ("可读、可控和自然使用是否一致", [58, 300, 291, 351, 322], "把探针检测、全局干预、自然范围救援和行为回路拆开检验。"),
        ("表达人格是否改变行动", [10, 92, 344, 376], "同一trait在自陈、文本措辞和博弈决策上的效果可能不同。"),
        ("情绪是什么，又与人格有什么关系", [3, 165, 146, 348, 206], "比较功能性情绪、去关键词验证、情境解释、语用残差与自我语体；不预设共享一个子空间。"),
    ]:
        lines.append(f"- **{title}**：" + " → ".join(paper(by_number[i]) for i in numbers) + f"。{why}")
    lines += ["", "## 待定记录", "", "尚缺相关正文的实质性审阅，引用关系查验不等于主题审阅。保留这些记录以防误删。", "",
              "| 编号 | 论文 | 待核实内容 |", "|---|---|---|"]
    for row in pending:
        lines.append(f"| {row['record_id']} | [{escape(row['title'])}]({row['paper_url']}) | {escape(row['decision_reason'])} |")
    lines += ["", "## 排除记录", "", "全部未命中persona硬规则。以后若补充材料改变判断，可从工作表恢复。", "",
              "| 编号 | 论文 | 理由 |", "|---|---|---|"]
    for row in excludes:
        lines.append(f"| {row['record_id']} | [{escape(row['title'])}]({row['paper_url']}) | {escape(row['decision_reason'])} |")
    lines += ["", "## 工作约定与复现", "",
              "- 筛选状态、三档相关性、主类和阅读优先级互相独立。交叉标签是词项辅助，不是自动排除器。",
              "- `method` 和 `research_question` 字段暂留给后续全文笔记；当前逐篇判断在 `decision_reason`，研究方向的问题在分组导航。",
              "- 原始抓取见 `scripts/collect_persona_citations.py`，其保护逻辑禁止覆盖已有快照。",
              "- 逐篇人工决策保存于 `citation_screening_sources/review_decisions.json`，分组起步串保存于 `reading_group_specs.json`。",
              "- `python scripts/render_persona_citation_review.py` 从这些决策重建工作表和导航；若直接修改CSV，请先同步决策源文件，以免重建覆盖。",
              "- 下阶段优先完成13条边界案例、疑似扩展版核对，以及所选方向的全文阅读；更新判断时保留证据位置和版本。"]
    (DOCS / "citation_screening_reading_map.md").write_text("\n".join(lines) + "\n")
    summary = {"rows": len(rows), "kept": len(keeps), "pending": len(pending), "excluded": len(excludes),
               "tiers": dict(counts), "mandatory_persona_kept": sum(r["persona_title_hit"] == "true" or r["persona_abstract_hit"] == "true" for r in keeps),
               "primary_reference_verified": primary_count,
               "clusters": {g["name"]: sum(r["primary_cluster"] == g["name"] for r in keeps) for g in specs},
               "priority": dict(Counter(r["reading_priority"] for r in keeps))}
    (SOURCES / "screening_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
