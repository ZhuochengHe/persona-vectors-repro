"""Render a small contribution-focused reading list without deleting the broad corpus."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/papers"
SOURCE = DOCS / "citation_screening_sources"
TABLE = DOCS / "citation_screening_working.csv"
EXTRA_FIELDS = ["round2_status", "shortlist_tier", "shortlist_reason", "verified_affiliations",
                "venue", "venue_verification", "venue_source_url", "institution_source_url",
                "main_contribution", "limitation_or_reading_caution", "quality_review_scope",
                "quality_evidence_location"]
GROUPS = [
    ("人格空间与起源", "人格是什么结构，又从什么时候出现？"),
    ("情绪与心理表征", "情绪是否只是表达语气，还是有独立行为作用？"),
    ("人格、偏好与行动", "测到人格之后，是否真正改变了选择和行动？"),
    ("训练泛化与机制", "trait怎样被学到、传递，为什么会跨域泛化？"),
    ("干预方法", "有哪些机制不同、值得比较的控制路线？"),
    ("监测与解释", "该读什么内部信号，怎样避免过度解释？"),
    ("推理、角色与用户表征", "persona如何连接推理内部角色和模型对用户的理解？"),
]


def safe(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    decisions = json.loads((SOURCE / "quality_decisions.json").read_text())
    evidence = {r["record_id"]: r for r in json.loads((SOURCE / "quality_evidence.json").read_text())}
    deferred = {f"PV-C{number:03d}": reason for number, reason in
                json.loads((SOURCE / "quality_pool_deferred.json").read_text())}
    with TABLE.open(newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    fields += [field for field in EXTRA_FIELDS if field not in fields]
    by_id = {r["record_id"]: r for r in rows}
    selected = {f"PV-C{d[0]:03d}": d for d in decisions}
    assert len(selected) == len(decisions) == 30
    assert set(selected).issubset(by_id)
    assert set(evidence) == set(selected) | set(deferred)
    for row in rows:
        rid = row["record_id"]
        for field in EXTRA_FIELDS:
            row[field] = ""
        if rid in selected:
            (number, tier, group, affiliations, venue, venue_status, venue_url, contribution, caution) = selected[rid]
            assert row["screening_status"] == "keep"
            assert evidence[rid]["html_status"] == "available"
            row.update(round2_status="shortlisted", shortlist_tier=tier,
                       shortlist_reason=contribution, verified_affiliations=affiliations,
                       venue=venue, venue_verification=venue_status, venue_source_url=venue_url,
                       institution_source_url=evidence[rid]["source_url"], main_contribution=contribution,
                       limitation_or_reading_caution=caution,
                       quality_review_scope="author_header_and_selected_contribution_discussion_limitation_sections; not_full_paper_audit",
                       quality_evidence_location=f"citation_screening_sources/quality_evidence.json#{rid}")
        elif row["screening_status"] == "keep":
            row["round2_status"] = "deferred"
            row["shortlist_reason"] = deferred.get(rid,
                "第一轮主题相关，但本轮未排入有限精读预算；优先同主题的代表贡献。未作无贡献判断。")
            row["quality_review_scope"] = "selected_body_sections" if rid in deferred else "round1_title_abstract_only"
            if rid in evidence:
                row["institution_source_url"] = evidence[rid]["source_url"]
                row["quality_evidence_location"] = f"citation_screening_sources/quality_evidence.json#{rid}"
        else:
            row["round2_status"] = "round1_pending" if row["screening_status"] == "pending" else "round1_excluded"
            row["shortlist_reason"] = row["decision_reason"]
            row["quality_review_scope"] = "round1_title_abstract_only"
    write_csv(TABLE, rows, fields)
    write_csv(DOCS / "citation_screening_retained.csv", [r for r in rows if r["screening_status"] == "keep"], fields)
    shortlisted = [by_id[f"PV-C{d[0]:03d}"] for d in decisions]
    group_by_id = {f"PV-C{d[0]:03d}": d[2] for d in decisions}
    for row in shortlisted:
        row["shortlist_group"] = group_by_id[row["record_id"]]
    compact_fields = ["record_id", "shortlist_tier", "shortlist_group", "title", "authors", "year", "arxiv_id", "paper_url",
                      "verified_affiliations", "venue", "venue_verification", "venue_source_url", "institution_source_url",
                      "main_contribution", "limitation_or_reading_caution", "citation_source", "citation_relation_status",
                      "quality_review_scope", "quality_evidence_location"]
    write_csv(DOCS / "citation_screening_shortlist.csv", shortlisted, compact_fields)
    audit_fields = ["record_id", "title", "paper_url", "screening_status", "round2_status", "shortlist_tier", "shortlist_reason", "quality_review_scope"]
    write_csv(DOCS / "citation_screening_round2_audit.csv", rows, audit_fields)
    main_count = sum(r["venue_verification"] == "official_proceedings" for r in shortlisted)
    counts = Counter(group_by_id[r["record_id"]] for r in shortlisted)
    lines = ["# Persona Vectors：高价值精选阅读", "", "更新：2026-10-30。第二轮已将351篇主题相关记录压缩为30篇主阅读清单：A档10篇先读，B档20篇按方向读。", "",
             "[精选CSV](citation_screening_shortlist.csv) · [完整工作表](citation_screening_working.csv) · [第二轮全部去向](citation_screening_round2_audit.csv) · [规则基准](citation_screening_rules.md) · [第一轮宽口径导航](citation_screening_reading_map.md)", "",
             "## 这轮怎样筛", "",
             "第一轮把“相关”当成了保留条件，不能直接当精读推荐。这轮优先具体的新问题、新机制、重要反例和可复用的研究范式，并用署名机构、公司参与及会议作辅助信号。纯应用迁移、外围综述和相近方法框架优先延后。即使来自名校或已中顶会，也不自动入选。", "",
             f"- 所有30篇仍来自原文的376条直接被引快照，没有主题搜索补入其他论文。",
             f"- 对43篇候选核查官方HTML署名及贡献／讨论／局限片段；不是43篇全文方法审计。30篇入选，13篇重点候选延后，其余308篇第一轮保留记录未进一步作贡献高低定论。",
             f"- 精选中{main_count}篇已由官方会议录核实主会。其他按公司报告、作者自报、workshop记录或未核实标注；未把在审或workshop写成顶会主会。",
             "- persona命中仍留在总清单，不能自动进入精选。未入选不等于已证明无贡献。",
             "- 排名和入选判断属于本轮编辑判断；“限制／阅读提醒”可能是作者明确局限，也可能是据证据范围提出的核对点，不是论文质量评分。", "",
             "## 先读这10篇", "", "按下列顺序形成问题地图，再决定深入哪个方向；不需要一次读完后面的20篇。", "",
             "| 顺序 | 论文 | 机构／发表信号 | 为什么先读 |", "|---|---|---|---|"]
    a_rows = [r for r in shortlisted if r["shortlist_tier"] == "A"]
    for index, row in enumerate(a_rows, 1):
        venue = f"[{safe(row['venue'])}]({row['venue_source_url']})" if row["venue_source_url"] else safe(row["venue"])
        institution = f"[{safe(row['verified_affiliations'])}]({row['institution_source_url']})"
        lines.append(f"| {index} | [{safe(row['title'])}]({row['paper_url']})（{row['record_id']}） | {institution}；{venue} | {safe(row['main_contribution'])} |")
    lines += ["", "## 按方向读精选30篇", "", "A/B不是质量等级：A适合先建立问题地图，B适合进入专题后再读。", ""]
    for group, question in GROUPS:
        lines += [f"### {group}（{counts[group]}篇）", "", question, "",
                  "| 论文 | 机构／发表 | 独立贡献 | 限制／阅读提醒 |", "|---|---|---|---|"]
        for row in shortlisted:
            if group_by_id[row["record_id"]] != group:
                continue
            venue = f"[{safe(row['venue'])}]({row['venue_source_url']})" if row["venue_source_url"] else safe(row["venue"])
            institution = f"[{safe(row['verified_affiliations'])}]({row['institution_source_url']})"
            lines.append(f"| **{row['shortlist_tier']}** [{safe(row['title'])}]({row['paper_url']})（{row['record_id']}） | {institution}；{venue} | {safe(row['main_contribution'])} | {safe(row['limitation_or_reading_caution'])} |")
        lines.append("")
    lines += ["## 重点核查后仍延后的13篇", "", "这些不是低贡献黑名单。列出取舍是为了减少重复阅读，并说明学校／公司／会议没有替代贡献和主题判断。", "",
              "| 论文 | 本轮取舍 |", "|---|---|"]
    for rid, reason in deferred.items():
        row = by_id[rid]
        lines.append(f"| [{safe(row['title'])}]({row['paper_url']})（{rid}） | {safe(reason)} |")
    lines += ["", "## 核查范围与文件", "",
              "署名机构来自对应论文HTML首页，避免由作者履历猜本篇机构；公司Fellows Program与公司署名分别标明。主会来源采用ICLR Proceedings、PMLR和ACL Anthology。NeurIPS自报、workshop记录没有并入已核实主会计数。",
              "C041与C348的arXiv、会议页面作者／数据表述存在版本差异；原快照不覆盖，阅读时优先确认所用版本。未凭这些差异推断不是同一论文。",
              "精选决策保存于`citation_screening_sources/quality_decisions.json`；正文证据片段保存于`quality_evidence.json`；13篇取舍保存于`quality_pool_deferred.json`。`python scripts/render_persona_quality_shortlist.py`可重建精选及第二轮去向。",
              "当前不把一般预印本写成已接收，也不把未入选写成无贡献。后续全文阅读如果推翻本轮判断，应更新规则和工作文件。"]
    (DOCS / "citation_screening_shortlist.md").write_text("\n".join(lines) + "\n")
    summary = {"source_records": len(rows), "round1_kept": 351, "body_evidence_pool": len(evidence),
               "shortlisted": len(shortlisted), "A": len(a_rows), "B": len(shortlisted)-len(a_rows),
               "official_main_conference_verified": main_count,
               "round2_deferred": sum(r["round2_status"] == "deferred" for r in rows), "groups": dict(counts)}
    (SOURCE / "quality_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
