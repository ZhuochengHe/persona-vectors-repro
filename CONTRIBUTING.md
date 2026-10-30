# Git and experiment workflow

## Choose isolation by the implementation change

| Change | Recommended workflow |
|---|---|
| More coefficients, seeds, model controls, or another run of an existing protocol | Add/reuse a descriptive config or narrowly scoped runner; update the existing study. A separate branch is optional. |
| Small reusable pipeline improvement | Validate it and make a focused implementation commit, separate from result updates. |
| Changes to shared model loading, extraction, hooks, judging, or data semantics | Use a feature branch; use a worktree when the main workspace has unrelated changes or ongoing work. |
| Concurrent alternative implementations | One branch/worktree per alternative, from the same explicit base commit. Keep their data directories separate. |

A new config or script is not a new research document. Reuse the existing study
unless the scientific question changes. Avoid creating another runner when a
config or an existing interface can express the experiment. Share model/runtime
code rather than copying it into each runner.

`main` is the integration branch. Small, self-contained changes can be committed
there; substantial experiments and competing implementations should be developed
on branches such as `feat/gaming-layer-selection` or `exp/steering-sampler`.
Do not require a pull request for every local experiment. Merge after appropriate
checks and review, not merely because a Slurm job was submitted.

## Commit discipline

- Commit reusable fixes and workflow improvements once their relevant checks
  pass. Do not leave them mixed with multiple later experiments.
- Before a new expensive run, commit the implementation and config needed to
  reproduce it. Record the commit and freeze the actual submitted inputs.
- Keep implementation, experiment configuration/protocol, and harvested
  results/interpretation in separate coherent commits when practical. A commit
  must include its new local dependencies; do not commit a runner that relies
  on an untracked module or undeclared local asset.
- Use explicit paths when staging. Review `git diff --cached` before committing.
  Do not use `git add .` to sweep in another agent's work, credentials, generated
  artifacts, or unfinished changes.
- Prefer concise messages explaining the resulting behavior, for example
  `fix: preserve assistant-turn boundaries during extraction`,
  `feat: select gaming layers under a coherence constraint`, or
  `results: summarize the sampler ablation`.
- Do not automatically stash, reset, clean, force-push, or switch an occupied
  workspace to another branch. Commit locally without assuming it also needs
  an immediate remote push. Keep an experiment branch until its provenance is
  safely recorded and its useful changes are integrated.

## Branches and worktrees

A branch isolates history; a worktree also isolates files. Multiple agents or
alternative implementations must not switch branches in the same working
directory. Commit shared prerequisites first: a new worktree starts from a
commit and does **not** include uncommitted changes from the original workspace.

Place worktrees in the project's large-file workspace, not inside a run's frozen
`source/` directory. Create one only when isolation is useful. Set `BASE_COMMIT` to the reviewed
commit SHA first:

```bash
git worktree add -b exp/steering-sampler \
  "$PV_WORK/worktrees/steering-sampler" "$BASE_COMMIT"
```

Use the same model caches and read-only source datasets when appropriate, but
separate run directories, writable outputs, and active-run pointers. Changes to
dependency versions require a separate environment or explicit compatibility
validation; worktrees do not isolate Python environments by themselves.

Parallel implementations should share the same declared base, dataset split,
sampling seeds, and evaluation protocol where scientifically appropriate. Record
their differences explicitly. Keep result-document updates serialized; either
have one coordinator update the canonical study or merge result updates later.

Integrate with a regular merge or a focused cherry-pick after checks. Preserve
the source implementation commit in the experiment record even if integration
creates another SHA. Remove a worktree only after jobs no longer depend on it,
its changes are committed/integrated, and required artifacts are preserved.

## Experiment lifecycle

1. **Design:** locate the existing stable study; fix the question, controls,
   counts, sampler, development/confirmation split, and selection rules.
2. **Implement:** choose the appropriate workspace, validate relevant behavior,
   and commit the required code/config/assets. Run model workloads and test
   suites in Slurm, not on the login node.
3. **Freeze and submit:** copy declared inputs to a unique run directory and
   record hashes. Jobs execute that frozen copy, not a mutable worktree.
4. **Monitor:** distinguish generation, scoring, analysis, and archival states.
   Do not alter a running job's inputs or move its files to tidy the repository.
   Change methods through a new versioned implementation and a new run.
5. **Harvest:** check counts, scoring status, job outcome, and provenance; update
   the existing study and registry. Update the topic-level interpretation only
   when the evidence supports it. Commit the result/document changes separately.
6. **Integrate and archive:** merge reusable implementation changes, verify
   actual Drive IDs/checksums, then retire temporary worktrees and old pointer
   paths when they are no longer needed.

Record at least the study ID, run ID, implementation commit, branch/base when
relevant, model/data/vector identities, config/task/source hashes, environment,
and Slurm IDs. A commit SHA alone is insufficient if the submitted source had
uncommitted changes: historical dirty snapshots remain valid evidence through
their manifests, but must not be described as exact clean-commit reproductions.
Never rewrite their provenance to match a later commit retroactively.

## Documentation and currently running experiments

Canonical documents live under `docs/research/`: topic overviews explain ideas,
stable study records hold settings/results, and the registry maps studies to
runs and archives. New runs do not need new numbered or dated notes.

Keep existing compatibility links and automatic-report markers while frozen
jobs still reference them. Defer further relocation, merging, renaming, or
archival cleanup of active experiments until they finish. The current pending
documentation reorganization should be committed coherently after its active
writers are finished; do not include it accidentally in unrelated commits.

The existing submission scripts are launchers, not proof that all of the above
provenance checks have been automated. Verify the frozen manifest and settings
for each submission instead of assuming a wrapper enforces them.
