"""Retry malformed judge output without imputing scores or altering the rubric."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from persona_repro.judge import CodexJudge


def test_retry_corrects_status_score_format_without_zero_imputation(tmp_path,monkeypatch):
    prompts=[]
    def run(command,**kwargs):
        prompts.append(kwargs['input'])
        output=Path(command[command.index('--output-last-message')+1])
        output.write_text(json.dumps({'status':'refusal','score':0 if len(prompts)==1 else None}))
        return SimpleNamespace(returncode=0,stderr='')
    monkeypatch.setattr('persona_repro.judge.subprocess.run',run)
    monkeypatch.setattr('persona_repro.judge.time.sleep',lambda *args:None)
    judge=CodexJudge(cache_dir=tmp_path,retries=1)
    value=judge.score('q','a','Original rubric: {question} {answer}')
    assert value['status']=='refusal' and value['score'] is None
    assert len(prompts)==2 and prompts[1].startswith(prompts[0])
    assert 'OUTPUT FORMAT CHECK' in prompts[1]
    assert judge.score('q','a','Original rubric: {question} {answer}')==value
    assert len(prompts)==2


def test_repeated_malformed_output_still_fails_closed(tmp_path,monkeypatch):
    def run(command,**kwargs):
        Path(command[command.index('--output-last-message')+1]).write_text(json.dumps({'status':'invalid','score':50}))
        return SimpleNamespace(returncode=0,stderr='')
    monkeypatch.setattr('persona_repro.judge.subprocess.run',run)
    monkeypatch.setattr('persona_repro.judge.time.sleep',lambda *args:None)
    with pytest.raises(RuntimeError,match='Non-numeric status'):
        CodexJudge(cache_dir=tmp_path,retries=1).score('q','a','{question} {answer}')
    assert not list(tmp_path.glob('*.json'))


def batch_fixture(tmp_path, monkeypatch):
    from persona_repro.common import write_jsonl
    monkeypatch.setattr('persona_repro.common.require_compute', lambda: None)
    monkeypatch.setattr('persona_repro.judge.time.sleep', lambda *args: None)
    (tmp_path / 'data_generation/trait_data_eval').mkdir(parents=True)
    (tmp_path / 'data_generation/trait_data_eval/evil.json').write_text(json.dumps({'eval_prompt': '{question} {answer}'}))
    (tmp_path / 'eval').mkdir()
    (tmp_path / 'eval/prompts.py').write_text("Prompts['coherence_0_100'] = '{question} {answer}'\n")
    config={'traits':['evil'],'paths':{'upstream':str(tmp_path),'work':str(tmp_path)},
            'judge':{'model':'gpt-5.6-luna','timeout_seconds':600,'retries':2,
                     'concurrency':1,'failed_item_passes':1,'batch_retry_delay_seconds':0}}
    files=[]
    for i, question in enumerate(['fails-first', 'succeeds']):
        source=tmp_path/f'in{i}.jsonl';target=tmp_path/f'out{i}.jsonl'
        write_jsonl(source,[{'sample_id':str(i),'trait':'evil','question':question,'answer':'answer'}])
        files.append((source,target,('trait',)))
    return config,files


def test_batch_finishes_other_files_before_retrying_failures(tmp_path,monkeypatch):
    from persona_repro.judge import score_files
    config,files=batch_fixture(tmp_path,monkeypatch)
    calls=[]
    def score(self,question,answer,rubric):
        calls.append(question)
        if question=='fails-first' and calls.count(question)==1:
            raise RuntimeError('temporary timeout')
        return {'status':'ok','score':75}
    monkeypatch.setattr(CodexJudge,'score',score)
    score_files(files,config)
    assert calls==['fails-first','succeeds','fails-first']
    assert all(target.exists() for _,target,_ in files)
    assert not list(tmp_path.glob('*.pending.json'))


def test_persistent_failure_keeps_success_and_marks_incomplete(tmp_path,monkeypatch):
    from persona_repro.judge import score_files
    config,files=batch_fixture(tmp_path,monkeypatch)
    def score(self,question,answer,rubric):
        if question=='fails-first':raise RuntimeError('timeout')
        return {'status':'ok','score':75}
    monkeypatch.setattr(CodexJudge,'score',score)
    with pytest.raises(RuntimeError,match='batch incomplete'):
        score_files(files,config)
    assert not files[0][1].exists()
    assert files[1][1].exists()
    pending=json.loads(files[0][1].with_suffix('.pending.json').read_text())
    assert pending['status']=='incomplete' and pending['pending'][0]['sample_id']=='0'


def test_timeout_retries_use_long_backoff(tmp_path,monkeypatch):
    import subprocess
    calls=[];waits=[]
    def run(command,**kwargs):
        calls.append(kwargs['timeout'])
        raise subprocess.TimeoutExpired(command,kwargs['timeout'])
    monkeypatch.setattr('persona_repro.judge.subprocess.run',run)
    monkeypatch.setattr('persona_repro.judge.time.sleep',waits.append)
    monkeypatch.setattr('persona_repro.judge.random.uniform',lambda a,b:0)
    with pytest.raises(RuntimeError,match='after retries'):
        CodexJudge(cache_dir=tmp_path).score('q','a','{question} {answer}')
    assert calls==[600,600,600] and waits==[30,60]
