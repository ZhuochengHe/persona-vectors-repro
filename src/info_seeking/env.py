"""Native re-implementation of the HiL-Bench SQL tool environment.

Semantics follow the official files pinned in official.py:
- schema tools: SWE-agent tool scripts (printed Python dict or error string);
- execute_sql: Harbor sql_server (read-only, 200-row CSV, subprocess timeout);
- get_business_info: business_info_server (all-MiniLM-L6-v2, top 5, filtered by database name);
- ask_human: ask-human server (judge + per-blocker cap), delegated to a simulator object.
Deviations are recorded in the study document.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from .official import CANT_ANSWER, IRRELEVANT_QUESTION, MAX_ANSWERED_QUESTIONS_PER_BLOCKER

# Subprocess workers import this very copy of the package (repo src or a run's frozen source).
WORKER_ENV = {**os.environ, 'PYTHONPATH': str(Path(__file__).resolve().parents[1])}


class MiniLMRetriever:
    """sentence-transformers/all-MiniLM-L6-v2 = BERT mean pooling + L2 normalisation, max 256 tokens.

    Chroma's default L2 space on normalised vectors ranks identically to cosine similarity; with
    about 30 documents per task the exact search reproduces Chroma's HNSW top 5.
    """
    MODEL_ID = 'sentence-transformers/all-MiniLM-L6-v2'

    def __init__(self, revision: str | None = None, max_length: int = 256):
        from transformers import AutoModel, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_ID, revision=revision)
        self.model = AutoModel.from_pretrained(self.MODEL_ID, revision=revision).eval()
        self.max_length = max_length
        self._cache: dict[tuple, Any] = {}

    def embed(self, texts: list[str]):
        import torch
        batch = self.tokenizer(texts, padding=True, truncation=True, max_length=self.max_length, return_tensors='pt')
        with torch.inference_mode():
            hidden = self.model(**batch).last_hidden_state
        mask = batch['attention_mask'].unsqueeze(-1).float()
        pooled = (hidden * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
        return torch.nn.functional.normalize(pooled, dim=-1)

    def search(self, documents: list[str], query: str, n_results: int = 5) -> list[str]:
        key = tuple(documents)
        if key not in self._cache:
            self._cache = {key: self.embed(documents)}
        scores = self._cache[key] @ self.embed([query])[0]
        order = scores.argsort(descending=True)[:n_results].tolist()
        return [documents[i] for i in order]


class SQLTaskEnv:
    def __init__(self, task: dict, *, ask_enabled: bool, simulator=None, retriever: MiniLMRetriever,
                 sql_timeout_seconds: float, external_root: str, verify_timeout_seconds: float = 600):
        self.task, self.ask_enabled = task, ask_enabled
        self.simulator, self.retriever = simulator, retriever
        self.sql_timeout = sql_timeout_seconds
        self.verify_timeout = verify_timeout_seconds
        self.external_root = external_root
        self.descriptions = Path(task['descriptions_dir'])
        self.questions: list[dict] = []
        self.submission: str | None = None
        if ask_enabled and simulator is None:
            raise ValueError('ask_human requires a simulator')

    # Schema tools (SWE-agent scripts print the returned dict or error string).
    def get_database_info(self, database_name: str) -> str:
        import pandas as pd
        try:
            df = pd.read_csv(self.descriptions / 'table_descriptions.csv')
            return str(dict(zip(df['table_name'], df['table_description'])))
        except FileNotFoundError:
            return f"Error: database {database_name} doesn't exist"

    def get_table_info(self, database_name: str, table_name: str) -> str:
        import pandas as pd
        table_lowered = table_name.lower()
        error_msg = f"Error: table {table_name} in database {database_name} doesn't exist"
        info = {}
        try:
            df = pd.read_csv(self.descriptions / 'table_descriptions.csv')
            df_slice = df[df['table_name'] == table_name]
            if len(df_slice) == 0:
                df_slice = df[df['table_name'] == table_lowered]
            info['description'] = df_slice.iloc[0]['table_description']
        except (FileNotFoundError, IndexError):
            return error_msg
        try:
            df = pd.read_csv(self.descriptions / f'{table_lowered}.csv')
        except FileNotFoundError:
            return error_msg
        info['columns'] = df['original_column_name'].tolist()
        return str(info)

    def get_column_info(self, database_name: str, table_name: str, column_name: str) -> str:
        import pandas as pd
        table_lowered, column_lowered = table_name.lower(), column_name.lower()
        error_msg = f"Error: column {column_name} in table {table_name} in database {database_name} doesn't exist"
        try:
            df = pd.read_csv(self.descriptions / f'{table_lowered}.csv')
        except FileNotFoundError:
            return error_msg
        try:
            df_slice = df[df['original_column_name'] == column_name]
            if len(df_slice) == 0:
                df_slice = df[df['original_column_name'] == column_lowered]
            row = df_slice.iloc[0]
        except IndexError:
            return error_msg
        return str({'description': row['combined_description'], 'data_type': row.get('data_format', '')})

    def get_business_info(self, database_name: str, search_string: str) -> str:
        if not database_name:
            return 'Error querying knowledge base: Missing database_name'
        if not search_string:
            return 'Error querying knowledge base: Missing search_string'
        docs = []
        if database_name == self.task['database_name']:
            docs = self.retriever.search(self.task['business_info'], search_string, 5)
        if not docs:
            return f"No business information found matching '{search_string}'."
        return '\n'.join(f'{i + 1}. {doc.strip()}' for i, doc in enumerate(docs))

    def execute_sql(self, query: str) -> str:
        try:
            completed = subprocess.run([sys.executable, '-m', 'info_seeking.sql_worker', self.task['database_path']],
                                       input=query, capture_output=True, text=True, timeout=self.sql_timeout,
                                       check=False, env=WORKER_ENV)
        except subprocess.TimeoutExpired:
            return f'Error: query timed out after {self.sql_timeout:g} seconds'
        except Exception as e:
            return f'Error launching query worker: {e}'
        if completed.returncode != 0 and ('ModuleNotFoundError' in completed.stderr or 'ImportError' in completed.stderr):
            # Harness failure, not a query outcome: never show it to the model as an observation.
            raise RuntimeError(f'SQL worker import failure: {completed.stderr[-500:]}')
        if completed.returncode != 0:
            detail = completed.stderr.strip() or f'worker exited with status {completed.returncode}'
            return f'Error executing query: {detail}'
        return completed.stdout

    def submit_sql(self, query: str) -> str:
        self.submission = query
        return f'Submission received:\n{query}'

    def ask_human(self, question: str) -> str:
        """Official ask-human server logic; the simulator only classifies the question."""
        if not self.task['blockers']:
            return self._log(question, CANT_ANSWER, None, None, 'no_registry')
        if not question or not question.strip() or len(question.strip()) < 3:
            return self._log(question, IRRELEVANT_QUESTION, None, None, 'too_short')
        verdict = self.simulator.classify(self.task['blockers'], question.strip())
        if verdict['status'] != 'ok':
            return self._log(question, CANT_ANSWER, None, None, verdict['status'], verdict)
        registry = {b['id']: b for b in self.task['blockers']}
        # A key outside the registry is a non-match in the official server (and not "relevant").
        key = verdict['blocker_key'] if verdict['blocker_key'] in registry else None
        if key is not None:
            prior = sum(1 for q in self.questions if q['blocker_name'] == key)
            if prior >= MAX_ANSWERED_QUESTIONS_PER_BLOCKER:
                return self._log(question, IRRELEVANT_QUESTION, None, key, 'capped', verdict)
            return self._log(question, registry[key]['resolution'], key, key, 'matched', verdict)
        return self._log(question, IRRELEVANT_QUESTION, None, None, 'unmatched', verdict)

    def _log(self, question, response, blocker_name, judged_key, outcome, verdict=None) -> str:
        self.questions.append({'question': question, 'response': response, 'blocker_name': blocker_name,
                               'judged_blocker_key': judged_key, 'outcome': outcome,
                               'judge': {k: v for k, v in (verdict or {}).items() if k != 'blocker_key'}})
        return response

    def call(self, name: str, arguments: dict) -> str:
        handlers = {'execute_sql': self.execute_sql, 'get_database_info': self.get_database_info,
                    'get_table_info': self.get_table_info, 'get_column_info': self.get_column_info,
                    'get_business_info': self.get_business_info, 'submit_sql': self.submit_sql}
        if self.ask_enabled:
            handlers['ask_human'] = self.ask_human
        return handlers[name](**arguments)

    def verify(self) -> dict:
        if self.submission is None:
            return {'solve': 0, 'submitted': False}
        with tempfile.TemporaryDirectory() as work:
            sub, gt = Path(work) / 'submission.sql', Path(work) / 'ground_truth.sql'
            sub.write_text(self.submission.strip())
            gt.write_text(self.task['ground_truth_sql'].strip())
            try:
                completed = subprocess.run(
                    [sys.executable, '-m', 'info_seeking.sql_worker', '--verify', self.external_root,
                     self.task['database_path'], str(sub), str(gt)],
                    capture_output=True, text=True, timeout=self.verify_timeout, check=True, env=WORKER_ENV)
                result = json.loads(completed.stdout.strip().splitlines()[-1])
            except subprocess.TimeoutExpired:
                result = {'solve': 0, 'verify_error': 'timeout'}
            except (subprocess.CalledProcessError, json.JSONDecodeError, IndexError) as e:
                result = {'solve': 0, 'verify_error': f'{type(e).__name__}: {getattr(e, "stderr", "")[-500:]}'}
        result['submitted'] = True
        return result

    def ask_metrics(self) -> dict:
        """Both precision definitions: harness (unique resolved / questions) and paper (|Q_rel| / |Q|)."""
        n_questions = len(self.questions)
        n_blockers = len(self.task['blockers'])
        resolved = {q['blocker_name'] for q in self.questions if q['blocker_name'] is not None}
        relevant = sum(1 for q in self.questions if q['judged_blocker_key'] is not None)
        recall = len(resolved) / n_blockers if n_blockers else 0.0

        def f1(p, r):
            return 2 * p * r / (p + r) if p + r > 0 else 0.0
        p_harness = len(resolved) / n_questions if n_questions else 0.0
        p_paper = relevant / n_questions if n_questions else 0.0
        return {'n_questions': n_questions, 'n_blockers': n_blockers, 'blockers_resolved': len(resolved),
                'n_relevant': relevant,
                'recall': recall, 'precision_harness': p_harness, 'f1_harness': f1(p_harness, recall),
                'precision_paper': p_paper, 'f1_paper': f1(p_paper, recall),
                'n_judge_failures': sum(1 for q in self.questions if q['response'] == CANT_ANSWER),
                'n_judge_parse_failed': sum(1 for q in self.questions if q['outcome'] == 'parse_failed'),
                'n_judge_transport_failed': sum(1 for q in self.questions if q['outcome'] == 'judge_failed'),
                'n_capped': sum(1 for q in self.questions if q['outcome'] == 'capped')}
