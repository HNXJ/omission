from="gpt-5.4-thinking"
to="all-any ; gemini-cli ; repo-maintainers"
subject="Stabilize omission code, skills, context, dashboard"

# A. Ingredients

1. Repository inspected from the uploaded archive `omission-main.zip`.
2. Active surfaces inspected directly:
   - `README.md`
   - `GEMINI.md`
   - `context/GEMINI.md`
   - `.gemini/skills/*`
   - `dashboard/*`
   - `src/*`
   - `tests/test_skill_paths.py`
3. Canonical live code topology observed:
   - `src/analysis/io`
   - `src/analysis/lfp`
   - `src/analysis/spiking`
   - `src/analysis/visualization`
   - figure packages `src/f001_*` through `src/f046_*`
   - `src/main.py`
   - `src/scripts/run_pipeline.py`
4. Dominant repository failure mode identified:
   - architectural split-brain between live code and active documentation / skills.
5. Stability target:
   - one truthful architecture,
   - one truthful skill contract,
   - one truthful dashboard data contract,
   - one truthful validation layer.

# B. Mission

The repository is already close to a useful modular analysis system, but it is unstable because its public control surfaces disagree about what the repository actually is. The code says one thing, the skill layer says another, the context layer says a third, and the dashboard assumes a fourth environment. The mission is not to add more breadth first. The mission is to make the repository self-consistent so that code execution, agent routing, documentation, and frontend visualization all consume the same reality.

# C. Problem State

## C1. Root diagnosis

The repository exhibits a split-brain architecture.

The live codebase is centered on:
- `src/analysis/*`
- figure-specific packages `src/f0xx_*`
- orchestration through `src/main.py` and `src/scripts/run_pipeline.py`
- dashboard visualization through a manifest-driven frontend.

The active instruction layer still claims or implies:
- canonical modules under `src/core/*`
- canonical loaders under `src/core/data_loader.py`
- canonical plotting under `src/core/plotting.py`
- historical utilities under `src/utils/*` and `src/extract/*`
- external Windows-only output roots as if they are repo truth.

This mismatch is the most damaging issue in the repository because it corrupts all higher-order operations:
- a human cannot know which instruction layer to trust,
- an agent can route into dead files with high confidence,
- tests validate the wrong contract,
- the dashboard depends on data contracts that are not fully formalized,
- maintenance work amplifies drift instead of reducing it.

## C2. Live code is more coherent than the docs admit

The actual codebase is not the main source of disorder. The code is imperfect, but it has a real architecture:
- analysis primitives grouped by signal type and utility domain,
- figure-specific modules with `analysis.py`, `plot.py`, and `script.py`,
- a central pipeline runner,
- a dashboard that attempts to consume figure artifacts as a gallery.

That means the best stability improvements should not start by redesigning the scientific analysis. They should start by bringing the interfaces into alignment with the current code.

## C3. Public control surfaces are overclaiming

Several top-level and active-control documents make strong claims that are false in the checked-in tree. Examples include:
- exact root structure claims that do not match the archive,
- canonical module claims for files that do not exist,
- statements that all active skills are updated to the `src/` architecture when many still reference older layouts,
- dashboard assumptions that a manifest and output directory are already present and valid.

The practical consequence is that documentation is not functioning as a stabilizer. It is acting as a second source of bugs.

# D. Solution Architecture

The repository should be stabilized around four truths, not four competing narratives.

## D1. Truth 1: code topology truth

The live Python package structure must be the primary source of truth. If the code says the analysis lives under `src/analysis/*` and figure execution lives under `src/f0xx_*`, then active docs and active skills must point there and nowhere else unless a path is explicitly marked historical.

## D2. Truth 2: operator truth

Active skills must become executable operator contracts rather than broad conceptual notes. Each active skill should specify:
- when it should be used,
- when it should not be used,
- exact inputs,
- exact outputs,
- exact canonical files,
- exact validation checks,
- exact failure modes.

## D3. Truth 3: metadata truth

The repository needs one canonical registry or metadata layer describing figure modules, labels, execution targets, expected outputs, and dashboard exposure. Right now that information is distributed across code, dashboard scripts, folder names, and human memory. That is a classic drift engine.

## D4. Truth 4: environment truth

Active repo behavior must stop assuming one Windows workstation as the canonical runtime. Local Windows support can remain first-class, but hardcoded drive-letter paths should not define repo truth. The repo should be stable under repo-relative paths with optional environment overrides.

# E. Core Findings By Surface

## E1. Root and context documents

### E1.1 `README.md`

The root README has useful scientific framing and a useful attempt at architecture summary, but it overstates repository certainty. It claims ranges such as `f001_theory/` through `f050_laminar_analysis/` even though the observed tree does not present a clean contiguous canonical range and does not end at that named package. It also asserts Python 3.14 exclusively and a rigorous 15-step master pipeline without showing the actual dependency and configuration contract needed to execute it reliably.

Highly recommended edits:
- rewrite the architecture section to match the exact live tree, not the intended mature tree,
- replace figure-range prose with a generated or manually maintained table of actual modules,
- separate scientific goals from execution guarantees,
- add a section called `Execution Reality` that states required dependencies, optional dependencies, and known environment assumptions,
- add a section called `Canonical Entrypoints` listing only real files.

### E1.2 `context/GEMINI.md`

This file is currently one of the most destabilizing documents in the repo because it functions like a control document but contains multiple false statements relative to the checked-in tree. It references `src/core/plotting.py` and `src/core/data_loader.py`, enforces an exact root layout that is not present, describes `context/skills/` as the active skill location even though `.gemini/skills/` is active, and hardcodes workspace assumptions around `D:\drive\omission` and `Export_Staging/`.

Highly recommended edits:
- shrink the file aggressively,
- convert it from visionary doctrine to repo-truth control plane,
- remove all references to nonexistent canonical modules,
- split the content into `always true` versus `local workstation preference`,
- move archival or aspirational language into `context/archive/`.

### E1.3 `GEMINI.md` at repo root

The root Gemini file should either be the short control surface and `context/GEMINI.md` becomes the extended operational guide, or vice versa. Right now the layering is not sharply defined. Two control documents that can diverge will diverge.

Highly recommended edits:
- define one file as the authoritative control file,
- define the other as explanatory support,
- add a first-line status header indicating canonicality.

## E2. Skill system

### E2.1 Active skill layer quality is mixed

The active skill layer contains good intent and substantial project-specific thinking, but its reliability is not uniform. Some skills behave like careful operator docs; others behave like archived notes or partially migrated workflow reminders.

Observed stability issues:
- mixed filename conventions (`SKILL.md` versus `skill.md`),
- stale path references to dead modules,
- Windows-only hardcoded paths treated as if universally canonical,
- some skills lacking explicit validation and failure-mode sections,
- some skills referencing broad conceptual workflows but not executable entrypoints.

### E2.2 Active skills are not sufficiently typed

The repo needs explicit classification of skills.

Recommended classes:
- **Live execution skills**: must reference only existing files and executable paths.
- **Scientific reasoning skills**: may be conceptual, but may not claim nonexistent implementation targets.
- **Archive skills**: historical, superseded, noncanonical.

Without this typing, stale guidance remains accidentally active.

### E2.3 Priority rewrite skills

The first skills to rewrite should be the ones most likely to route future work incorrectly:
- `analysis-omission-suite`
- `analysis-nwb-read-guardrails`
- `analysis-lfp-pipeline`
- `frontend-dashboard`
- `coding-neuro-omission-bhv-parser`
- `coding-neuro-omission-signal-conditioning`
- `analysis-neuro-omission-npy-export`
- `analysis-neuro-omission-oculomotor-suite`

Rationale:
these skills sit near the top of likely routing pathways and several still reference nonexistent or superseded modules.

### E2.4 Mandatory active skill template

Every active skill should adopt this exact shape:

1. Purpose
2. When to use
3. When not to use
4. Inputs
5. Outputs
6. Canonical files
7. Execution steps
8. Validation
9. Failure modes
10. Minimal example
11. Related skills
12. Status header (`active`, `experimental`, or `archived`)

The `Canonical files` section must be machine-checkable. If a file path is listed there, it must exist.

## E3. Code and orchestration

### E3.1 `src/scripts/run_pipeline.py` is structurally fragile

The pipeline runner is readable, but it eagerly imports many figure modules at file import time. That is fragile because one optional dependency failure can prevent the entire pipeline from even importing. During inspection, `src.scripts.run_pipeline` failed import because `nitime` was missing through the effective connectivity path.

This is not merely a dependency issue; it is an orchestration design issue.

Highly recommended edits:
- replace eager imports with lazy imports inside step execution,
- define a pipeline registry containing module path strings rather than function objects imported at the top,
- allow step-local capability failures without global import failure,
- add CLI support for running a single figure or subset of figures,
- separate `registry load`, `dependency check`, and `execution` concerns.

### E3.2 Duplicate figure numbering is hazardous

The tree contains duplicate numbering families such as:
- `f028_state_manifolds`
- `f028_spectral_identity_correlation`
- `f029_info_bottleneck`
- `f029_effective_connectivity`
- `f030_recurrence_dynamics`
- `f030_putative_cell_type`

This is manageable for narrative manuscript labels but harmful for tooling. A filesystem-facing id should be unique.

Highly recommended edits:
- introduce unique internal ids such as `f028a_*` and `f028b_*`, or a nonnumeric stable slug system,
- keep manuscript-facing labels separate from internal ids,
- ensure pipeline, dashboard, and tests all consume internal ids, not ambiguous display labels.

### E3.3 Optional dependencies need to be formalized

The repository currently behaves as if all scientific dependencies are core dependencies. That increases failure radius. Some modules should be optional or capability-gated.

Highly recommended edits:
- define a dependency tag set per figure module,
- expose clear error messages when a figure is invoked without required extras,
- move heavyweight imports inside analysis functions where practical,
- separate base requirements from optional extras in requirements files.

### E3.4 Shared configuration is too diffuse

Hardcoded path assumptions currently appear in skills, tests, dashboard sync scripts, and context docs. That means configuration is not centralized.

Highly recommended edits:
- create one canonical config layer, e.g. `src/config.py` or `src/analysis/io/paths.py`,
- define repo root resolution, optional external data root, optional output root, manifest path, and report path,
- permit environment-variable overrides,
- require all scripts, tests, and dashboard sync logic to consume this one config source.

### E3.5 Shared plotting truth is underenforced

The repo has a live plotting helper area under `src/analysis/visualization`, but active docs still instruct use of nonexistent `src/core/plotting.py`.

Highly recommended edits:
- declare `src/analysis/visualization/plotting.py` or the actual active plotting helper as the only plotting truth,
- remove all active references to `src/core/plotting.py`,
- standardize save behavior, HTML export, modebar policy, and theming in one place.

## E4. Dashboard

### E4.1 Good concept, weak contract

The dashboard is conceptually sound: a manifest-driven gallery that can render figures and reports. The frontend structure in `dashboard/src/App.jsx` is serviceable. The main issue is not React architecture. The issue is data-contract fragility.

Observed risks:
- direct import of `./data/manifest.json` although the file is not guaranteed present,
- frontend assumes `selectedItem.files` exists for figures,
- frontend assumes local Vite `/@fs/` serving semantics for actual content resolution,
- report and figure discovery logic exists in overlapping Python scripts with partially distinct responsibilities,
- hardcoded workstation paths appear in manifest-sync logic,
- dashboard README is descriptive but not contract-driven.

Highly recommended edits:
- define one canonical manifest schema,
- generate the manifest from one canonical Python entrypoint,
- check in a tiny example manifest for development and UI stability,
- make the UI resilient to missing or empty manifests,
- add `no data`, `missing file`, and `fetch failed` states,
- make frontend file resolution consume a single config contract rather than implicit absolute paths.

### E4.2 Dashboard should validate data, not merely consume it

The dashboard can become much more stable if it includes light validation at the boundary.

Highly recommended edits:
- validate manifest shape when the app starts,
- surface diagnostics in the UI: manifest source, figure count, report count, generation time,
- reject duplicate ids early,
- guard against missing `baseUrl`, `files`, and `title` fields.

### E4.3 Manifest generation is conceptually duplicated

There are overlapping sync / manifest scripts under `dashboard/` and `scratch/`, plus generation logic under `src/scripts/`. This creates ambiguity about which script is authoritative.

Highly recommended edits:
- declare one manifest generator as canonical,
- archive or delete the others,
- move the canonical one under `src/scripts/` or a clearly named dashboard integration module,
- make all documentation point to that one path.

## E5. Tests and validation

### E5.1 Existing test coverage is too narrow and too local-machine-specific

`tests/test_skill_paths.py` is a useful instinct but not yet a robust test. It assumes `D:\drive\omission`, only checks a narrow markdown link pattern, ignores lowercase `skill.md`, and uses process exits instead of ordinary assertions. It validates less than the repo actually needs.

Highly recommended edits:
- rewrite it as a pure pytest suite using repo-relative root discovery,
- detect both `SKILL.md` and `skill.md` while transitioning, then enforce one convention,
- scan active docs and active skills for path references,
- validate that all referenced canonical files exist,
- validate uniqueness of figure ids,
- validate that the dashboard manifest schema can be produced from the current tree,
- validate that core entrypoints import without optional figure modules breaking everything.

### E5.2 The repo needs documentation integrity tests

The fastest path to greater stability is not more unit tests in analysis code. It is integrity tests for repository contracts.

Recommended integrity tests:
- active skill path existence,
- active skill required sections,
- context control file path validity,
- duplicate figure id detection,
- pipeline registry validity,
- dashboard manifest schema validation,
- README architecture claims sanity.

# F. Strongly Recommended Edits

## F1. Immediate edits with highest leverage

### F1.1 Rewrite `context/GEMINI.md`

Target outcome:
- short,
- true,
- operational,
- free of nonexistent canonical paths.

Must remove or rewrite:
- exact-root-layout claims that are false,
- `src/core/*` canonicality claims,
- references to `Export_Staging/` as live repo truth,
- claims that `context/skills/` is the active skill home if `.gemini/skills/` is actually active.

### F1.2 Normalize all active skill filenames

Rename all active `skill.md` files to `SKILL.md`.

Reason:
active skills should not require case-variant discovery logic. This is a low-cost, high-yield cleanup.

### F1.3 Replace dead file references in active skills

Audit all active skills and replace every stale path. Where a concept no longer maps to a real file, rewrite the section in terms of the actual current module path.

### F1.4 Make figure ids unique

This is essential before further dashboard hardening. Ambiguous ids are a structural bug for registries and manifests.

### F1.5 Convert pipeline runner to lazy import registry

This will reduce global failure radius and make dependency errors local and intelligible.

## F2. Next edits with high leverage

### F2.1 Create a central figure registry

A single registry should define for each figure or analysis module:
- internal unique id,
- manuscript label,
- title,
- module path,
- runner function,
- dependency tags,
- dashboard grouping,
- expected outputs,
- README availability,
- active versus archived state.

This registry should drive:
- pipeline execution,
- dashboard manifest generation,
- integrity tests,
- auto-generated docs tables,
- skill references where appropriate.

### F2.2 Create a central path/config module

This should be imported by:
- pipeline scripts,
- manifest generation,
- tests,
- dashboard sync utilities,
- export utilities.

### F2.3 Add status banners to docs and skills

Every important markdown should begin with a small status header:
- Status: active / archived / draft / experimental
- Canonicality: authoritative / supporting / historical
- Supersedes / superseded by

This is a simple but very powerful anti-drift measure.

### F2.4 Replace the dashboard README

The current dashboard README is adequate as a starter note, but not strong enough as an engineering contract. Replace it with:
- purpose,
- manifest schema,
- data source expectations,
- local dev steps,
- empty-state behavior,
- troubleshooting,
- canonical generator path.

## F3. Medium-term edits

### F3.1 Introduce optional dependency groups

For example:
- base analysis,
- connectivity extras,
- dashboard extras,
- development / test extras.

### F3.2 Generate architecture docs from code metadata

The more architecture is generated from code, the less it drifts. The figure registry can generate a concise markdown table for README and dashboard docs.

### F3.3 Add smoke tests for core entrypoints

At minimum:
- import `src.main`,
- load pipeline registry,
- generate empty or example manifest,
- verify active skill schema.

# G. Proposed Stable End-State

## G1. Stable code state

- One central registry for figures and analysis modules.
- Unique internal ids for all figure packages.
- Lazy-import pipeline execution.
- Central config and path resolution.
- Optional dependency guards.
- Shared plotting wrapper under the actual live visualization package.

## G2. Stable skill state

- One active skill directory.
- One filename convention.
- One required skill template.
- No active references to nonexistent files.
- Archived skills visibly marked and isolated.

## G3. Stable context state

- One authoritative control document.
- One accurate architecture summary.
- Archive content clearly marked as noncanonical.
- No workstation-specific claims treated as repo law.

## G4. Stable dashboard state

- One canonical manifest schema.
- One canonical manifest generator.
- Example manifest checked in.
- UI resilient to missing or partial data.
- No implicit dependency on one machine’s filesystem layout.

## G5. Stable validation state

- Repo-relative pytest suite.
- Documentation integrity tests.
- Registry uniqueness tests.
- Manifest schema tests.
- Import smoke tests.

# H. Concrete File-Level Recommendations

## H1. `README.md`

Recommended edits:
- replace architecture prose with actual current topology,
- stop claiming contiguous or finalized figure ranges unless true,
- add `Known limitations` and `Optional dependencies`,
- add a generated table of current figure modules and status,
- separate scientific narrative from execution guarantees.

## H2. `context/GEMINI.md`

Recommended edits:
- rewrite from scratch rather than patch piecemeal,
- keep only live-truth rules,
- refer to actual paths only,
- distinguish local operator preferences from repository invariants.

## H3. `.gemini/skills/*`

Recommended edits:
- normalize names,
- add mandatory sections,
- replace all dead paths,
- add validation steps,
- add `Status` and `Canonical files` headers.

## H4. `src/scripts/run_pipeline.py`

Recommended edits:
- registry-driven lazy execution,
- local import inside each step,
- subset execution support,
- optional dependency handling,
- output summary at end using registry metadata.

## H5. `dashboard/src/App.jsx`

Recommended edits:
- defend against missing manifest and malformed items,
- split sidebar, viewer, and modal into smaller components,
- add diagnostics and empty states,
- validate presence of `files`, `baseUrl`, and `url` before use,
- avoid assuming first file exists.

## H6. `dashboard/README.md`

Recommended edits:
- define exact manifest schema,
- define exact generator path,
- explain local file serving model,
- explain expected data roots,
- include troubleshooting for empty UI and broken embeds.

## H7. `tests/test_skill_paths.py`

Recommended edits:
- make repo-relative,
- use assertions,
- broaden pattern coverage,
- validate active docs too,
- validate schema/sections,
- enforce one skill filename convention after migration.

# I. Recommended Execution Order

## I1. Phase 1: truth alignment

1. Rewrite `context/GEMINI.md`.
2. Normalize active skill filenames.
3. Remove dead canonical file claims from active skills.
4. Rewrite root README architecture and execution sections.
5. Mark archive docs and archive skills explicitly.

## I2. Phase 2: orchestration hardening

1. Create central figure registry.
2. Convert pipeline runner to lazy registry execution.
3. Introduce central config/path module.
4. Make figure ids unique.
5. Add optional dependency guards.

## I3. Phase 3: dashboard hardening

1. Define manifest schema.
2. Consolidate to one manifest generator.
3. Add example manifest.
4. Add frontend empty/error/diagnostic states.
5. Remove hidden workstation assumptions.

## I4. Phase 4: test hardening

1. Replace path test with documentation integrity suite.
2. Add figure registry validation.
3. Add manifest validation.
4. Add import smoke tests.
5. Add skill schema validation.

# J. Cautions

1. Do not try to “fix” instability by adding more high-level planning markdown first. The problem is not insufficient planning. It is insufficient convergence.
2. Do not keep both old and new architectures active in documentation. That guarantees further drift.
3. Do not let dashboard sync scripts multiply. One canonical generator is enough.
4. Do not use manuscript-facing numbering as the only machine-facing identifier when duplicates already exist.
5. Do not treat workstation-specific Windows paths as repo truth. Make them config overrides.

# K. Strongest Single Recommendation

If only one structural idea is implemented, it should be this:

Create a single canonical figure registry and force the pipeline, dashboard, tests, README tables, and active skills to consume it.

Reason:
that one move centralizes metadata, eliminates duplicate truth sources, reduces drift, supports validation, and creates a common vocabulary across code, skills, context, and frontend.

# L. Final Outcome Definition

The repository becomes stable when these statements are simultaneously true:
- active docs point only to real files,
- active skills can be executed as written,
- the pipeline imports even when optional scientific extras are absent,
- figure ids are unique internally,
- the dashboard can render gracefully with valid, missing, or partial manifests,
- tests verify integrity of the repo contracts instead of only one narrow path pattern,
- the codebase, skills, context, and dashboard all describe the same architecture.

That is the actual target state. Not more documentation. Not more figures. Convergence.
