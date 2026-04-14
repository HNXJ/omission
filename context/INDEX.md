# Documentation Index

This index provides a one-line description of every active document in the `context/` directory.

## 🟢 Overview (Canonical)
- **`overview/project-overview.md`**: Core project purpose, scientific questions, and directory map. (Source of Truth)
- **`overview/data-availability.md`**: Summary of 13 sessions and available data modalities. (Source of Truth)
- **`overview/session-area-mapping.md`**: Anatomical probe-to-area mapping logic and master table. (Source of Truth)

## 🔵 Specs (Canonical)
- **`specs/task-specification.md`**: Detailed stimulus sequence, condition logic, and omission definitions. (Source of Truth)
- **`specs/pipeline-standard.md`**: The 15-step LFP-NWB analysis protocol and timing standards. (Source of Truth)
- **`specs/supplemental-figure-mandate.md`**: SF1–SF13 supplemental figure logic and method mandates. (Source of Truth)
- **`specs/nwb-table-sessions-probes-areas.md`**: Raw NWB-extracted probe/area channel table.

## 🟡 Analysis (Working/Canonical)
- **`analysis/roadmap.md`**: strategic objective, completed work, and future analysis phases. (Source of Truth)
- **`analysis/decoding-framework.md`**: Principles and targets for neural/behavioral decoding.
- **`analysis/methods-spiking.md`**: Methodology for single-unit and population dynamics.
- **`analysis/methods-spectral.md`**: Methodology for TFR, coherence, and Granger causality.
- **`analysis/methods-rsa-cka.md`**: Representational Similarity Analysis and CKA standards.
- **`analysis/methods-behavior.md`**: Oculomotor analysis rules (DVA, Pupil, Saccades).


## 🟠 Context Root (Floating — Pending Classification)
- **`nwb-data-oglo-session-by-session.md`**: Raw session-by-session NWB data log (large, ~10KB). Should be moved to `overview/` or `specs/`.
- **`nwb-data-oglo-session-by-session-table.md`**: Table companion to the above.

## 🟣 Manuscript (Working)
- **`manuscript/results-summary.md`**: Synthesis of findings for Figures 1-6. (Source of Truth)
- **`manuscript/poster-01.md`**: Content for Neural Dynamics/Spectral Omission poster.
- **`manuscript/poster-02.md`**: Content for Oscillations/Predictive Routing poster.

## 🔴 Operations (Working)
- **`operations/troubleshooting.md`**: Solutions for common bugs (e.g., mapping, timing).
- **`operations/implementation-history.md`**: Historical log of pipeline development phases.

## 🔵 Root-Level Docs (Outside context/ — Not Auto-Indexed)
> These files live in `docs/` at the repo root and are not part of the `context/` canonical system.
- **`docs/detailed_population_audit.md`**: Tiered omission neuron census (Tiers 1–4, all 11 areas).
- **`docs/unit-neuron-extended-hierarchical-comparison.md`**: High-stringency O+ table (ratio > 2.0, 9 neurons).
- **`docs/manuscript_analysis_spec.md`**: Tool-level implementation spec for manuscript Figures 1–4.


## ⚪ Navigation & Meta
- **`migration-note.md`**: Detailed record of the 2026-04-06 context/ cleanup pass decisions.
- **`README.md`**: Top-level directory guide and conventions.

---
> [!WARNING]
> `specs/reproducibility.md` was referenced here but **does not exist on disk**. It was listed in `migration-note.md` as "moved" but the destination file is missing. Verify and recreate if needed.
