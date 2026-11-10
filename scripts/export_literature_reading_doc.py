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
    ('Where do persona directions come from, and how do they form?', [1, 3, 8, 6, 28, 18, 25, 26, 30, 16]),
    ('Do self-reports, representations, and actual behavior agree?', [5, 12, 9, 13, 2]),
    ('How do traits combine, and why do they interfere?', [7, 33, 34, 24, 15]),
    ('How should more effective control directions and intervention sites be selected?', [10, 17, 20, 21, 22, 23, 27, 47]),
    ('How do emotion, reasoning, and user models affect behavior?', [4, 29, 11, 31, 32]),
    ('How can reliability in audits and interactions be evaluated?', [14, 19]),
    ('Current-question supplements: Geometry, read–write, and agent transfer', list(range(35, 44)) + [48]),
    ('Safety evaluation, model defaults, and multimodal subspaces', [44, 45, 46]),
]


def utf16(text):
    return len(text.encode('utf-16-le')) // 2


def architecture_label(row):
    # Compact labels are reviewed separately: keyword matching prose can mistake
    # "not MoE" or "text-only on a VLM" for a positive experimental category.
    layout = json.loads((ROOT / 'docs/papers/citation_screening_sources/reading_doc_layout.json').read_text())
    return layout.get('architecture_labels', {}).get(str(row['ID']), 'Unverified')


def index_rows(rows):
    layout = json.loads((ROOT / 'docs/papers/citation_screening_sources/reading_doc_layout.json').read_text())
    return [['ID', 'Short title', 'Type', 'Architecture', 'Status', 'Task', 'Major finding (abstract)', 'Benchmark / Validation']] + [
        [r['ID'], layout['short_titles'].get(str(r['ID']), r['Title']), r['Paper type'], architecture_label(r), r['Read status'], r.get('Task', ''), r.get('Major finding', ''), r.get('Validation', '')]
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
        groups.append(('Newly added papers', extra))
    paragraphs = []

    def add(text, style='NORMAL_TEXT', bold=False, link=None):
        paragraphs.append((text, style, bold, link))

    add('Persona Literature Notes', 'TITLE')
    add('Research-question navigation · Stable paper IDs · Methods, evidence, and personal notes', 'SUBTITLE')
    add('Reading guide', 'HEADING_1')
    add('Use the document outline to select a research question, then locate a paper by ID. Start with its research question and one-sentence topic, then read the methods, contributions, and limitations as needed. Additional think is reserved for the user.')
    add('Classify by contribution; multiple labels are allowed: Method introduces a control, training, or extraction method; Benchmark introduces evaluation tasks, data, or protocols; Survey systematically reviews prior work; Analysis characterizes empirical patterns; Theory contains formal mathematical statements and proofs. Equations, linear algebra, or geometric analysis alone do not qualify as Theory.')
    add('Paper types and research questions are working labels based on the available reading evidence. Short notes retain their original depth. Do not label an item Theory without verified formal proofs; the collection need not contain a Survey.')
    for title, ids in groups:
        add(title + ' | ' + ', '.join(f'ID {i}' for i in ids))
    add('Browse by architecture: representative papers', 'HEADING_2')
    add('Distinguish backbone capabilities from experimental inputs. See each paper’s Models and architecture section for model roles, actual thinking mode, and exact checkpoints.')
    architecture_nav = [
        ('Common dense-decoder baselines', [1, 2, 3, 7, 33, 34, 45]),
        ('MoE / hybrid-attention evidence (distinguish probing and steering)', [5, 9, 11, 13, 26, 27, 30, 44]),
        ('VLMs tested with image and text inputs', [46]),
        ('Vision-capable backbones tested only on text', [6, 9, 12, 18, 30, 34, 35, 44]),
        ('Non-Transformer intervention controls', [10]),
        ('Closed-weight / API subjects', [4, 38, 41]),
    ]
    for label, ids in architecture_nav:
        present = [i for i in ids if i in by_id]
        if present:
            add(label + ': ' + ', '.join(f'ID {i}' for i in present))
    add('Browse by paper type', 'HEADING_2')
    for category in ('Method', 'Benchmark', 'Survey', 'Analysis', 'Theory'):
        ids = [i for i, r in sorted(by_id.items()) if category in r['Paper type'].split('; ')]
        add(category + ': ' + (', '.join(f'ID {i}' for i in ids) if ids else 'No items currently labeled in this category'))
    for title, ids in groups:
        if not ids:
            continue
        add(title, 'HEADING_1')
        for i in ids:
            r = by_id[i]
            add(f'ID {i}｜{r["Title"]}', 'HEADING_2')
            add(f'{r["Paper type"]}　|　Reading status: {r["Read status"]}　|　Priority: {r["Priority"]}')
            add('Paper', link=r['Link'])
            add('Models and architecture', bold=True)
            add('Models studied: ' + (r.get('Models studied') or 'Unverified'))
            add('Architecture: ' + (r.get('Architecture') or 'Unverified'))
            add('Input / inference mode: ' + (r.get('Inference mode') or 'Not reported / unverified'))
            add('Architecture evidence: ' + (r.get('Architecture evidence') or 'Model settings not yet verified'))
            add('Research question', bold=True)
            add(r['Research question'])
            add('One-sentence topic', bold=True)
            add(r['One sentence/topic'])
            for label, key in [('Methods and contributions', 'Contributions'), ('Limitations and interpretation boundaries', 'Limitation'), ('Future work', 'Future work'), ('Additional think | User notes', 'Additional think')]:
                add(label, bold=True)
                text = r.get(key, '')
                if text:
                    for line in text.splitlines():
                        if line.strip():
                            add(line)
                else:
                    add('(Reserved for user notes)' if key == 'Additional think' else '(Not yet summarized)')
            add('Related papers: ' + r['Related paper'])
            add('Keywords: ' + r['Key words'])
            add('Institution / venue: ' + r['Institution / Venue'])
            add('Reading evidence: ' + r['Evidence scope'])
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
            identifier = text_part.split(' | ', 1)[0].split()[1]
            md = f'<a id="paper-{identifier}"></a>\n\n' + md
        markdown.append(md)
        if text_part.startswith('Reading evidence: '):
            markdown.append('[Return to paper index](#paper-index)')
        index = end + 1
    # User notes can contain tables imported from native Docs cells. Keep
    # adjacent pipe rows together so the local mirror preserves their columns.
    md_text = ''.join(
        ('\n' if i and part.startswith('|') and markdown[i - 1].startswith('|') else '\n\n') + part
        for i, part in enumerate(markdown)
    ).lstrip('\n') + '\n'
    grid = index_rows(rows)
    table = ['## Paper index', '', 'Click an ID for notes or a short title for the paper. Major finding summarizes the abstract; Validation lists tasks and key conditions. Use Excel for detailed filtering.', '',
             '| ' + ' | '.join(grid[0]) + ' |', '| ' + ' | '.join(['---'] * len(grid[0])) + ' |']
    for identifier, short_title, category, architecture, status, task, finding, validation in grid[1:]:
        row = by_id[int(identifier)]
        cells = [f'[{identifier}](#paper-{identifier})', f'[{short_title}]({row["Link"]})', category, architecture, status, task, finding, validation]
        table.append('| ' + ' | '.join(c.replace('|', '\\|').replace('\n', '<br>') for c in cells) + ' |')
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
