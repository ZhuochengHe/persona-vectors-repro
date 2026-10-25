import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from persona_repro.common import load_config, question_splits, REPO
from persona_repro.planning import build_plan
from persona_repro.judge import CodexJudge, coherence_rubric


def test_plan_has_selected_matrix_and_no_calibration():
    config=load_config(REPO/'configs/reproduction.json')
    plan=build_plan(config)
    assert len(plan['training_subsets'])==15
    assert plan['judge']['calibration'] is False
    assert sum(row['questions'] for row in plan['extraction_counts'])==30
    assert sum(row['conditions'] for row in plan['extraction_counts'])==180
    assert sum(row['responses'] for row in plan['extraction_counts'])==540
    assert plan['model']['revision']
    assert {e['id'] for e in plan['experiments']}=={'E01','E02','E06','E08','E09','E10','E11','E19'}
    for split in plan['question_splits'].values():
        assert not set(split['dev']) & set(split['test'])
        assert len(split['dev'])==len(split['test'])==10


def test_original_coherence_prompt_is_literal():
    rubric=coherence_rubric(REPO/'upstream')
    assert '{question}' in rubric and '{answer}' in rubric
    assert 'coherence' in rubric


def test_codex_direct_score_caching_without_model_request(tmp_path,monkeypatch):
    import persona_repro.judge as module
    calls=[]
    def run(command,**kwargs):
        calls.append(command)
        output=Path(command[command.index('--output-last-message')+1])
        output.write_text(json.dumps({'score':73,'status':'ok'}))
        assert kwargs['input'].count('test question')==1
        return SimpleNamespace(returncode=0,stderr='')
    monkeypatch.setattr(module.subprocess,'run',run)
    judge=CodexJudge(cache_dir=tmp_path)
    assert judge.score('test question','answer','{question}\n{answer}')['score']==73
    assert judge.score('test question','answer','{question}\n{answer}')['score']==73
    assert len(calls)==1
    assert calls[0][calls[0].index('--model')+1]=='gpt-5.6-luna'


def test_judge_failure_does_not_become_zero(tmp_path,monkeypatch):
    import persona_repro.judge as module
    monkeypatch.setattr(module.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=2,stderr='failed'))
    with pytest.raises(RuntimeError):
        CodexJudge(cache_dir=tmp_path,retries=0).score('q','a','{answer}')
    assert not list(tmp_path.glob('*.json'))


def test_steering_preserves_gradient_and_removes_hook():
    import torch
    from persona_repro.model import Steering
    block=torch.nn.Identity()
    x=torch.ones(1,3,4,requires_grad=True)
    with Steering([block],1,torch.arange(4.),2.,'last'):
        result=block(x)
        assert torch.equal(result[0,:2],x[0,:2])
        assert torch.equal(result[0,-1],x[0,-1]+2*torch.arange(4.))
        result.sum().backward()
    assert torch.equal(x.grad,torch.ones_like(x))
    assert torch.equal(block(x),x)
