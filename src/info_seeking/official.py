"""Load pinned official HiL-Bench files without copying them into this repository.

The upstream repository has no top-level license, so its files stay in the external
checkout under PV_WORK and are verified by SHA-256 before use. The ask-human judge
prompt is reconstructed from the official server source by AST parsing (no code from
that file is executed). The SQL verifier module is imported only after its hash matches.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any

# Paths are relative to the configured external root (see configs/info-seeking-hil-sql.json).
PINNED_FILES = {
    'ask_human_server': ('ask-human-image/x/app/server.py',
                         '69550ae022dd4d7e5d7e9d1925949de4d91ab31c510bd5170deba2965f22ddef'),
    'sql_server': ('main-image/x/opt/hil-bench/sql_server.py',
                   '73bfc2a802504188c2e989b36132afbf061e77f3233f2549d154d12a7ca2f856'),
    'business_info_server': ('main-image/x/opt/hil-bench/business_info_server.py',
                             'df302b8682d99bdb6b5a303542cd1030bc0280fc268865747e8fc55ce3b60a72'),
    'full_info_template': ('hil-bench/hil_bench/templates/problem_full_info.jinja2',
                           '8d4c65d598dcf834378f8f1a1b3521e3334f0f7062cb66213b71408b6e836490'),
    'ask_config': ('hil-bench/configs/sql/ask_sql_config_qwen3_30b_a3b_instruct_2507.yaml',
                   '482b82a10d2a85bc36e72e5b88e0568cddd74177358b30efea2a18b11618869b'),
    'test_verify': ('hil-bench/harbor_sql/hil-bench-sql_1-ask_human/tests/test_verify.py',
                    '5ea34491ed83d552d53a7d1c136ba166cf13774f2363015cd134610949f2f9ae'),
    'dataset': ('hil-bench-data/train.parquet',
                '260c245ba012b95cac3d63eb58222f79350fb43037b1f1ce9e3b40819d2a789c'),
}
TOOL_CONFIG_SHA256 = {
    'execute_sql': 'fd9dcda25352dbebeab4ad379ca80132124c1455c8685ee033696efab77ceeec',
    'get_database_info': '1524f0a73d7f8e2212742a53c3a0b0363a41f331d6f712692f4dbde8dfb88a59',
    'get_table_info': '99e91b353a03390ff29ca1ab9cac124a6b23628fcd049c95eb1bb35f6082ab93',
    'get_column_info': '56d15ae652df5f682634e463339e31e81ddff39e26a2dd103bd39216868eb37e',
    'get_business_info': '9aa6260beb5f4666763f4e62a1ff8edd577889fce1cc32d5051fbd40c5ee8541',
    'ask_human': 'f3abc697fe47d61882abe5d9a0d9eb00e2dca9d32d57f483a7039c6bd24a9eb3',
    'submit_sql': '4be864d5f18bd0cde8e207de3dafc391993c99ebb7d155e86f229a220fbd330c',
}
TOOL_CONFIGS = tuple(TOOL_CONFIG_SHA256)
HIL_REPO_COMMIT = 'c5a656e41b5c50917686f9df8e4c72152bf27ba9'

# Official strings (ask-human server.py and sql_server.py); checked against the source in tests.
CANT_ANSWER = "can't answer (perhaps transient hiccup)"
IRRELEVANT_QUESTION = 'irrelevant question'
MAX_ANSWERED_QUESTIONS_PER_BLOCKER = 2
# The paragraph that distinguishes the official ask config from a no-ask prompt.
ASK_PARAGRAPH = ('A human analyst is available via the ask_human tool. You can ask the analyst about '
                 'details that are not clear from the question or the business info. Each question '
                 'should be about one specific ambiguity.\n\n')


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _fstring_to_template(node: ast.JoinedStr) -> list[tuple[str, str]]:
    """Return [('text', literal) | ('expr', source)] parts of an f-string node."""
    parts = []
    for value in node.values:
        if isinstance(value, ast.Constant):
            parts.append(('text', value.value))
        elif isinstance(value, ast.FormattedValue):
            if value.conversion != -1 or value.format_spec is not None:
                raise ValueError('Unexpected f-string formatting in judge prompt')
            parts.append(('expr', ast.unparse(value.value)))
        else:
            raise ValueError('Unexpected f-string node')
    return parts


@dataclass(frozen=True)
class JudgePromptTemplate:
    blocker_parts: list[tuple[str, str]]
    prompt_parts: list[tuple[str, str]]

    def render(self, blockers: list[dict], agent_question: str) -> str:
        """Same output as official create_evaluation_prompt for this registry and question."""
        blocks = []
        for blocker in blockers:
            values = {'key': blocker['id'], 'blocker.description': blocker['description'],
                      "', '.join(blocker.example_questions)": ', '.join(blocker.get('example_questions') or [])}
            blocks.append(self._fill(self.blocker_parts, values))
        values = {'chr(10).join(blockers_info)': chr(10).join(blocks), 'agent_question': agent_question}
        return self._fill(self.prompt_parts, values)

    @staticmethod
    def _fill(parts, values):
        out = []
        for kind, value in parts:
            if kind == 'text':
                out.append(value)
            else:
                if value not in values:
                    raise KeyError(f'Unsupported judge prompt expression: {value}')
                out.append(str(values[value]))
        return ''.join(out)


def parse_judge_prompt(server_source: str) -> JudgePromptTemplate:
    tree = ast.parse(server_source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'create_evaluation_prompt':
            appended = [n for n in ast.walk(node) if isinstance(n, ast.Call)
                        and isinstance(n.func, ast.Attribute) and n.func.attr == 'append'
                        and n.args and isinstance(n.args[0], ast.JoinedStr)]
            returns = [n for n in ast.walk(node) if isinstance(n, ast.Return) and isinstance(n.value, ast.JoinedStr)]
            if len(appended) != 1 or len(returns) != 1:
                raise ValueError('Unexpected create_evaluation_prompt structure')
            return JudgePromptTemplate(_fstring_to_template(appended[0].args[0]),
                                       _fstring_to_template(returns[0].value))
    raise ValueError('create_evaluation_prompt not found')


class OfficialFiles:
    def __init__(self, external_root: str | Path):
        self.root = Path(external_root)

    def path(self, name: str) -> Path:
        relative, expected = PINNED_FILES[name]
        path = self.root / relative
        actual = sha256(path)
        if actual != expected:
            raise ValueError(f'Pinned official file changed: {path} sha256={actual}, expected {expected}')
        return path

    def tool_config_path(self, tool: str) -> Path:
        path = self.root / 'hil-bench/SWE-agent/tools' / tool / 'config.yaml'
        actual = sha256(path)
        if actual != TOOL_CONFIG_SHA256[tool]:
            raise ValueError(f'Pinned tool config changed: {path} sha256={actual}')
        return path

    def hashes(self) -> dict[str, Any]:
        result = {name: {'path': rel, 'sha256': sha256(self.root / rel)} for name, (rel, _) in PINNED_FILES.items()}
        for tool in TOOL_CONFIGS:
            path = self.tool_config_path(tool)
            result[f'tool:{tool}'] = {'path': str(path.relative_to(self.root)), 'sha256': sha256(path)}
        result['hil_repo_commit'] = HIL_REPO_COMMIT
        return result

    @cached_property
    def judge_prompt(self) -> JudgePromptTemplate:
        return parse_judge_prompt(self.path('ask_human_server').read_text())

    @cached_property
    def verifier(self):
        """Official compare_pandas_outputs; module import has no side effects (main is guarded)."""
        spec = importlib.util.spec_from_file_location('hil_official_test_verify', self.path('test_verify'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @cached_property
    def ask_config(self) -> dict:
        import yaml
        return yaml.safe_load(self.path('ask_config').read_text())

    def system_prompt(self, ask_enabled: bool) -> str:
        template = self.ask_config['agent']['templates']['system_template']
        if ask_enabled:
            return template
        if ASK_PARAGRAPH not in template:
            raise ValueError('Official ask paragraph not found; cannot build matched no-ask prompt')
        return template.replace(ASK_PARAGRAPH, '', 1)

    def instance_message(self, database_name: str, problem_statement: str) -> str:
        template = self.ask_config['agent']['templates']['instance_template']
        expected = "Please answer the following question about the '{{database_name}}' database: {{problem_statement}}"
        if template != expected:
            raise ValueError('Unexpected instance template')
        return f"Please answer the following question about the '{database_name}' database: {problem_statement}"

    @property
    def observation_templates(self) -> tuple[str, str]:
        templates = self.ask_config['agent']['templates']
        return templates['next_step_template'], templates['next_step_no_output_template']

    @property
    def format_error_template(self) -> str:
        return self.ask_config['agent']['tools']['parse_function']['error_message']

    def render_full_info(self, problem_statement: str, blockers: list[dict]) -> str:
        from jinja2 import Environment, FileSystemLoader, StrictUndefined
        path = self.path('full_info_template')
        env = Environment(loader=FileSystemLoader(path.parent), undefined=StrictUndefined)
        return env.get_template(path.name).render(problem_statement=problem_statement, blockers=blockers)

    def tool_schemas(self, ask_enabled: bool) -> list[dict]:
        """Function-calling schemas in the same form SWE-agent builds from the tool configs."""
        import yaml
        tools = []
        for name in TOOL_CONFIGS:
            if name == 'ask_human' and not ask_enabled:
                continue
            spec = yaml.safe_load(self.tool_config_path(name).read_text())['tools'][name]
            properties = {arg['name']: {'type': arg['type'], 'description': arg['description']}
                          for arg in spec.get('arguments', [])}
            required = [arg['name'] for arg in spec.get('arguments', []) if arg.get('required')]
            tools.append({'type': 'function', 'function': {
                'name': name, 'description': spec['docstring'],
                'parameters': {'type': 'object', 'properties': properties, 'required': required}}})
        return tools

    def end_names(self) -> dict[str, str]:
        """Heredoc terminators (e.g. ENDOFSQL) that SWE-agent strips from multi-line arguments."""
        import yaml
        result = {}
        for name in TOOL_CONFIGS:
            spec = yaml.safe_load(self.tool_config_path(name).read_text())['tools'][name]
            if spec.get('end_name'):
                result[name] = spec['end_name']
        return result
