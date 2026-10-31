"""Synchronize run references from registered stable study documents only."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'docs/research/run_registry.json'
RUN_ID = re.compile(r'\b[a-z0-9][a-z0-9-]*-20\d{6}-\d{6}\b')


def synchronized(registry):
    result = dict(registry)
    runs = {}
    ids, paths = set(), set()
    archives = {item['item']: item for item in registry['archives']}
    for study in registry['studies']:
        if study['id'] in ids or study['record'] in paths:
            raise ValueError('Study IDs and canonical records must be unique')
        if re.match(r'(?:\d|latest\b|final\b)', Path(study['record']).name, re.I):
            raise ValueError('Use a stable semantic study filename, not a counter/date/status')
        ids.add(study['id']);paths.add(study['record'])
        record = ROOT / study['record']
        if record.is_symlink() or not record.is_file():
            raise ValueError(f'Expected a canonical regular study document: {record}')
        for run_id in sorted(set(RUN_ID.findall(record.read_text()))):
            entry = runs.setdefault(run_id, {
                'local_path_template': '${PV_WORK}/runs/' + run_id,
                'referenced_by_studies': [],
                'drive_archive': archives.get(run_id),
            })
            entry['referenced_by_studies'].append(study['id'])
    for topic in {study['topic'] for study in registry['studies']}:
        for record in (ROOT / 'docs/research' / topic / 'studies').glob('*.md'):
            if str(record.relative_to(ROOT)) not in paths:
                raise ValueError(f'Unregistered study; reuse an existing study or register its question: {record}')
    for record in (ROOT / 'experiment_records').glob('*.md'):
        if not record.is_symlink() and record.name != 'README.md':
            raise ValueError(f'New record in compatibility directory is forbidden: {record}')
    for old, destination in registry.get('compatibility_paths', {}).items():
        path = ROOT / old
        if old == 'experiment_records/README.md':
            continue
        if not path.is_symlink() or path.resolve() != (ROOT / destination).resolve():
            raise ValueError(f'Compatibility path no longer points to its canonical document: {old}')
    result['runs'] = dict(sorted(runs.items()))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate without writing')
    args = parser.parse_args()
    current = json.loads(REGISTRY.read_text())
    updated = synchronized(current)
    if args.check:
        if updated != current:
            raise SystemExit('Run registry is stale; run scripts/sync_research_registry.py')
    else:
        REGISTRY.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + '\n')
    print(f"{len(updated['studies'])} studies, {len(updated['runs'])} referenced runs, "
          f"{len(updated['archives'])} confirmed archive entries")


if __name__ == '__main__':
    main()
