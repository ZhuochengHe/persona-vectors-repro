"""E06 budget, no future-response access, refusal handling and dependency guards."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from persona_repro.common import REPO, load_config, write_jsonl
from persona_repro.e06 import tasks_for, merge_rows, analyze_trait, selected_layers


def test_e06_budget_and_common_random_numbers():
    config=load_config(REPO/'configs/e06.json')
    total=0
    for trait in config['traits']:
        tasks=tasks_for(config,trait);total+=len(tasks)
        assert len(tasks)==224
        assert len({(r['prompt_id'],r['question_id']) for r in tasks})==56
        assert len({r['sampling_seed_id'] for r in tasks})==28
        assert len({r['sample_id'] for r in tasks})==224
    assert total==672


def test_e06_does_not_start_with_missing_e02_completion_marker(tmp_path):
    config={'monitoring':{'e02_run':str(tmp_path),'e02_final_job':'123'}}
    with pytest.raises(ValueError,match='not completed'):
        selected_layers(tmp_path,config)


def test_e06_skips_missing_settings_and_freezes_selection(tmp_path):
    parent=tmp_path/'parent';parent.mkdir();(parent/'logs').mkdir()
    (parent/'logs/test-score_123.done.json').write_text(json.dumps({'status':'complete'}))
    selection={'selected':{'evil':None,'sycophantic':{'layer':20},'hallucinating':{'layer':16}}}
    (parent/'selection.json').write_text(json.dumps(selection));(parent/'heldout-summary.json').write_text('{}')
    config={'traits':['evil','sycophantic','hallucinating'],'monitoring':{'e02_run':str(parent),'e02_final_job':'123'}}
    result=selected_layers(tmp_path,config)
    assert result['layers']=={'sycophantic':20,'hallucinating':16}
    assert 'evil' in result['skipped']
    selection['selected']['sycophantic']['layer']=19
    (parent/'selection.json').write_text(json.dumps(selection))
    with pytest.raises(ValueError,match='changed'):
        selected_layers(tmp_path,config)


def example_rows():
    rows=[];projections={}
    for prompt in ['low','high']:
        for q in range(3):
            p={'prompt_token_ids':[1,q+2],'messages':[{'role':'user','content':f'{prompt}{q}'}],
               'vector_id':'hash','projection_model_id':'Qwen','projection_revision':'rev',
               'projection_checkpoint_id':'base','projection_mode':'prompt_last',
               'all_layer_projections':[float(q+(10 if prompt=='high' else 0))]*32}
            projections[prompt,q]=p
            for rollout in range(4):
                rows.append({'sample_id':f'{prompt}{q}r{rollout}','trait':'evil','prompt_id':prompt,'question_id':q,
                    'prompt_token_ids':p['prompt_token_ids'],'messages':p['messages'],
                    'checkpoint_id':'base','layer':None,'coefficient':0,'truncated':False,
                    'scores':{'evil':{'status':'ok','score':float(q*10+(50 if prompt=='high' else 0))}}})
    return rows,projections


def test_e06_rollouts_averaged_and_refusals_counted():
    rows,p=example_rows();rows[0]['scores']['evil']={'status':'refusal','score':None}
    result,merged=analyze_trait(rows,p,16,'evil')
    assert result['excluded_non_numeric']==1
    assert result['score_status_counts']=={'refusal':1,'ok':23}
    assert len(result['condition_question_means'])==6
    assert result['trait_reports'][0]['rollout_count']==23
    assert merged[0]['steering_layer'] is None and merged[0]['layer']==16
    assert len(result['overall_question_bootstrap_95'])==2


def test_e06_rejects_projection_generation_template_mismatch():
    rows,p=example_rows();rows[0]['prompt_token_ids']=[999]
    with pytest.raises(ValueError,match='tokenized prompts'):
        merge_rows(rows,p,16)


def test_e06_only_requests_target_trait_scores(tmp_path,monkeypatch):
    import persona_repro.judge as module
    config=load_config(REPO/'configs/e06.json');config['paths']['work']=str(tmp_path)
    calls=[]
    class FakeJudge:
        def __init__(self,*args):pass
        def score(self,q,a,rubric):
            calls.append(rubric);return {'status':'ok','score':42}
    monkeypatch.setattr('persona_repro.common.require_compute',lambda:None)
    monkeypatch.setattr(module,'CodexJudge',FakeJudge)
    source=tmp_path/'input.jsonl';output=tmp_path/'output.jsonl'
    write_jsonl(source,[{'trait':'evil','question':'q','answer':'a'}])
    module.score_file(source,output,config,metrics=('trait',))
    assert len(calls)==1 and set(json.loads(output.read_text())['scores'])=={'evil'}


def test_e06_projection_is_prompt_only_and_reused_across_rollouts(tmp_path):
    import torch
    from persona_repro.e06 import prompt_projections
    config=load_config(REPO/'configs/e06.json');config['monitoring']['question_ids']['evil']=[1]
    (tmp_path/'vectors').mkdir()
    torch.save({'raw':torch.ones(32,2560),'unit':torch.ones(32,2560)/(2560**.5)},tmp_path/'vectors/evil.pt')
    class Runtime:
        calls=0
        def load(self):return self
        def encode_conversation(self,messages):return {'input_ids':[1,len(messages[0]['content'])]}
        def activations(self,messages):
            self.calls+=1
            return {l:{'prompt_last':torch.ones(2560)*l,'response_avg':None} for l in range(1,33)}
    runtime=Runtime()
    p=prompt_projections(tmp_path,config,'evil',runtime)
    assert len(p)==8 and runtime.calls==8
    assert all(len(r['all_layer_projections'])==32 for r in p.values())
    prompt_projections(tmp_path,config,'evil',runtime)
    assert runtime.calls==8
