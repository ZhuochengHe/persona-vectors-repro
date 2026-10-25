# Persona Vectors Reproduction

Repository map for the Qwen3.5-4B reproduction of [Persona Vectors](https://arxiv.org/abs/2507.21509).

## Start here

| Location | Contents |
|---|---|
| [experiment_records/](experiment_records/README.md) | Chinese experiment notes: settings, findings, run IDs, Google Drive file IDs, and archive links. |
| [docs/experiments/RUNBOOK.md](docs/experiments/RUNBOOK.md) | Environment setup and stage-by-stage execution commands. |
| [docs/experiments.md](docs/experiments.md) | Experiment status and historical submissions. |
| [docs/experiments/strategies/](docs/experiments/strategies/) | Protocols for E01, E02, E06, E08, E09, E10, E11, and E19. |
| [docs/plans/](docs/plans/) | Paper experiment inventory and adaptation plans. |
| [docs/ARCHIVE.md](docs/ARCHIVE.md) | Archive scope, exclusions, and checksum files. |
| [Google Drive archives](https://drive.google.com/drive/folders/1Y9fgfox6sSKq2qOig1c53hWE8oMZIZuZ) | Experiment ZIPs, generated answers, scores, vectors, frozen configurations, source snapshots, and logs. |

## Source: `src/persona_repro/`

| File | Purpose |
|---|---|
| [cli.py](src/persona_repro/cli.py) | Command-line entry points. |
| [pipeline.py](src/persona_repro/pipeline.py) | E01 stage orchestration. |
| [common.py](src/persona_repro/common.py) | Configuration, paths, JSON I/O, fingerprints, and compute-node checks. |
| [model.py](src/persona_repro/model.py) | Model loading, generation, activation capture, and steering hooks. |
| [operations.py](src/persona_repro/operations.py) | Shared generation, extraction, and projection operations. |
| [inference_tasks.py](src/persona_repro/inference_tasks.py) | Extraction and evaluation task builders. |
| [extraction.py](src/persona_repro/extraction.py) | Positive/negative pair filtering. |
| [judge.py](src/persona_repro/judge.py) | Luna scoring, cache, retries, and original rubrics. |
| [e02.py](src/persona_repro/e02.py) | Steering conditions, paired summaries, and shared validation. |
| [e02_paper.py](src/persona_repro/e02_paper.py) | Historical fixed-alpha layer selection. |
| [e02_coherent.py](src/persona_repro/e02_coherent.py) | Joint layer/alpha selection with coherence thresholds. |
| [e06.py](src/persona_repro/e06.py) | Prompt-projection monitoring. |
| [e06_paper.py](src/persona_repro/e06_paper.py) | Monitoring under the historical E02 layer selections. |
| [training.py](src/persona_repro/training.py) | LoRA training, response masks, and training-time interventions. |
| [data.py](src/persona_repro/data.py) | Training-data subsets and splits. |
| [data_inventory.py](src/persona_repro/data_inventory.py) | Downloaded-data checks and token-length summaries. |
| [setup.py](src/persona_repro/setup.py) | Pinned upstream dataset download. |
| [mmlu.py](src/persona_repro/mmlu.py) | MMLU preparation and evaluation. |
| [analysis.py](src/persona_repro/analysis.py) | Correlations and experiment analyses. |
| [reporting.py](src/persona_repro/reporting.py) | Result tables and reports. |
| [planning.py](src/persona_repro/planning.py) | Experiment execution plans. |
| [preflight.py](src/persona_repro/preflight.py) | Model and training preflight checks. |
| [__init__.py](src/persona_repro/__init__.py) | Package initialization. |

## Scripts: `scripts/`

| Files | Purpose |
|---|---|
| `submit.sh`, `run.slurm`, `bootstrap.sh`, `checks.slurm` | Persistent-log submission, generic CLI stages, environment setup, and tests. |
| `e01_stage.slurm` | E01 generation, scoring, and extraction stages. |
| `e02_stage.slurm`, `e02_paper_stage.slurm`, `e02_coherent.slurm` | E02 execution for the successive selection protocols. |
| `e06_stage.slurm`, `e06_paper_stage.slurm` | E06 monitoring stages. |
| `e08_train.slurm`, `e08_matrix.slurm`, `prepare_e08_matrix.py` | Individual and matrix LoRA training. |
| `preflight_training.py`, `training_preflight.slurm` | Real-model training preflight. |
| `steering_followups.py`, `steering_followups.slurm` | Prompt-position controls and fresh sycophantic extraction. |
| `random_direction_control.py`, `random_direction_control.slurm` | Norm-matched random-direction controls. |
| `vector_boundary_test.py`, `vector_boundary.slurm` | Controlled response-boundary extraction experiment. |
| `measure_perturbation.py` | Vector norms relative to unsteered activations. |
| `check_runtime_interactions.py` | Upstream-hook and cached/replayed inference comparisons. |
| `benchmark_kernels.py`, `accelerate.slurm` | Kernel and inference performance checks. |

Slurm files are Great Lakes templates. Storage paths are configured through `PV_ROOT` and `PV_WORK`; see the runbook before submitting jobs.

## Configurations, assets, and tests

| Location | Contents |
|---|---|
| [configs/reproduction.json](configs/reproduction.json) | Shared model, generation, judge, data, and training settings. |
| `configs/e02.json`, `configs/e02-paper.json` | Historical E02 sweep configurations. |
| `configs/e06.json`, `configs/e06-paper.json` | E06 monitoring configurations. |
| `configs/pilot.json`, `configs/natural.json` | Pilot and natural-response settings. |
| [assets/monitoring_prompts.json](assets/monitoring_prompts.json) | Original monitoring prompts. |
| [assets/execution_plan.json](assets/execution_plan.json) | Initial planning snapshot. |
| [tests/](tests/) | Tests for data, templates, extraction, steering, judging, selection, monitoring, and training. |
| [pyproject.toml](pyproject.toml) | Package metadata and dependency groups. |

## Upstream and licensing

[upstream/](upstream/) is the original authors' Git submodule, pinned at `b8e0f044fe2410a6fad579f38324f03f13b4e917`. Initialize it with `git submodule update --init`. Paper links are in [docs/papers/README.md](docs/papers/README.md).

See [LICENSE](LICENSE) and [NOTICE](NOTICE) for licensing and attribution. Model weights, adapters, caches, and generated experiment artifacts are kept outside Git.
