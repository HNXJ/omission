---
name: paper-architecture
description: Institutionalizes a "Figure-First" workflow where each figure acts as the foundation for methods, results, and captions.
version: 1.0.0
---

# SKILL: Figure-First Paper Architecture

This skill enforces a rigorous, artifact-centric workflow for scientific writing. The core principle is that **figures are finalized first**, and their documentation serves as the single source of truth for all manuscript sections.

## 📐 The Figure-First Protocol

### 1. Figure Manifest (Documentation)
Every figure (and supplement) MUST have a dedicated markdown file in `docs/figures/`.
- **File Naming**: `FIG_01_Population_Firing.md`
- **Mandatory Sections**:
    - **🎯 Intent**: What biological question does this figure answer?
    - **🔬 Methodology**: The exact scripts, filters, and statistical tests used to generate the data (source of truth for the **Methods** section).
    - **📊 Observations**: Key trends and significant findings (source of truth for the **Results** section).
    - **📝 Caption & Labels**: Draft text for the figure legend.
    - **🗺️ Narrative Context**: How this figure leads to the next one.

### 2. Recursive Drafting
Once a figure's manifest is complete:
1.  **Methods**: Directly transcribed from the "Methodology" section of the manifest.
2.  **Results**: Directly transcribed from the "Observations" section of the manifest.
3.  **Refinement**: If a figure is moved to the supplement or removed, its manifest is updated accordingly, ensuring the paper's narrative remains consistent.

## 📁 Workspace Structure
```text
docs/
├── figures/          # FIG_XX manifests (The Source of Truth)
├── methods/          # Drafted from FIG manifests
├── results/          # Drafted from FIG manifests
└── paper_draft.md    # Compiled manuscript
```

## 🛠️ Usage Example
When starting a new figure:
1.  Generate the plot using an analysis script.
2.  Immediately create `docs/figures/FIG_XX.md`.
3.  Fill out the methodology while the code logic is fresh.
