# Comprehensive Skills Audit Report
**Auditor**: Antigravity  
**Date**: 2026-04-24  
**Scope**: All 49 active skills in `.gemini/skills/`, 4 archived skills in `context/archive/`, 1 consolidated skill in `context/skills/`, and 1 protocol in `context/protocols/`.

---

## Executive Summary

The Omission project carries **49 active operator skills**, **4 archived skills**, **1 consolidated skill**, and **1 GAMMA protocol**. The skills are conceptually rich and domain-aware, but suffer from **systemic path drift**: the majority reference files and modules that do not exist in the live codebase. This renders them operationally unreliable for any agent that takes file paths literally.

### Key Metrics
| Metric | Value |
|---|---|
| Total Active Skills | 49 |
| Skills with CORRECT file casing (`SKILL.md`) | 49/49 ✅ |
| Skills referencing ≥1 missing file | **~38/49** ❌ |
| Skills referencing ONLY live files | **~6/49** |
| Unique missing file paths referenced | **25+** |
| Skills that are knowledge-only (no executable procedure) | **~12** |
| Archived skills (correctly quarantined) | 4 |

---

## Path Truth Audit

### Files Referenced by Skills That DO NOT EXIST

These paths are cited across multiple skills as "canonical" or "core implementation" files, but resolve to nothing in the live repo.

| Referenced Path | Skills Citing It | Status |
|---|---|---|
| `codes/functions/behavioral_utils.py` | analysis-behavioral-data-processing | ❌ MISSING |
| `src/utils/eye_data_mapper.py` | analysis-behavioral-data-processing, coding-neuro-omission-bhv-parser | ❌ MISSING |
| `src/utils/behavioral.py` | coding-neuro-omission-behavioral-utils | ❌ MISSING |
| `src/core/data_loader.py` | analysis-omission-suite, nwb-analysis | ❌ MISSING |
| `src/core/plotting.py` | analysis-poster-figures, design-neuro-omission-advanced-plotting | ❌ MISSING |
| `src/utils/nwb_io.py` | analysis-nwb-read-guardrails, analysis-nwb-utils | ❌ MISSING |
| `src/analysis/pac.py` | analysis-neuro-omission-pac-analysis | ❌ MISSING |
| `src/analysis/pupil_decoding.py` | analysis-neuro-omission-pupil-decoding | ❌ MISSING |
| `src/analysis/classification.py` | analysis-neuro-omission-unit-classification | ❌ MISSING |
| `src/analysis/population.py` | analysis-neuro-omission-population-manifolds | ❌ MISSING |
| `src/analysis/geometry.py` | analysis-rsa-cka | ❌ MISSING |
| `src/analysis/latencies.py` | science-neuro-omission-surprise-latencies | ❌ MISSING |
| `src/analysis/fano_factor.py` | science-neuro-omission-variability-quenching | ❌ MISSING |
| `src/analysis/connectivity.py` | analysis-neuro-omission-functional-connectivity | ❌ MISSING |
| `src/analysis/manifolds.py` | analysis-neuro-omission-population-manifolds | ❌ MISSING |
| `src/analysis/oculomotor.py` | analysis-neuro-omission-oculomotor-suite | ❌ MISSING |
| `src/analysis/spiking/utils.py` | spike-population | ❌ MISSING |
| `src/extract/pipeline_orchestrator.py` | analysis-omission-factor-extraction | ❌ MISSING |
| `src/extract/report_utils.py` | analysis-summary-enrichment | ❌ MISSING |
| `src/export/npy_io.py` | analysis-neuro-omission-npy-export | ❌ MISSING |
| `src/data/nwb_loader.py` | nwb-analysis | ❌ MISSING |
| `src/math/connectivity.py` | math-neuro-omission-connectivity-metrics | ❌ MISSING |
| `src/math/information.py` | math-neuro-omission-stochastic-metrics | ❌ MISSING |
| `src/spectral/wavelet_engine.py` | coding-neuro-omission-signal-conditioning | ❌ MISSING |
| `src/neuro/circuits.py` | neuroscience-actions | ❌ MISSING |

### Files Referenced by Skills That DO EXIST

| Live Path | Skills Citing It | Status |
|---|---|---|
| `src/analysis/io/loader.py` | (implicitly via `DataLoader`) | ✅ LIVE |
| `src/analysis/io/eye_mapper.py` | (implicitly via `EyeDataMapper`) | ✅ LIVE |
| `src/analysis/spiking/putative_classification.py` | analysis-neuro-omission-unit-classification | ✅ LIVE |
| `src/analysis/visualization/plotting.py` | analysis-poster-figures | ✅ LIVE |
| `src/analysis/visualization/poster_figures.py` | design-neuro-omission-branding-theme | ✅ LIVE |
| `src/analysis/lfp/*` | analysis-lfp-pipeline | ✅ LIVE |
| `src/analysis/spiking/stats.py` | spike-population | ✅ LIVE |

---

## Skill-by-Skill Classification

### Tier 1: OPERATIONAL (Live paths, executable, validated)

| # | Skill | Grade | Notes |
|---|---|---|---|
| 1 | `spike-population` | **B+** | Points to `src/analysis/spiking/*` correctly. Still references `spiking/utils.py` which doesn't exist. |
| 2 | `analysis-lfp-pipeline` | **B+** | Correctly targets `src/analysis/lfp/*`. Well-structured procedure. |
| 3 | `analysis-granger-convergence-debug` | **B** | Operationally useful debug skill. References live `nitime` patterns. |
| 4 | `analysis-spectrolaminar` | **B** | Targets `src/analysis/lfp/lfp_laminar_mapping.py` correctly. |
| 5 | `frontend-dashboard` | **B-** | Points to `dashboard/src/*`. Short but functional. |
| 6 | `analysis-mapping-debug` | **B-** | Debug skill for channel mapping issues. Targets live loader patterns. |

### Tier 2: PARTIALLY OPERATIONAL (Conceptually sound, 1-3 stale references)

| # | Skill | Grade | Primary Stale Reference |
|---|---|---|---|
| 7 | `analysis-poster-figures` | **C+** | References `src/core/plotting.py` (dead). Live: `src/analysis/visualization/plotting.py` |
| 8 | `analysis-neuro-omission-unit-classification` | **C+** | References `src/analysis/classification.py` (dead). Live: `src/analysis/spiking/putative_classification.py` |
| 9 | `analysis-neuro-omission-npy-export` | **C** | References `src/export/npy_io.py` (dead). Data now lives in `D:/drive/data/arrays/` |
| 10 | `analysis-behavioral-data-processing` | **C** | References `codes/functions/behavioral_utils.py` (dead legacy path). |
| 11 | `coding-neuro-omission-bhv-parser` | **C** | References `src/utils/eye_data_mapper.py` (dead). Live: `src/analysis/io/eye_mapper.py` |
| 12 | `analysis-neuro-omission-oculomotor-suite` | **C** | References `src/analysis/oculomotor.py` (dead). |
| 13 | `analysis-global-unit-counts-nwb` | **C** | Inline code is correct, but references `nwb-analysis/skill.md` (lowercase). |
| 14 | `analysis-nwb-read-guardrails` | **C** | References `src/utils/nwb_io.py` (dead). |
| 15 | `analysis-nwb-utils` | **C** | References `src/utils/nwb_io.py` (dead). |
| 16 | `coding-neuro-omission-signal-conditioning` | **C** | References `src/spectral/wavelet_engine.py` (dead). |
| 17 | `design-neuro-omission-advanced-plotting` | **C** | References `src/core/plotting_engine.py` (dead). |
| 18 | `analysis-omission-suite` | **C-** | Top-level routing skill. References stale canonical infrastructure. |
| 19 | `analysis-nwb-data-availability-report` | **C-** | References absent reporting utilities. |
| 20 | `analysis-metadata-extraction` | **C-** | References absent metadata scripts. |
| 21 | `analysis-mmff` | **C-** | References absent Fano factor module. |

### Tier 3: KNOWLEDGE-ONLY (No executable procedure, purely conceptual)

These skills provide domain knowledge but cannot answer "which real files do I touch?"

| # | Skill | Grade | Notes |
|---|---|---|---|
| 22 | `science-neuro-omission-cortical-hierarchy` | **D+** | Rich scientific context. No executable paths. |
| 23 | `science-neuro-omission-active-inference` | **D+** | Theoretical framing only. |
| 24 | `science-neuro-omission-ghost-signals` | **D+** | Good domain context but references absent analysis modules. |
| 25 | `science-neuro-omission-prediction-errors` | **D+** | Same pattern — theory without live file bindings. |
| 26 | `science-neuro-omission-spectral-fingerprints` | **D+** | Theory-heavy, no live paths. |
| 27 | `science-neuro-omission-surprise-latencies` | **D+** | References `src/analysis/latencies.py` (dead). |
| 28 | `predictive-routing` | **D** | CSD-based routing theory. No live implementation. |
| 29 | `neuroscience-actions` | **D** | Biophysical modeling knowledge. References `src/neuro/circuits.py` (dead). |
| 30 | `study-eval-actions` | **D** | Literature evaluation framework. No repo file targets. |
| 31 | `write-neuro-omission-manuscript-suite` | **D** | Manuscript guidance. Aspirational, not executable. |
| 32 | `paper-architecture` | **D** | Paper structure notes. Not actionable. |

### Tier 4: STALE / DEPRECATED (Should be archived or deleted)

| # | Skill | Grade | Notes |
|---|---|---|---|
| 33 | `analysis-neuro-omission-pac-analysis` | **F** | References `src/analysis/pac.py` (dead). Live: `src/f019_pac_analysis/`. |
| 34 | `analysis-neuro-omission-pupil-decoding` | **F** | References `src/analysis/pupil_decoding.py` (dead). Live: `src/f021_pupil_decoding/`. |
| 35 | `analysis-neuro-omission-population-manifolds` | **F** | References `codes/scripts/analysis/` (dead legacy). |
| 36 | `analysis-neuro-omission-functional-connectivity` | **F** | References `src/analysis/connectivity.py` (dead). Live: `src/analysis/lfp/lfp_connectivity.py`. |
| 37 | `analysis-omission-factor-extraction` | **F** | References `src/extract/pipeline_orchestrator.py` (dead). |
| 38 | `analysis-rsa-cka` | **F** | References `src/analysis/geometry.py` (dead). |
| 39 | `analysis-summary-enrichment` | **F** | References `src/extract/report_utils.py` (dead). |
| 40 | `math-neuro-omission-connectivity-metrics` | **F** | References `src/math/connectivity.py` (dead). |
| 41 | `math-neuro-omission-stochastic-metrics` | **F** | References `src/math/information.py` (dead). |
| 42 | `nwb-analysis` | **F** | References `src/data/nwb_loader.py` (dead). Live: `src/analysis/io/loader.py`. |
| 43 | `coding-neuro-omission-decoding-engine` | **F** | References absent decoding modules. |
| 44 | `design-neuro-omission-branding-theme` | **F** | Theme constants are correct but file targets are stale. |

### Tier 5: OUT-OF-SCOPE (Not Omission analysis, but kept for tooling)

| # | Skill | Grade | Notes |
|---|---|---|---|
| 45 | `jax-actions` | **N/A** | JAX framework guidance. Not repo-specific. |
| 46 | `jaxley-actions` | **N/A** | JAXley biophysical modeling. Not repo-specific. |
| 47 | `mac-access` | **N/A** | macOS SSH/remote access. Infrastructure skill. |
| 48 | `hardware-neuro-omission-lab-infrastructure` | **N/A** | Lab hardware reference. Not executable. |
| 49 | `analysis-area-inspection` | **C** | Area audit utility. Partially operational. |

---

## Archived Skills (context/archive/)

| Skill | Location | Status | Recommendation |
|---|---|---|---|
| `bridger-actions` | `context/archive/bridger-actions/SKILL.md` | Archived | ✅ Correctly quarantined. References macOS paths. |
| `frontend-actions` | `context/archive/frontend-actions/SKILL.md` | Archived | ✅ Correctly quarantined. Superseded by `frontend-dashboard`. |
| `github-management-actions` | `context/archive/github-management-actions/SKILL.md` | Archived | ✅ Correctly quarantined. |
| `surf-actions` | `context/archive/surf-actions/SKILL.md` | Archived | ✅ Correctly quarantined. HPC-specific. |
| `wan-video-gen` | `context/archive/wan-video-gen/SKILL.md` | Archived | ✅ Correctly quarantined. |

## Consolidated Skills (context/skills/)

| Skill | Location | Status | Recommendation |
|---|---|---|---|
| `classify_neurons` | `context/skills/consolidated/classify_neurons.md` | **A** | ✅ Well-written. Points to correct threshold (0.4ms). Matches live `putative_classification.py`. |

## Protocols (context/protocols/)

| Protocol | Location | Status | Recommendation |
|---|---|---|---|
| `gamma-impedance-estimation` | `context/protocols/gamma-impedance-estimation.md` | **A-** | ✅ Mathematically rigorous. Self-contained. References live `src/analysis/impedance/estimation.py`. |

---

## Root Cause Analysis

The fundamental problem is **architectural drift without automated synchronization**. The repo underwent a major refactoring from:
- `codes/functions/*` → `src/analysis/*`  
- `src/core/*` → `src/analysis/io/*`, `src/analysis/visualization/*`  
- `src/utils/*` → `src/analysis/io/*`  
- `src/extract/*` → (removed, functionality absorbed into `loader.py`)  
- `src/data/*` → `src/analysis/io/*`  
- `src/math/*` → (removed or not yet implemented)  
- `src/spectral/*` → `src/analysis/lfp/*`  

The skills were written against the **pre-refactoring** topology and were never updated.

---

## Recommended Actions (Priority Order)

### P0: Emergency Path Rebinding (12 skills)
Rebind the **most-used** skills to live paths. Highest impact:

1. `analysis-omission-suite` → Point to `src/analysis/io/loader.py`, `src/f0xx_*/script.py`
2. `nwb-analysis` → Replace `src/data/nwb_loader.py` with `src/analysis/io/loader.py`
3. `analysis-neuro-omission-unit-classification` → Replace `src/analysis/classification.py` with `src/analysis/spiking/putative_classification.py`
4. `analysis-neuro-omission-functional-connectivity` → Replace `src/analysis/connectivity.py` with `src/analysis/lfp/lfp_connectivity.py`
5. `analysis-neuro-omission-pac-analysis` → Point to `src/f019_pac_analysis/`
6. `analysis-neuro-omission-pupil-decoding` → Point to `src/f021_pupil_decoding/`

### P1: Archive or Demote Knowledge-Only Skills (10 skills)
Move to `context/archive/` or reclassify as `[KNOWLEDGE_REF]`:
- `science-neuro-omission-*` (5 skills)
- `predictive-routing`
- `study-eval-actions`
- `write-neuro-omission-manuscript-suite`
- `paper-architecture`
- `neuroscience-actions`

### P2: Delete or Consolidate Redundant Skills (5 skills)
- `analysis-nwb-utils` overlaps heavily with `analysis-nwb-read-guardrails` and `nwb-analysis`
- `math-neuro-omission-connectivity-metrics` and `math-neuro-omission-stochastic-metrics` reference absent modules and duplicate concepts in `analysis-lfp-pipeline`
- `analysis-summary-enrichment` and `analysis-omission-factor-extraction` reference absent infrastructure

### P3: Add Consistency Checker
Create `tests/test_skill_paths.py` that:
1. Parses all `SKILL.md` files for `file:///` links
2. Verifies each path resolves to a real file
3. Fails CI if any skill references a ghost path

---

## Live Codebase Truth Model

For reference, the **actual** live topology that skills should target:

```
src/
├── analysis/
│   ├── io/
│   │   ├── loader.py          ← DataLoader (sessions, signals, output dirs)
│   │   ├── eye_mapper.py      ← EyeDataMapper (BHV2-NWB correlation)
│   │   └── logger.py          ← Logging utilities
│   ├── spiking/
│   │   ├── putative_classification.py  ← E/I classification (0.4ms threshold)
│   │   ├── stats.py                    ← Ramping detection, PSTH stats
│   │   └── omission_hierarchy_utils.py ← Hierarchy-wide spiking utilities
│   ├── lfp/
│   │   ├── lfp_constants.py   ← Timing, bands, conditions, aesthetic colors
│   │   ├── lfp_pipeline.py    ← 15-step LFP processing pipeline
│   │   ├── lfp_preproc.py     ← Preprocessing (filtering, referencing)
│   │   ├── lfp_tfr.py         ← Time-frequency representations
│   │   ├── lfp_connectivity.py ← Granger, coherence, MI
│   │   ├── sfc.py             ← Spike-field coherence
│   │   ├── signal.py          ← Signal utilities
│   │   └── stats.py           ← Statistical tests
│   ├── visualization/
│   │   ├── plotting.py        ← OmissionPlotter (canonical figure wrapper)
│   │   ├── poster_figures.py  ← Poster-specific layouts
│   │   └── lfp_plotting.py   ← LFP-specific plotting
│   ├── laminar/
│   │   └── mapper.py          ← Laminar depth mapping
│   └── impedance/
│       ├── estimation.py      ← Impedance estimation (GAMMA protocol)
│       └── muae.py            ← Multi-unit activity envelope
├── f001_theory/ through f045_laminar_coherence/  ← Figure modules
│   └── script.py, analysis.py, plot.py           ← Per-figure entry points
├── scripts/
│   └── run_pipeline.py        ← Batch orchestrator (NEEDS IMPORT FIXES)
└── main.py                    ← CLI entry point
```

---

**Bottom line**: The skills are intellectually strong but operationally broken. The single highest-yield action is a systematic find-and-replace of the 25 dead paths with their live equivalents. Until that happens, any agent following these skills will waste cycles on import errors and phantom modules.
