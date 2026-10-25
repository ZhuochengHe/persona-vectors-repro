"""Explicit data download into large-file storage, with fixed upstream revision."""
from __future__ import annotations
import hashlib
from pathlib import Path
import urllib.request
import zipfile
from .common import require_compute, write_json

UPSTREAM_REVISION='b8e0f044fe2410a6fad579f38324f03f13b4e917'


def fetch_data(config, output: Path):
    require_compute()
    output = output.resolve()
    if output.is_relative_to(Path.home().resolve()):
        raise ValueError('Large training data must not be downloaded into home')
    output.mkdir(parents=True,exist_ok=True)
    archive = output/'dataset.zip'
    if not archive.exists():
        url=f'https://raw.githubusercontent.com/safety-research/persona_vectors/{UPSTREAM_REVISION}/dataset.zip'
        temporary = archive.with_suffix('.partial')
        urllib.request.urlretrieve(url,temporary)
        temporary.replace(archive)
    allowed={f'dataset/{category}/{version}.jsonl' for category in config['data']['categories'] for version in ('normal','misaligned_1','misaligned_2')}
    with zipfile.ZipFile(archive) as source:
        if not allowed.issubset(source.namelist()):
            raise ValueError('Archive is missing requested datasets')
        for name in sorted(allowed):
            source.extract(name,output)  # Names come from explicit whitelist; never extract arbitrary members.
    write_json(output/'download.manifest.json',{'upstream_revision':UPSTREAM_REVISION,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':sorted(allowed)})
