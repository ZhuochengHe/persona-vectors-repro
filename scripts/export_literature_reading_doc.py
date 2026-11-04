"""Render the reading CSV as a readable Markdown mirror and native Docs requests.

Requests initialize a NEW document only. Existing Docs must be read and merged
by stable paper ID before any edit; never replay these requests over user text.
Native table cells and internal heading links require a separate live-structure
pass described in docs/papers/literature_document_maintenance.md.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUPS = [
    ('人格方向从哪里来，如何形成？', [1, 3, 8, 6, 28, 18, 25, 26, 30, 16]),
    ('自报、表征与实际行为是否一致？', [5, 12, 9, 13, 2]),
    ('trait如何组合，为什么相互干扰？', [7, 33, 34, 24, 15]),
    ('如何选择更有效的控制方向与位置？', [10, 17, 20, 21, 22, 23, 27]),
    ('情绪、推理与用户模型怎样影响行为？', [4, 29, 11, 31, 32]),
    ('如何评估审计与交互中的可靠性？', [14, 19]),
    ('当前问题补充：几何、read–write与agent迁移', list(range(35, 44))),
]


def utf16(text):
    return len(text.encode('utf-16-le')) // 2


def index_rows(rows):
    layout = json.loads((ROOT / 'docs/papers/citation_screening_sources/reading_doc_layout.json').read_text())
    return [['ID', '论文短标题', '类型', '阅读状态']] + [
        [r['ID'], layout['short_titles'].get(str(r['ID']), r['Title']), r['Paper type'], r['Read status']]
        for r in sorted(rows, key=lambda r: int(r['ID']))
    ]


def render(rows):
    by_id = {int(row['ID']): row for row in rows}
    grouped = [i for _, ids in GROUPS for i in ids]
    if len(set(grouped)) != len(grouped):
        raise ValueError('Duplicate IDs in reading groups')
    groups = [(title, [i for i in ids if i in by_id]) for title, ids in GROUPS]
    extra = sorted(set(by_id) - set(grouped))
    if extra:
        groups.append(('后续新增论文', extra))
    paragraphs = []

    def add(text, style='NORMAL_TEXT', bold=False, link=None):
        paragraphs.append((text, style, bold, link))

    add('Persona 文献阅读笔记', 'TITLE')
    add('研究问题导航 · 稳定论文 ID · 方法、证据与个人思考', 'SUBTITLE')
    add('阅读导航', 'HEADING_1')
    add('按左侧大纲进入研究问题，再按 ID 找论文。每篇先看 Research question 与一句话主题，需要时展开方法、贡献和局限；用户的 Additional think 单独保留。')
    add('分类按主要贡献，可多选：Method＝提出控制／训练／提取方法；Benchmark＝提出评估任务、数据或协议；Survey＝系统综述已有研究；Analysis＝通过实证研究刻画规律；Theory＝包含正式数学命题与证明。公式、线性代数或几何分析本身不构成 Theory。')
    add('分类与研究问题是基于当前阅读证据整理的工作标签。短笔记保持原有阅读深度；未核实正式证明的条目暂不标 Theory，当前收录也不强求包含 Survey。')
    for title, ids in groups:
        add(title + '｜' + '、'.join(f'ID {i}' for i in ids))
    add('按论文类型查找', 'HEADING_2')
    for category in ('Method', 'Benchmark', 'Survey', 'Analysis', 'Theory'):
        ids = [i for i, r in sorted(by_id.items()) if category in r['Paper type'].split('; ')]
        add(category + '：' + ('、'.join(f'ID {i}' for i in ids) if ids else '当前未标注符合此类的条目'))
    for title, ids in groups:
        if not ids:
            continue
        add(title, 'HEADING_1')
        for i in ids:
            r = by_id[i]
            add(f'ID {i}｜{r["Title"]}', 'HEADING_2')
            add(f'{r["Paper type"]}　|　阅读状态：{r["Read status"]}　|　优先级：{r["Priority"]}')
            add('论文原文', link=r['Link'])
            add('Research question', bold=True)
            add(r['Research question'])
            add('一句话主题', bold=True)
            add(r['One sentence/topic'])
            for label, key in [('方法与贡献', 'Contributions'), ('局限与解释边界', 'Limitation'), ('Future work', 'Future work'), ('Additional think｜用户笔记', 'Additional think')]:
                add(label, bold=True)
                text = r.get(key, '')
                if text:
                    for line in text.splitlines():
                        if line.strip():
                            add(line)
                else:
                    add('（留空，供用户填写）' if key == 'Additional think' else '（尚未整理）')
            add('关联论文：' + r['Related paper'])
            add('关键词：' + r['Key words'])
            add('机构／会议：' + r['Institution / Venue'])
            add('阅读证据：' + r['Evidence scope'])
    text = ''.join(t + '\n' for t, *_ in paragraphs)
    requests = [{'insertText': {'location': {'index': 1}, 'text': text}}]
    requests.append({'updateParagraphStyle': {'range': {'startIndex': 1, 'endIndex': 1 + utf16(text)}, 'paragraphStyle': {'spaceBelow': {'magnitude': 6, 'unit': 'PT'}}, 'fields': 'spaceBelow'}})
    index = 1
    markdown = []
    font_requests = []
    for text_part, style, bold, link in paragraphs:
        end = index + utf16(text_part)
        rng = {'startIndex': index, 'endIndex': end}
        if style != 'NORMAL_TEXT':
            requests.append({'updateParagraphStyle': {'range': rng, 'paragraphStyle': {'namedStyleType': style}, 'fields': 'namedStyleType'}})
            size = {'TITLE': 22, 'SUBTITLE': 13, 'HEADING_1': 18, 'HEADING_2': 16}[style]
            font_requests.append({'updateTextStyle': {'range': rng, 'textStyle': {'fontSize': {'magnitude': size, 'unit': 'PT'}}, 'fields': 'fontSize'}})
        elif bold:
            requests.append({'updateTextStyle': {'range': rng, 'textStyle': {'bold': True}, 'fields': 'bold'}})
        elif link:
            requests.append({'updateTextStyle': {'range': rng, 'textStyle': {'link': {'url': link}}, 'fields': 'link'}})
        prefix = {'TITLE': '# ', 'SUBTITLE': '', 'HEADING_1': '## ', 'HEADING_2': '### '}.get(style, '')
        md = f'[{text_part}]({link})' if link else (f'**{text_part}**' if bold else prefix + text_part)
        if style == 'HEADING_2' and text_part.startswith('ID '):
            identifier = text_part.split('｜', 1)[0].split()[1]
            md = f'<a id="paper-{identifier}"></a>\n\n' + md
        markdown.append(md)
        if text_part.startswith('阅读证据：'):
            markdown.append('[返回论文总表](#论文总表)')
        index = end + 1
    md_text = '\n\n'.join(markdown) + '\n'
    grid = index_rows(rows)
    table = ['## 论文总表', '', '点击 ID 进入笔记，点击短标题打开原文；表格用于浏览，复杂筛选使用 Excel。', '',
             '| ID | 论文短标题 | 类型 | 阅读状态 |', '| --- | --- | --- | --- |']
    for identifier, short_title, category, status in grid[1:]:
        row = by_id[int(identifier)]
        table.append(f'| [{identifier}](#paper-{identifier}) | [{short_title}]({row["Link"]}) | {category} | {status} |')
    first_group = next(title for title, ids in groups if ids)
    marker = '## ' + first_group + '\n'
    md_text = md_text.replace(marker, '\n'.join(table) + '\n\n' + marker, 1)
    return md_text, requests + font_requests, text


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/papers/literature_reading.md')
    parser.add_argument('--requests-output', type=Path)
    args = parser.parse_args()
    with (ROOT / 'docs/papers/literature_reading.csv').open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    markdown, requests, text = render(rows)
    args.output.write_text(markdown)
    if args.requests_output:
        args.requests_output.write_text(json.dumps({'requests': requests, 'expected_text': text, 'index_rows': index_rows(rows), 'native_index_pass_required': True}, ensure_ascii=False))
    print(f'Rendered {len(rows)} papers, {utf16(text)} UTF-16 units, {len(requests)} native requests.')
