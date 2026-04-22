---
name: paper-architecture
description: Manuscript drafting framework enforcing a "Figure-First" protocol to ensure consistency between data visualization, methods, and results.
---
# skill: paper-architecture

## When to Use
Use this skill when drafting manuscripts or technical reports. It is mandatory for:
- Implementing the "Figure-First Protocol" where data visualization drives the narrative.
- Creating and maintaining "Figure Manifests" in `docs/figures/`.
- Ensuring 1:1 correspondence between code methodology and manuscript text.
- Organizing the hierarchy of Main vs. Supplementary figures.

## What is Input
- **Analysis Figures**: Finalized interactive HTML plots or SVG exports.
- **Experimental Metadata**: Stimulus timings, subject counts, and recording parameters.
- **Narrative Goals**: The biological questions being addressed (e.g., "Predictive Routing in V1").

## What is Output
- **Figure Manifests**: Dedicated `.md` files for every figure containing Intent, Methodology, Observations, and Caption.
- **Draft Sections**: Compiled Methods and Results sections derived directly from manifests.
- **Compiled Manuscript**: The final `paper_draft.md` tracking the full narrative arc.

## Algorithm / Methodology
1. **Manifest Creation**: For every figure `FXXX`, create `docs/figures/FXXX_manifest.md`.
2. **Methodology Lock**: Transcribe exact scripts, filters, and window sizes used during analysis into the manifest.
3. **Observation Logging**: Record key statistical findings and biological implications immediately after analysis.
4. **Recursive Compilation**: Draft Results and Methods sections by summarizing and connecting the manifests.
5. **Branding Check**: Ensure all figures follow the "Madelane Golden Dark" aesthetic.

## Placeholder Example
```markdown
# Figure Manifest: F012_Laminar_Alpha_Beta
## Intent
To demonstrate the deep-layer dominance of feedback-related oscillations.

## Methodology
- Script: `src/analysis/laminar_spectrum.py`
- Window: Delay interval d1 (1531-2031ms).
- Stats: Paired t-test between L2/3 and L5/6.

## Observations
- Alpha power is 45% higher in deep layers (p < 0.001).
```

## Relevant Context / Files
- [design-neuro-omission-branding-theme](file:///D:/drive/omission/.gemini/skills/design-neuro-omission-branding-theme/skill.md) — For aesthetic compliance.
- [docs/paper_outline.md](file:///D:/drive/omission/docs/paper_outline.md) — The high-level structure of the current manuscript.
