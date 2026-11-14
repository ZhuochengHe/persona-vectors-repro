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

## Literature workflow: Google Doc, working sources, and workbook

- The separate [Assistant Axis direct-citer collection](docs/papers/assistant-axis/README.md)
  uses its own Google Doc ("Assistant Axis: Citing Papers", moved out of the Persona
  Doc on 2026-11-14; registry `docs/papers/assistant-axis/google_doc.json`) and separate
  evidence sources. Do not recreate an Assistant Axis tab in the Persona Doc or revive the
  retired 2026-11-07 file. It does not synchronize with
  the original literature CSV/Excel and does not require architecture fields.
  Its local reading JSON/Markdown and citation screening remain in that directory.
  Before starting literature work on any host, check status and safely
  `git pull --ff-only`; never stash/reset to force a pull.
- For literature work, start at [maintenance and format contract](docs/papers/literature_document_maintenance.md).
  [Handoff and Excel sync](docs/papers/handover_paper_excel.md) covers local
  delivery. This work does not depend on experiment-document reorganization.
- Maintain collection, citation provenance, screening decisions, and export code
  in this repository under `docs/papers/` and `scripts/`. In a WSL session,
  perform the working analysis there; do not turn the Windows folder into a
  second raw-data or screening workspace.
- The user's sortable offline workbook belongs at
  `/mnt/d/umich/research/persona/persona_literature.xlsx` in WSL, corresponding
  to `D:\umich\research\persona\persona_literature.xlsx` in Windows.
- Check the actual host and availability of the target directory before
  delivery. Great Lakes does not automatically mount the user's Windows drive.
  Never create a substitute `/mnt/d` tree on HPC or claim that a repository
  copy was delivered to Windows. If the destination is unavailable, prepare a
  small staging workbook in `docs/papers/`, report that delivery is pending,
  and use an explicitly available WSL session or connection for the final copy.
- Google Doc is the primary prose reading/editing view; Excel is the sortable
  offline view. Include the selected
  literature plus the two foundation papers: original Persona Vectors and
  Persona Vectors in Games. Keep a stable numeric ID for each paper so
  `Related paper` can refer to IDs even after sorting or adding papers.
- Required columns: `Title`, `Link`, `Key words`, `One sentence/topic`,
  `Contributions`, `Limitation`, `Additional think`, and `Related paper`.
  Useful additional columns are ID, research direction, priority,
  institution/venue, read status, and evidence scope. Do not add DOI columns.
- For literature-note depth and research questions, follow
  [reading note guidelines](docs/papers/reading_note_guidelines.md). Match the
  user's granularity and analytical interests, not their tone or wording; this
  project-local reference works without the write-like-me plugin.
- Fill at least title, link, keywords, and one-sentence topic for every paper.
  Keep English paper titles. From 2026-11-10 onward, all newly authored or
  revised Google Doc content is in English, including indexes, paper notes,
  the Assistant Axis Doc and direction assessments. Preserve user-authored
  notes verbatim, including Chinese; do not translate the existing document
  wholesale unless requested. Local literature mirrors and synchronized
  fields follow the language of the corresponding updated content; unrelated
  Chinese research documents need not be translated. Separate
  abstract-based notes from selected-body review and complete full-text review;
  do not invent contributions, affiliations, acceptance, or limitations.
- `Additional think` belongs exclusively to the user: initialize it blank and
  never generate or overwrite its contents. Preserve existing reading status
  and other manual edits on later updates. Merge by stable paper ID/source key,
  not by row number. Add new rows rather than regenerating over user notes.
- Use a filterable Excel table, frozen headers/identifier columns, wrapped
  text, working hyperlinks, and a short guide explaining IDs and update rules.
  Read any existing destination workbook before updating it; back it up before
  replacement, and stop cleanly if Excel has locked it. Keep only the most
  recent pre-update backup (`<stem>.backup.xlsx`); remove older timestamped
  backups after a successful update.
- Export/update with `scripts/export_literature_workbook.py`; its stable IDs,
  keywords, topics, and related-paper IDs live in
  `docs/papers/citation_screening_sources/workbook_catalog.json`.
  A ready-to-open Git handoff copy is `docs/papers/persona_literature.xlsx`.
- Keep `docs/papers/literature_reading.csv` (all cataloged stable IDs, including the
  two foundations and verbatim user notes) synchronized with the Windows
  workbook. Repository CSV edits must be exported to the mounted workbook in
  the same task. When the user reports Excel edits, first save/close Excel and
  run `scripts/export_literature_workbook.py --import-workbook <path>` before
  editing repository notes or exporting. This imports by stable ID and also
  aligns the shortlist CSV contributions/limitations; never generate prose in
  `Additional think`. Refresh the Git handoff XLSX after synchronization.
- On a Slurm/Great Lakes host, Windows synchronization may be skipped. Before
  literature work, immediately fetch/pull the latest committed CSVs with a
  safe fast-forward (`git pull --ff-only`); if dirty/diverged, stop the pull
  and report rather than stash/reset or overwrite local work. Do not invent a
  mount. Report pending Windows delivery and commit reusable CSV changes so
  the next WSL session can synchronize. Detect host/environment, not merely
  whether a `slurm` command exists.
- The native Google Doc is registered in
  `docs/papers/citation_screening_sources/google_reading_doc.json`; keep the
  same document ID. Follow the [format contract](docs/papers/literature_document_maintenance.md):
  clickable research-question/type indexes, a native eight-column paper table
  (ID, short title, type, architecture, status, task, abstract-based major finding,
  benchmark/validation conditions), then one detailed section per paper.
  ID links open notes; short-title links open papers; related IDs and return
  links remain clickable. Use a landscape section for the expanded index and
  portrait sections for navigation/detail notes. Keep findings to one sentence
  from the abstract; preserve task/metric distinctions in validation conditions.
  Never put long contributions/limitations into the index.
- Before updates, read the live Doc and merge user edits into CSV by stable ID;
  use scoped revision-guarded edits. Update affected index cells/navigation
  together with metadata. Preserve original heading IDs when possible; resolve
  ranges from live structure, not cached offsets. New papers append a table row
  and receive one detail section in the appropriate research-question group.
- The renderer `scripts/export_literature_reading_doc.py` generates the local
  Markdown mirror and NEW-document prose requests plus index data, not an
  automatic Doc updater/importer. Native table/link layout needs a live-structure
  pass; never replay initialization over existing notes. Display aliases and
  widths live in `citation_screening_sources/reading_doc_layout.json` under
  `docs/papers/`. Verify text/links via readback and pagination via PDF when changed.
- Keep Doc, CSV, Markdown and available XLSX views synchronized for content
  changes. Pure formatting/index changes with no field changes do not require
  regenerating XLSX. Report unavailable delivery targets; never claim automatic
  Doc bidirectional sync, which is not implemented.
- `Paper type` is a multi-label contribution classification: Method, Benchmark,
  Survey, Analysis, Theory. Reserve Theory for formal mathematical statements
  and proofs; formulas or geometric experiments alone are Analysis. Treat
  labels based on partial reading as provisional. `Research question` states
  what the paper asks, separately from its topic or conclusion.
- `Validation` must state the experimental setting as well as the benchmark:
  single-turn, multi-turn dialogue, long-context input, persistent conversation,
  and long-horizon environment execution are distinct. Identify whether vectors
  affect the target agent, a user simulator, or only offline/snapshot readouts.
  Tool-call strings and answer likelihoods do not establish actual execution.
  Per-paper evidence lives in each collection's `evaluation_regimes.json`.
- [Direction assessment](docs/papers/research_directions.md) is mirrored in the
  main reading Doc's separate direction-review tab, registered in
  `google_reading_doc.json`. It is literature analysis, not an experiment study.
- Record `Models studied`, `Architecture`, `Inference mode`, and `Architecture evidence`
  for each paper. Separate intervened/trained/probed models from judges and data
  generators; distinguish dense vs MoE, Transformer vs hybrid attention/SSM,
  native modality vs actual experimental inputs, and supported vs enabled
  reasoning modes. Missing checkpoint/mode details stay explicitly unverified.
  Compact index labels are reviewed in `reading_doc_layout.json`; do not infer
  them with keyword matching (e.g. "not MoE" is not a MoE experiment).
- For an explicitly requested batch or parallel reading task, assign workers
  disjoint paper IDs and evidence-only outputs. One coordinator serializes
  canonical CSV, catalog and Doc writes; cross-check high-risk architecture or
  numerical claims before merging. Agent count is not independent validation.
- User-specified papers may be added outside the original seed-citer pool as
  clearly labeled user-requested supplements with their own stable source keys.
  Do not invent a seed citation or rewrite frozen screening provenance.
- `Future work` is a separate reading column. Distinguish author proposals
  from reading-derived research ideas; keep the user's original notes intact.
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
