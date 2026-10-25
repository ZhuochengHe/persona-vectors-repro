"""Paper-rule selection and exact data reuse; no coherence exclusion."""
import json
from pathlib import Path
from copy import deepcopy
from persona_repro.common import REPO,load_config,stable_id,write_jsonl,read_jsonl
from persona_repro.e02 import condition,digest,tasks_for
from persona_repro.e02_paper import select_fixed_alpha,sweep_conditions,reuse_conditions,generate_pending


def test_full_fixed_alpha_budget():
    c=load_config(REPO/'configs/e02-paper.json');cells=sweep_conditions(c)
    assert len(cells)==147
    assert sum(len(tasks_for(c,x['trait'],x['split'])) for x in cells)==2940
    assert set(x['coefficient'] for x in cells)=={0,1,1.5,2}
    assert c['steering']['primary_alpha']==1


def test_selection_uses_trait_mean_not_coherence_or_paired_gain():
    c={'traits':['evil'],'steering':{'coefficients':[1.,1.5,2.],'primary_alpha':1.,'layers':[4,19]}}
    rows=[]
    for a in [1.,1.5,2.]:
        rows.extend([{'trait':'evil','layer':4,'coefficient':a,'trait_mean':10.,'trait_gain':100.,'coherence_mean':90.,'coherence_change':0},
                     {'trait':'evil','layer':19,'coefficient':a,'trait_mean':80.,'trait_gain':5.,'coherence_mean':2.,'coherence_change':-90}])
    result=select_fixed_alpha(rows,c)
    assert result['selected']['evil']['layer']==19
    assert all(s['evil']['layer']==19 for s in result['selected_by_alpha'].values())
    assert len(result['test_conditions'])==4


def test_primary_alpha_is_frozen_even_if_other_alpha_scores_higher():
    c={'traits':['evil'],'steering':{'coefficients':[1.,1.5,2.],'primary_alpha':1.,'layers':[4,8]}}
    rows=[{'trait':'evil','layer':4,'coefficient':1.,'trait_mean':20.},
          {'trait':'evil','layer':8,'coefficient':1.5,'trait_mean':99.},
          {'trait':'evil','layer':8,'coefficient':2.,'trait_mean':90.}]
    selected=select_fixed_alpha(rows,c)
    assert selected['selected']['evil']['layer']==4
    assert selected['selected_by_alpha']['1.5']['evil']['layer']==8


def test_fixed_alpha_ties_lower_layer_and_reports_missing_numeric():
    c={'traits':['evil'],'steering':{'coefficients':[1.,1.5],'primary_alpha':1.,'layers':[4,8]}}
    rows=[{'trait':'evil','layer':8,'coefficient':1.,'trait_mean':20.},
          {'trait':'evil','layer':4,'coefficient':1.,'trait_mean':20.},
          {'trait':'evil','layer':4,'coefficient':1.5,'trait_mean':None}]
    result=select_fixed_alpha(rows,c)
    assert result['selected']['evil']['layer']==4
    assert result['selected_by_alpha']['1.5']['evil'] is None


def test_reuse_preserves_fingerprints_and_does_not_generate_again(tmp_path,monkeypatch):
    import persona_repro.e02_paper as module
    source=tmp_path/'old';run=tmp_path/'new'
    for root in [source,run]:
        for folder in ['responses','scored','vectors']:(root/folder).mkdir(parents=True)
        (root/'vectors/evil.pt').write_bytes(b'fixture-only-hash')
    c=load_config(REPO/'configs/e02-paper.json');c['reuse']={'e02_run':str(source)}
    (source/'config.json').write_text(json.dumps(c))
    cell=condition('evil',4,1)
    fingerprint=stable_id('explicit-generation-v3-turn-end',c['model'],str(None),digest(run/'vectors/evil.pt'),4,1.,c['generation'])
    rows=[dict(r,generation_fingerprint=fingerprint,layer=4,coefficient=1.,checkpoint_id='base',
               model_id=c['model']['id'],model_revision=c['model']['revision']) for r in tasks_for(c,'evil','dev')]
    write_jsonl(source/'responses'/f"{cell['id']}.jsonl",rows)
    calls=[];monkeypatch.setattr(module,'generate_cells',lambda r,c,cells:calls.extend(cells))
    generate_pending(run,c,[cell])
    assert not calls
    assert read_jsonl(run/'responses'/f"{cell['id']}.jsonl")==rows
    assert len(json.loads((run/'reuse/evil.json').read_text()))==1
    # An already-present legacy target must not bypass the reuse guard.
    rows[0]['generation_fingerprint']='legacy-v2'
    write_jsonl(run/'responses'/f"{cell['id']}.jsonl",rows)
    import pytest
    with pytest.raises(ValueError,match='protocol/fingerprint'):
        generate_pending(run,c,[cell])


def test_monitoring_data_reused_when_only_e02_layer_choice_changes(tmp_path):
    from persona_repro.e06_paper import reuse_monitoring
    source=tmp_path/'old06';run=tmp_path/'new06'
    for root in [source,run]:
        for folder in ['responses','scored','projections','vectors']:(root/folder).mkdir(parents=True)
        for trait in ['evil','sycophantic','hallucinating']:
            (root/'vectors'/f'{trait}.pt').write_bytes(b'frozen-unit-and-raw-vector')
    c=load_config(REPO/'configs/e06-paper.json');old=deepcopy(c)
    old['monitoring']['e02_run']='old-layer-choice';c['monitoring']['e02_run']='new-layer-choice'
    c['reuse']={'e06_run':str(source)}
    (source/'config.json').write_text(json.dumps(old))
    for folder in ['responses','scored','projections']:
        write_jsonl(source/folder/'sycophantic.jsonl',[{'fixture':'unchanged-monitoring-data'}])
    reuse_monitoring(run,c)
    for folder in ['responses','scored','projections']:
        assert (source/folder/'sycophantic.jsonl').read_bytes()==(run/folder/'sycophantic.jsonl').read_bytes()
    assert not (run/'responses/evil.jsonl').exists()
