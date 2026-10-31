"""Regression checks for E01 settings and audits; no model or network calls."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from persona_repro.common import REPO, load_config, read_jsonl, write_jsonl, generation_fingerprint
from persona_repro.extraction import audit_pairs
from persona_repro.inference_tasks import build_extraction_tasks

FILTER = {'filter_mode': 'paired_repo', 'threshold': 50, 'coherence_threshold': 50}


def pair(index=0, positive=50, negative=49, **overrides):
    result=[]
    for side,score in [('pos',positive),('neg',negative)]:
        row={'sample_id':f'{index}:{side}', 'pair_id':f'pair:{index}', 'trait':'evil',
             'question_id':index, 'instruction_id':0, 'rollout':0, 'polarity':side,
             'messages':[{'role':'user','content':'question'}],
             'prompt_token_ids':[10], 'answer_token_ids':[3 if side=='pos' else 1],
             'model_id':'Qwen/Qwen3.5-4B',
             'model_revision':'851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a',
             'checkpoint_id':'base','coefficient':0.0,'truncated':False,
             'generation_fingerprint':generation_fingerprint(load_config(REPO/'configs/reproduction.json')),
             'scores':{'evil':{'status':'ok','score':score},'coherence':{'status':'ok','score':50}}}
        row.update(overrides)
        result.append(row)
    return result


def test_question_count_is_distinct_from_conditions_and_rollouts():
    tasks=build_extraction_tasks(REPO/'upstream','evil',1)
    assert len(tasks)==200
    assert len({row['question_id'] for row in tasks})==20
    assert len(build_extraction_tasks(REPO/'upstream','evil',10))==2000


def test_paired_thresholds_coverage_and_truncation():
    rows=pair(0)+pair(1,negative=50)
    rows[0]['truncated']=True
    accepted,audit=audit_pairs(rows,FILTER)
    assert len(accepted)==2
    assert audit['total_pairs']==2 and audit['retained_pairs']==1
    assert audit['rejection_counts']=={'neg_trait_threshold':1}
    assert audit['coverage']['question_id']['1']['retained_pairs']==0
    assert audit['truncation']['pos']['fraction']==0.5
    assert audit['decisions'][1]['retained'] is False


def test_non_numeric_score_excludes_whole_pair_without_zero_imputation():
    rows=pair()
    rows[0]['scores']['evil']={'status':'refusal','score':None}
    accepted,audit=audit_pairs(rows,FILTER)
    assert not accepted
    assert audit['status']=='no_valid_pairs'
    assert audit['decisions'][0]['scores']['pos']['trait'] is None


def test_bad_pair_and_fake_filter_mode_fail():
    rows=pair()
    rows[1]['question_id']=7
    with pytest.raises(ValueError,match='question_id'):
        audit_pairs(rows,FILTER)
    with pytest.raises(ValueError,match='paired_repo'):
        audit_pairs(pair(),dict(FILTER,filter_mode='independent'))


def test_numeric_nan_is_not_silently_accepted():
    rows=pair()
    rows[0]['scores']['evil']['score']=float('nan')
    with pytest.raises(ValueError,match='numeric'):
        audit_pairs(rows,FILTER)


@pytest.mark.parametrize('layers,hidden_size', [(32,2560), (28,3584)])
def test_vector_output_includes_audit_and_provenance(tmp_path,monkeypatch,layers,hidden_size):
    import torch
    import persona_repro.operations as module
    class FakeRuntime:
        def encode_conversation(self,messages):return {'input_ids':[10]}
        def activations(self,messages,**kwargs):
            value=float(kwargs['answer_token_ids'][0])
            return {layer:{'response_avg':torch.full((hidden_size,),value)} for layer in range(1,layers+1)}
    monkeypatch.setattr(module,'require_compute',lambda:None)
    monkeypatch.setattr(module,'runtime_from_config',lambda config:FakeRuntime())
    scored=tmp_path/'scored.jsonl'
    target=tmp_path/'evil.pt'
    config=load_config(REPO/'configs/reproduction.json')
    config['model'].update(expected_layers=layers,expected_hidden_size=hidden_size)
    if layers == 28:
        config['model'].update(id='Qwen/Qwen2.5-7B-Instruct',revision='a09a35458c702b33eeacc393d103063234e8bc28')
    overrides = {'generation_fingerprint': generation_fingerprint(config),
                 'model_id': config['model']['id'], 'model_revision': config['model']['revision']}
    write_jsonl(scored,pair(**overrides)+pair(1,positive=0,**overrides))
    module.extract_vectors(scored,target,config)
    # The cluster's lightweight test interpreter has old Torch. This fixture
    # was just created here; production loading still requires weights_only.
    import inspect
    options={'weights_only':True} if 'weights_only' in inspect.signature(torch.load).parameters else {}
    vectors=torch.load(target,**options)
    assert vectors['raw'].shape==(layers,hidden_size)
    assert torch.equal(vectors['raw'],torch.full((layers,hidden_size),2.0))
    assert torch.allclose(vectors['unit'].norm(dim=-1),torch.ones(layers))
    audit=json.loads(target.with_suffix('.audit.json').read_text())
    assert audit['retained_pairs']==1 and len(audit['decisions'])==2
    metadata=json.loads(target.with_suffix('.json').read_text())
    assert len(metadata['asset_sha256'])==len(metadata['scored_input_sha256'])==64
    assert len(metadata['raw_vector_norms'])==layers


def test_no_retained_pairs_writes_audit_without_loading_model(tmp_path,monkeypatch):
    import persona_repro.operations as module
    monkeypatch.setattr(module,'require_compute',lambda:None)
    def forbidden(_):
        pytest.fail('A model must not load when the fixed filter rejects all pairs')
    monkeypatch.setattr(module,'runtime_from_config',forbidden)
    scored=tmp_path/'scored.jsonl'
    write_jsonl(scored,pair(positive=0))
    target=tmp_path/'evil.pt'
    with pytest.raises(ValueError,match='No positive'):
        module.extract_vectors(scored,target,load_config(REPO/'configs/reproduction.json'))
    assert not target.exists()
    assert json.loads(target.with_suffix('.audit.json').read_text())['status']=='no_valid_pairs'


def test_explicit_generation_does_not_inherit_sampling_defaults(monkeypatch):
    import torch
    import sys
    # Test our protocol without installing/downloading the model environment.
    class GenerationConfig:
        def __init__(self,**kwargs): self.__dict__.update(kwargs)
        def to_dict(self): return dict(self.__dict__)
    monkeypatch.setitem(sys.modules,'transformers',SimpleNamespace(
        GenerationConfig=GenerationConfig,set_seed=lambda seed:None))
    from persona_repro.model import ModelRuntime
    class FakeTokenizer:
        pad_token_id=0
        bos_token_id=1
        eos_token_id=2
        def decode(self,ids,**kwargs): return 'hello'
    class FakeModel:
        device='cpu'
        generation_config=GenerationConfig(top_k=1,top_p=0.1,repetition_penalty=2.,num_beams=4,eos_token_id=[2,3])
        def generate(self,**kwargs):
            config=kwargs['generation_config']
            assert config.top_k==0 and config.top_p==1.
            assert config.num_beams==1 and config.repetition_penalty==1.
            assert config.min_new_tokens==1
            return torch.tensor([[10,11,3]])
    runtime=ModelRuntime('fake')
    runtime.model=FakeModel();runtime.tokenizer=FakeTokenizer()
    runtime.encode_conversation=lambda messages:{'input_ids':[10],'response_start':1}
    output=runtime.generate([],max_new_tokens=2)
    assert output['finish_reason']=='eos' and output['truncated'] is False
    assert output['effective_generation_config']['top_k']==0
    assert output['seed']==0


def test_generate_file_passes_full_settings_and_wraps_seed(tmp_path,monkeypatch):
    import persona_repro.operations as module
    config=load_config(REPO/'configs/reproduction.json')
    config['generation']['seed']=2**32-1
    seen=[]
    class FakeRuntime:
        def generate(self,messages,**kwargs):
            seen.append(kwargs)
            return {'answer':'text','prompt_token_ids':[1],'answer_token_ids':[2],'truncated':False}
    monkeypatch.setattr(module,'require_compute',lambda:None)
    monkeypatch.setattr(module,'runtime_from_config',lambda *a:FakeRuntime())
    source=tmp_path/'tasks.jsonl';out=tmp_path/'results.jsonl'
    write_jsonl(source,[{'sample_id':'test','messages':[{'role':'user','content':'q'}]}])
    module.generate_file(source,out,config)
    assert 0<=seen[0]['seed']<2**32
    assert seen[0]['top_k']==0 and seen[0]['min_new_tokens']==1
    module.generate_file(source,out,config)
    assert len(seen)==1
    assert len(read_jsonl(out))==1


def test_selected_e01_questions_instructions_and_repeats():
    config=load_config(REPO/'configs/reproduction.json')
    settings=config['extraction']
    for trait in config['traits']:
        tasks=build_extraction_tasks(REPO/'upstream',trait,settings['rollouts'],question_ids=settings['question_ids'],instruction_ids=settings['instruction_ids'])
        assert len(tasks)==180
        assert {row['question_id'] for row in tasks}==set(range(10))
        assert {row['instruction_id'] for row in tasks}=={0,1,2}
        assert {row['rollout'] for row in tasks}=={0,1,2}
        assert len({row['pair_id'] for row in tasks})==90
    # This change applies only to E01, not the other experiments' rollouts.
    assert config['generation']['rollouts']==10


def test_extraction_subset_keeps_source_ids_and_rejects_bad_selection():
    tasks=build_extraction_tasks(REPO/'upstream','evil',1,question_ids=[3,7],instruction_ids=[2])
    assert {row['question_id'] for row in tasks}=={3,7}
    assert len(tasks)==4
    with pytest.raises(ValueError):
        build_extraction_tasks(REPO/'upstream','evil',1,question_ids=[0,0])
    with pytest.raises(ValueError):
        build_extraction_tasks(REPO/'upstream','evil',1,instruction_ids=[9])
