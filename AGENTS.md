# Agent guide

## Read by research question, not by date

Start at [docs/research/index.md](docs/research/index.md). Current documentation
belongs to three stable research lines:

| Research line | High-level analysis | Protocol and evidence |
|---|---|---|
| Original Persona Vectors reproduction | [Overview](docs/research/persona-vectors/overview.md) | [Protocol](docs/research/persona-vectors/protocol.md), protocols/ and studies/ in that directory |
| Steering × decoding | [Overview](docs/research/steering-decoding/overview.md) | studies/: sampler ablation, model/layer transfer, token distributions, fresh-question validation |
| Gaming Figure 3 | [Overview](docs/research/gaming/overview.md) | [Protocol](docs/research/gaming/protocol.md), [single study record](docs/research/gaming/studies/altruism-figure3.md) |

The root [README](README.md) maps code. [Papers](docs/papers/README.md) and the
[citation reading map](docs/papers/citation_screening_reading_map.md) are the
literature entry points. Shared instructions: [runbook](docs/research/runbook.md)
and [archive guide](docs/research/archive.md).

## Literature workflow: working sources and Windows reading workbook

- For a literature-only handoff, start at
  `docs/papers/handover_paper_excel.md`; this task does not depend on a separate
  pending reorganization of experiment documentation.
- Maintain collection, citation provenance, screening decisions, and export code
  in this repository under `docs/papers/` and `scripts/`. In a WSL session,
  perform the working analysis there; do not turn the Windows folder into a
  second raw-data or screening workspace.
- The user's high-level literature workbook belongs at
  `/mnt/d/umich/research/persona/persona_literature.xlsx` in WSL, corresponding
  to `D:\umich\research\persona\persona_literature.xlsx` in Windows.
- Check the actual host and availability of the target directory before
  delivery. Great Lakes does not automatically mount the user's Windows drive.
  Never create a substitute `/mnt/d` tree on HPC or claim that a repository
  copy was delivered to Windows. If the destination is unavailable, prepare a
  small staging workbook in `docs/papers/`, report that delivery is pending,
  and use an explicitly available WSL session or connection for the final copy.
- The workbook is the user's high-level reading view. Include the selected
  literature plus the two foundation papers: original Persona Vectors and
  Persona Vectors in Games. Keep a stable numeric ID for each paper so
  `Related paper` can refer to IDs even after sorting or adding papers.
- Required columns: `Title`, `Link`, `Key words`, `One sentence/topic`,
  `Contributions`, `Limitation`, `Additional think`, and `Related paper`.
  Useful additional columns are ID, research direction, priority,
  institution/venue, read status, and evidence scope. Do not add DOI columns.
- Fill at least title, link, keywords, and one-sentence topic for every paper.
  Keep English paper titles and use concise Chinese synthesis. Separate
  abstract-based notes from selected-body review and complete full-text review;
  do not invent contributions, affiliations, acceptance, or limitations.
- `Additional think` belongs exclusively to the user: initialize it blank and
  never generate or overwrite its contents. Preserve existing reading status
  and other manual edits on later updates. Merge by stable paper ID/source key,
  not by row number. Add new rows rather than regenerating over user notes.
- Use a filterable Excel table, frozen headers/identifier columns, wrapped
  text, working hyperlinks, and a short guide explaining IDs and update rules.
  Read any existing destination workbook before updating it; back it up before
  replacement, and stop cleanly if Excel has locked it.
- Export/update with `scripts/export_literature_workbook.py`; its stable IDs,
  keywords, topics, and related-paper IDs live in
  `docs/papers/citation_screening_sources/workbook_catalog.json`.
  A ready-to-open Git handoff copy is `docs/papers/persona_literature.xlsx`.
- Current selection criteria live in
  `docs/papers/citation_screening_rules.md`; current high-value reading view
  is `docs/papers/citation_screening_shortlist.md`. The broad citation CSV stays
  as provenance, not the default Windows reading workload.

## One study document per research question

- Update the existing study for retries, recovery, progress, extra seeds,
  coefficients/layers, model controls, and follow-up results. Add a run row or
  evidence section; **do not create another numbered or dated note**.
- A new study requires a distinct research question/control objective. Register
  its stable semantic ID and canonical path in
  [run_registry.json](docs/research/run_registry.json) before submission. No
  counter/date/latest/final/v2 filenames. No standalone batch summaries, repair
  logs, review reports, or diaries unless explicitly requested by the user.
- `<topic>/overview.md` owns hypotheses, evidence links, alternative explanations,
  and next discriminating tests. `<topic>/studies/<name>.md` owns exact settings,
  controls, run IDs, result tables, limitations, and reproduction commands.
  Do not maintain the same result table or live status in multiple documents.
- Keep raw runs separate and immutable. Consolidating documents must not merge
  data with different vectors, models, samplers, or EOS protocols.
- `experiment_records/` and old docs/ideas, docs/plans, and experiment entry
  points are compatibility paths only. Do not create new files there. Symlinks
  preserve frozen jobs' output paths; do not remove them while old jobs may
  write. Only canonical study files contain the actual record bodies.
- After editing studies, run `python scripts/sync_research_registry.py`; use
  `--check` to validate. Confirmed Drive IDs live in registry `archives`; add
  actual IDs after uploads, never invent or reuse IDs. Preserve existing unique
  report markers and do not schedule concurrent writers to one document.
- Root README remains English and navigational; research notes use Chinese.
  Do not rewrite another agent's unrelated work or the literature collection.

## Git and experiment lifecycle

Follow [CONTRIBUTING.md](CONTRIBUTING.md). Commit validated reusable workflow
improvements separately from new experiment setup and harvested results. Use
explicit staging paths; do not bundle unrelated pending work. Small experiments
may add a descriptive config/runner and update an existing study. Shared-method
changes or parallel alternatives use branches/worktrees from a committed base;
a worktree does not inherit dirty files or isolate Python dependencies.

New expensive runs must record the implementation commit plus frozen source,
config, and task hashes. Never label an old dirty snapshot as a clean-commit run.
Keep active experiments' paths and inputs stable; defer further document/data
reorganization and its coherent commit until active writers finish. Serialize
canonical study updates across worktrees. Do not create a worktree for every run.

## Locate actual data

- `PV_ROOT`: `/home/jonzhe/persona_vectors`.
- Current `PV_WORK`:
  `/scratch/qdj_project_owned_root/qdj_project_owned1/jonzhe/persona_vectors`.
- Resolve study ID → registry/record → exact `${PV_WORK}/runs/<run_id>/`.
  Never search all runs/shared storage. Current pointer names include
  `active_sampling_validation.txt`, `active_gaming_figure3.txt`, and
  `active_token_distribution_diagnostic.txt`, all under PV_WORK. Pointers
  identify runs, not completion state.
- Runs contain frozen config.json, manifest.json, source/, tasks/, jobs.json,
  logs/, and stage outputs. Records specify paths under extraction/, scan/,
  positions/, pilot/, evaluation/, or the run root.
- Frozen settings outrank current templates. Summaries, row/scoring counts,
  and job/completion state outrank old pending prose. Generation, scoring,
  analysis, and Drive upload are different completion states.
- Scratch is purged after inactivity, not permanent archival storage. Run IDs,
  Slurm IDs, and Drive IDs differ. A registry reference is provenance, not
  necessarily ownership by the citing study.

## Scientific and HPC constraints

- Inspect settings before expensive runs. Select layers/alphas on development
  data, then freeze them before confirmation. Never silently relax thresholds
  or fall back to another layer when no candidate qualifies.
- Record model revision, vector hash, 1-based block index, hook positions, EOS,
  sampler, seed, judge, and sample counts. Raw vectors steer; unit directions
  project. Alpha values are not comparable across vector scales.
- Established judge: Luna direct scoring, no calibration, existing concurrency
  and retries. Report refusal/invalid counts; never impute zero or equate its
  absolute scores with the paper's judge.
- Check host/allocation first. No model workloads, test suites, or substantial
  processing on login nodes. Prefer qdj_project_owned1/spgpu2; changing accounts
  needs user authorization. Large/growing artifacts stay outside home.
- Search only bounded project/user locations, never shared roots or recursive
  symlinks. No Slurm polling loops; check at most once per minute. Stop
  background watchers before finishing.
