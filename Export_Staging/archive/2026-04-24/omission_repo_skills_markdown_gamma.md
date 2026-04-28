from="GPT-5.4 Thinking"
to="gemini-cli and repo maintainers"
subject="Repo-specific skill and markdown remediation"

# A. Ingredients

1. Repository under inspection: `omission-main.zip` as unpacked into `omission-main/`.
2. Active operator surfaces inspected:
   - `README.md`
   - `GEMINI.md`
   - `context/GEMINI.md`
   - `context/**.md`
   - `dashboard/**`
   - `.gemini/skills/**`
   - `src/main.py`
   - `src/scripts/run_pipeline.py`
3. Observed live code topology:
   - `src/analysis/*`
   - numbered figure modules `src/f001_*` through `src/f050_*`
   - `dashboard/src/*`
4. Observed skill topology:
   - `.gemini/skills/*`
   - `context/archive/*`
   - `frontend-dashboard.skill`
5. Constraints inferred from the repo’s own norms:
   - no unnecessary new top-level clutter
   - keep agent routing deterministic
   - prefer truthful, current, executable documentation over aspirational documentation
6. Success criterion for this remediation:
   - every skill points to real files
   - every markdown tells the truth about current architecture
   - every code-facing skill includes validation
   - central pipeline entry points are runnable or clearly marked as non-canonical

# B. Problem-Solution Chain

## B1. Core diagnosis

The repository has a strong conceptual organization and a rich skill layer, but the documentation surface, skill surface, and executable code surface are only partially synchronized.

The highest-level failure is not lack of content. The repo has a lot of content. The highest-level failure is architectural drift:
- many skills describe files that do not exist;
- several root/context markdowns describe a canonical structure that is not the live structure;
- the central pipeline import graph is out of sync with the actual module names;
- the dashboard code expects assets that are not present while the dashboard README is still a template;
- some skills are operational, others are advisory, and the repo does not clearly distinguish which is which.

This creates three downstream problems:
1. an agent can choose the right conceptual skill but still act on false file targets;
2. a human can follow the README and hit import or path failures;
3. future maintenance becomes multiplicative because each code refactor requires a broad documentation repair that has not been automated.

## B2. Primary objective

Convert the repo from “knowledge-rich but partially stale” into “operationally trustworthy.”

That requires four changes to happen together:
1. normalize the skill layer;
2. make markdown paths truthful;
3. align entry points with actual code;
4. add repo-level consistency checks so the drift does not recur.

# C. Gathering Components

## C1. What is strong already

1. The repo has real thematic structure. The figure-driven layout is clear and expressive.
2. The skills are domain-aware and often conceptually well targeted.
3. The `context/` tree is rich and shows serious thinking about analysis, manuscript, protocol, and overview layers.
4. The `src/analysis/io` pattern suggests there is already some internal modularization discipline.
5. The dashboard exists as a real frontend scaffold rather than only a plan.

These are not small positives. The remediation is therefore about synchronization and hardening, not about inventing structure from nothing.

## C2. What is concretely weak

### C2.1 Skill naming is inconsistent

Observed issue:
- several skills use `skill.md` instead of `SKILL.md`.

Impact:
- weakens deterministic skill discovery;
- introduces casing ambiguity;
- makes cross-skill conventions less reliable.

### C2.2 Many skills point to missing files

Representative missing targets referenced by skills include:
- `src/core/data_loader.py`
- `src/core/plotting.py`
- `src/core/plotting_engine.py`
- `src/utils/nwb_io.py`
- `src/utils/qwen_subagent.py`
- `src/analysis/connectivity.py`
- `src/analysis/pac.py`
- `src/analysis/pupil_decoding.py`
- `src/analysis/classification.py`
- `src/analysis/population.py`
- `src/analysis/geometry.py`
- `src/analysis/latencies.py`
- `src/analysis/fano_factor.py`
- `src/extract/pipeline_orchestrator.py`
- `src/extract/extract_omission_factors.py`
- `src/export/npy_io.py`
- `src/export/npy_orchestrator.py`
- `src/data/nwb_loader.py`
- `src/math/connectivity.py`
- `src/math/information.py`
- `src/math/information_theory.py`
- `src/spectral/wavelet_engine.py`
- `src/spectral/wavelet_transform.py`
- legacy `codes/functions/...`

Impact:
- the skill may be conceptually correct but operationally false;
- a model may confidently act on non-existent modules;
- debugging becomes unnecessarily expensive because the failure appears late.

### C2.3 Root and context docs describe a repo that is not present

Observed mismatches include:
- `README.md` says `tests/` exists under development, but there is no `tests/` directory in the archive.
- `context/GEMINI.md` mandates exactly five root folders including `tests/` and `Export_Staging/`, but neither exists.
- `context/GEMINI.md` declares canonical files such as `src/core/plotting.py` and `src/core/data_loader.py`, but these do not exist.
- several docs still present `src/core/*` as the truth layer while the live code is organized around `src/analysis/*` and `src/f0xx_*` modules.

Impact:
- root-level governance docs are no longer trustworthy;
- any agent following them is penalized for obedience;
- maintainers cannot tell whether absence means “not yet committed” or “architecture changed.”

### C2.4 Central pipeline is broken by stale imports

Observed in `src/scripts/run_pipeline.py`:
- imports `src.f012_mi_matrix.script`
- imports `src.f013_connectivity_graph.script`
- imports `src.f014_connectivity_delta.script`
- imports `src.f015_global_dynamics.script`

Observed in live tree instead:
- `src/f012_csd_profiling`
- `src/f013_rhythmic_evolution`
- `src/f014_spiking_granger`
- `src/f015_spectral_granger`

Impact:
- `python -m src.main --run-all` is not a dependable canonical path;
- the README advertises a top-level execution path that is likely to fail immediately;
- any skill referring to the full-batch pipeline inherits this breakage.

### C2.5 CLI help text is out of date

Observed in `src/main.py`:
- `--run-all` help says “Fig 1-30” while the pipeline file enumerates `f001-f040`.

Impact:
- small on its own, but it is diagnostic of drift;
- user expectations and code behavior diverge even at the CLI surface.

### C2.6 Dashboard operator surface is incomplete

Observed:
- `dashboard/README.md` is still the stock Vite README.
- `dashboard/src/App.jsx` imports `./data/manifest.json`, but `dashboard/src/data/manifest.json` is absent.
- the dashboard code is project-specific, but the dashboard docs are template-level.
- `frontend-dashboard.skill` is a zip archive containing `SKILL.md`, which is unusual and easy to miss.

Impact:
- frontend is neither self-documenting nor self-validating;
- the operator surface for dashboard work is fragmented;
- a maintainer sees a project dashboard but receives template instructions.

### C2.7 Some skills are notes, not executable skills

Examples of likely under-specified skills:
- `write-neuro-omission-manuscript-suite`
- `study-eval-actions`
- some analysis suite wrappers that describe intent but not exact invocation, file truth, and validation.

Impact:
- high-level reasoning is present, but actionability is weaker than it should be;
- agents must infer too much;
- the same task can be performed differently across runs.

### C2.8 Legacy and active documentation are too porous

Observed:
- `context/archive/` contains a substantial amount of material that remains semantically close to active work;
- active skills still echo legacy names and legacy path assumptions;
- the repo does not always sharply separate “archived guidance” from “current execution truth.”

Impact:
- models may blend historical and current architecture;
- path drift persists because legacy docs are not quarantined strongly enough.

# D. Exact Failure Taxonomy

## D1. Routing failures

Definition:
A model chooses the right domain skill but is routed into false file references or outdated commands.

Mechanism:
- stale path references;
- duplicate overlapping skill families;
- mixed filename casing.

Representative consequence:
A skill says use `src/core/data_loader.py`, but the live importable loader is elsewhere.

## D2. Execution failures

Definition:
The advertised command path exists in docs but fails when run.

Mechanism:
- stale imports in `src/scripts/run_pipeline.py`;
- missing dashboard manifest;
- missing canonical modules referenced in docs.

Representative consequence:
A maintainer runs the main batch pipeline and fails before any figure logic begins.

## D3. Governance failures

Definition:
The repo’s “must always” statements are no longer true.

Mechanism:
- hard mandates in `context/GEMINI.md` that do not match the tree;
- canonical file declarations for files that do not exist.

Representative consequence:
The strongest rules in the repo become the least trustworthy statements.

## D4. Maintenance failures

Definition:
Refactors are cheap in code but expensive in documentation because there is no consistency enforcement.

Mechanism:
- no automated checker for referenced paths in markdown;
- no validation that every skill points to real files;
- no smoke tests for the main entry points.

Representative consequence:
The repo gradually accumulates good ideas and stale instructions together.

# E. Remediation Strategy

## E1. Guiding principle

Do not merely add more docs. Reduce mismatch density.

The repo does not need a documentation volume increase first. It needs a documentation truth increase. The correct strategy is therefore:
1. normalize;
2. prune or archive stale claims;
3. reconnect skills to the live code topology;
4. add low-cost automated checks.

## E2. Canonical truth model to adopt

The live repo strongly suggests that the real topology is:
- orchestration: `src/main.py`, `src/scripts/*`
- analysis libraries: `src/analysis/*`
- figure workflows: `src/f0xx_*`
- dashboard frontend: `dashboard/src/*`
- project context: `context/*`
- active operator skills: `.gemini/skills/*`
- historical reference only: `context/archive/*`

This must become the explicitly documented truth. Any mention of `src/core/*`, `src/extract/*`, `codes/*`, or absent helpers should be either migrated or archived.

# F. Ordered Action Plan

## F1. Tier 0: emergency integrity fixes

These are the highest-value fixes because they directly affect trust.

### F1.1 Repair the batch pipeline imports

Action:
- update `src/scripts/run_pipeline.py` so imports match the live module names.
- audit all `run_f0xx` imports against actual directories.
- run a minimal import-only smoke test.

Reason:
The main advertised command path must be truthful before deeper refinement.

Critical improvement:
If some figure folders are placeholders or intentionally not wired, then the pipeline should either:
- import only verified runnable figures, or
- generate a clear “not yet wired” log entry without import-time failure.

### F1.2 Update `src/main.py` help text

Action:
- align CLI help to the actual pipeline range and scope.

Reason:
CLI text is part of the contract surface.

### F1.3 Replace the dashboard template README

Action:
- replace `dashboard/README.md` with project-specific instructions.
- document required data files, especially the manifest contract.

Reason:
A project dashboard cannot ship with template documentation and still be considered production-directed.

### F1.4 Resolve the dashboard manifest gap

Action:
- either commit `dashboard/src/data/manifest.json`, or
- change `App.jsx` to consume a generated manifest from a documented build step, or
- move manifest generation into a script and document it.

Reason:
The current frontend contract is incomplete.

## F2. Tier 1: skill normalization

### F2.1 Normalize all skill filenames to `SKILL.md`

Action:
- rename every lowercase `skill.md` to uppercase `SKILL.md`.

Reason:
Deterministic skill discovery is more important than individual preference.

Critical improvement:
After renaming, sweep all docs for references to the old lowercase filenames.

### F2.2 Introduce a single mandatory skill schema

Every active skill should contain the following sections in the same order:
1. Purpose
2. When to use
3. When not to use
4. Inputs
5. Outputs
6. Canonical repo files
7. Procedure
8. Validation
9. Failure modes
10. Minimal example
11. Related skills

Reason:
The problem with many current skills is not intelligence but uneven operator quality.

Critical improvement:
Separate domain knowledge from execution instructions. Skills should not read like essays.

### F2.3 Distinguish active skills from knowledge references

Action:
- active operator skills remain in `.gemini/skills/*`.
- static knowledge references should move into `context/` or skill-local `references/` without pretending to be action surfaces.

Reason:
A skill should answer “what do I do now,” not merely “what do I know.”

### F2.4 Rebind every skill to live paths

Action:
- for each skill, replace stale file mentions with actual files under `src/analysis/*`, `src/f0xx_*`, `dashboard/src/*`, or other real locations.

Reason:
This is the core synchronization step.

## F3. Tier 2: root and context markdown correction

### F3.1 Rewrite `context/GEMINI.md` to match the live repo

Action:
- remove mandates about absent root folders unless they will be created immediately;
- remove canonical file claims for absent modules;
- replace with truthful statements about current architecture.

Reason:
Governance docs must be stricter than all others, so they cannot afford drift.

### F3.2 Repair `README.md`

Action:
- remove or revise references to `tests/` if not present;
- verify `python -m src.main --run-all` only after the pipeline is fixed;
- state the true Python support range instead of “Python 3.14 exclusively” unless validated.

Reason:
The README is the first contract.

Critical improvement:
If Python 3.14 is a preference rather than a hard tested requirement, say so. Exclusive version mandates should be backed by CI.

### F3.3 Mark archive content as historical, not executable

Action:
- prepend archive docs with a clear notice that they are historical reference only;
- ensure active skills do not link to archived plans as if they were current instructions.

Reason:
Archive bleed-through is currently too easy.

## F4. Tier 3: code-facing skill hardening

### F4.1 Add validation blocks everywhere

Each code-facing skill should state how to verify completion, for example:
- import succeeds;
- output file exists;
- output dimensions are correct;
- no empty session mapping;
- plots render without exception;
- dashboard builds successfully.

Reason:
Without validation, the skill stops at intention instead of completion.

### F4.2 Add “do not” clauses

Examples:
- do not invent modules that are not in the repo;
- do not reference `codes/*` unless actively restored;
- do not use archived plans as execution authority;
- do not change root layout based on stale governance docs;
- do not claim canonical loaders or plotters unless they exist.

Reason:
Negative constraints are unusually valuable in agentic repos.

### F4.3 Require path truth in examples

Action:
- every example command or file path in every skill must resolve in the live repo.

Reason:
Examples are often copied into action. False examples are worse than missing examples.

# G. Skill-by-Skill Prioritization

## G1. Highest-priority skills to rewrite first

### 1. `analysis-omission-suite`

Why first:
- likely intended as a top-level routing skill;
- currently references stale canonical infrastructure.

Required improvements:
- point to real orchestration entry points;
- identify actual analysis modules and figure families;
- define exactly when to use figure modules versus shared analysis utilities;
- add validation and failure modes.

### 2. `coding-neuro-omission-nwb-pipeline`

Why first:
- NWB access is foundational;
- stale path references here propagate everywhere.

Required improvements:
- map to the actual loader and IO stack under `src/analysis/io` or the real live equivalents;
- define lazy-loading rules, safety rules, output formats, and verification;
- remove references to absent `src/extract/pipeline_orchestrator.py`.

### 3. `analysis-nwb-read-guardrails`

Why first:
- guardrail skills shape safe execution behavior;
- stale references undermine safety.

Required improvements:
- replace `src/utils/nwb_io.py` with the real NWB IO implementation;
- include exact inspection sequence and abort conditions;
- state what never to do on large NWB files.

### 4. `spike-population`

Why first:
- currently uses legacy `codes/functions/...` references;
- likely important for real downstream analyses.

Required improvements:
- rebind to actual spiking modules under `src/analysis/spiking` or current figure modules;
- define inputs, outputs, and cross-area/laminar expectations.

### 5. `write-neuro-omission-manuscript-suite`

Why first:
- manuscript work is central in this project context;
- the skill is conceptually relevant but not operational enough.

Required improvements:
- enforce section order;
- specify figure-to-section linkage;
- define citation/DOI rules;
- define paragraph length constraints;
- define source-of-truth files for manuscript drafts;
- state how `.tex`, `.gdoc`, and `.pdf` outputs are synchronized.

## G2. Second-priority skills to rewrite

- `analysis-lfp-pipeline`
- `lfp-core`
- `analysis-neuro-omission-functional-connectivity`
- `analysis-neuro-omission-pac-analysis`
- `analysis-neuro-omission-pupil-decoding`
- `analysis-population-coding`
- `analysis-rsa-cka`
- `analysis-poster-figures`
- `predictive-routing`
- `paper-architecture`

Reason:
These are likely heavily used, but their path truth is compromised.

## G3. Skills that should probably become references, not operator skills

Candidates:
- broad science concept skills that mostly provide theoretical framing;
- extremely abstract evaluation or study design notes that do not map to exact repo actions.

Reason:
If a skill cannot answer “which real files do I touch and how do I validate success,” it is probably a knowledge reference, not an execution skill.

# H. Markdown Refactoring Rules

## H1. What to remove

Remove or revise wording like:
- “ALWAYS use `src/core/...`” when the file does not exist.
- “Root MUST only contain ...” when the current root already violates the rule.
- “Use Python 3.14 exclusively” unless enforced and tested.
- “Canonical loader” or “canonical plotter” when absent.
- any reference to `codes/*` unless the directory actually exists.

## H2. What to add

Add explicit fields such as:
- Live canonical files
- Known stale legacy names
- Validation checklist
- Related archive references, if any

## H3. What to shorten

Long prose explanations in skills should be compressed into decision rules.

Example transformation:
- bad style: several paragraphs about why a loader is important;
- better style: “Use `X` for session-level NWB reads; use `Y` for metadata-only inspection; abort if probe map is incomplete.”

# I. Structural Code Improvements for Skill Reliability

## I1. Add a repo consistency checker

Create one script whose job is to fail fast on drift.

Minimum checks:
1. every active skill file is named `SKILL.md`;
2. every local path referenced in active markdown exists;
3. every `python -m` or module import example resolves;
4. all root governance docs point only to real files;
5. dashboard required assets exist or generation rules exist.

Reason:
Manual synchronization is not enough anymore.

## I2. Add smoke tests for entry points

Minimum smoke tests:
- import `src.main`
- import `src.scripts.run_pipeline`
- import every declared figure module wired into the pipeline
- build or lint dashboard

Reason:
The repo’s failure mode is often import drift, so import smoke tests buy a lot.

## I3. Add a generated skill index

Action:
- generate a machine-readable or markdown index of active skills, purpose, status, and canonical file anchors.

Reason:
You have enough skills now that discoverability itself is a maintenance problem.

Critical improvement:
Each skill should have a status field:
- active
- needs migration
- archived

# J. Proposed Repo Truth Model

## J1. Canonical architecture statement

The repo should explicitly state something close to this:

- `src/analysis/*` contains reusable analysis primitives and IO/logging helpers.
- `src/f0xx_*` contains figure-oriented execution modules.
- `src/scripts/*` contains orchestration entry points.
- `src/main.py` is the CLI entry point.
- `.gemini/skills/*` contains active operator skills.
- `context/*` contains active project context and specs.
- `context/archive/*` contains historical material not authoritative for current execution.
- `dashboard/src/*` contains the frontend app; data contracts must be documented explicitly.

Once this statement is adopted, every doc should be audited against it.

# K. Concrete Rewrite Examples

## K1. Example of how a stale skill should be transformed

### Old pattern
- “Always use `src/core/data_loader.py`.”
- “Use the canonical plotter in `src/core/plotting.py`.”
- no validation block.

### New pattern
- “For session-level loading, use `src.analysis.io.loader.DataLoader` from `src/analysis/io/loader.py` if that is the live implementation.”
- “For figure-specific work, call the corresponding `src/f0xx_*/script.py` entry point or its shared analysis utility.”
- validation:
  - import succeeds;
  - selected session metadata loads;
  - output directory contains expected artifact(s).

## K2. Example of how a stale dashboard doc should be transformed

### Old pattern
- stock Vite template README.

### New pattern
- project overview;
- manifest contract;
- how figure iframes are sourced;
- required local files;
- how to run dev server;
- how to verify figure and report rendering.

# L. Proposed Execution Sequence

## L1. Week-0 style order of operations

1. fix `src/scripts/run_pipeline.py` imports;
2. fix `src/main.py` CLI text;
3. fix dashboard README and manifest contract;
4. normalize all skill filenames to `SKILL.md`;
5. rewrite top five critical skills against live paths;
6. rewrite `README.md` and `context/GEMINI.md` to match reality;
7. add consistency checker;
8. add import smoke tests;
9. then perform second-pass cleanup across remaining skills.

Reason:
This order restores trust fastest while minimizing repeated edits.

# M. Risk Register

## M1. Main risk if no action is taken

The repo will continue to accumulate high-quality analysis content while becoming less executable over time. That is the worst kind of degradation because it is subtle: everything looks sophisticated, but the operator layer quietly loses truthfulness.

## M2. Main risk of over-correction

A heavy rewrite could erase useful historical context.

Mitigation:
- preserve archive material, but quarantine it clearly;
- do not delete domain knowledge, only demote stale execution claims.

# N. Acceptance Criteria

The remediation should be considered complete only when all of the following are true:

1. `python -m src.main --run-all` either runs or fails only at runtime work units, not at import resolution.
2. No active skill references a missing local path.
3. All active skills are named `SKILL.md`.
4. `README.md` and `context/GEMINI.md` describe the live repo truthfully.
5. The dashboard README is project-specific.
6. Dashboard manifest handling is documented and satisfied.
7. Archive docs are clearly marked non-authoritative.
8. A consistency checker exists and passes.

# O. Final Outcome

The repo does not need more ambition. It already has ambition.

It needs convergence.

The most important shift is to make the skill layer, markdown layer, and code layer speak the same language about the same files. Once that is done, the rest of the repo becomes much more powerful: the figure-module architecture becomes navigable, the analysis stack becomes safer to use, the manuscript work becomes easier to ground in real outputs, and the dashboard becomes an actual interface instead of a partial scaffold.

In practical terms, the highest-yield work is:
- fix the broken pipeline contract;
- rewrite the top-level skills against the real code;
- remove stale canonical claims;
- add consistency automation so this does not happen again.

That will convert the repo from “promising but drift-prone” into “agent-ready and maintainable.”
