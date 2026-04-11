# Omission: Neural Dynamics & Predictive Routing

This repository contains the analysis codebase for investigating neural dynamics during visual omission tasks, as detailed in our research on spectral aspects of predictive routing.

## Project Status

This project is currently in a state of active development and maintenance. The codebase is organized for reproducible analysis, covering LFP preprocessing, TFR computation, and inter-area spectral connectivity.

## Repository Structure

- `codes/`: Core source code for the project.
    - `functions/`: Canonical utilities for I/O, LFP preprocessing, TFR analysis, and plotting.
    - `scripts/`: Analysis entrypoints and pipelines for figure generation and QC.
    - `tests/`: Basic validation scripts for core components.
- `context/`: Project documentation, plans, and research notes.
- `outputs/`: Staging area for figures and analysis results.

## Conventions

- **Time**: P1 onset is the anchor at `0ms`.
- **Sampling**: Canonical LFP sampling rate (`FS_LFP`) is `1000.0 Hz`.
- **Areas**: The canonical area order is `['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']`.
- **Plotting**: Standardized figures use the Madelane Golden Dark palette and `plotly_white` theme.

## Getting Started

To set up your environment, ensure you have the necessary dependencies installed (see `requirements.txt`). Use the provided scripts in `codes/scripts/pipelines/` to run standardized analyses on NWB-formatted session data.

## Documentation Map

- `context/overview/project-overview.md`: High-level project goals and roadmap.
- `context/specs/pipeline-standard.md`: Detailed specification of the analysis pipeline.
- `context/manuscript/`: Drafts and summaries of related research findings.

For further assistance, consult the repository index report (`omission_repo_index_report.md`) or the individual skill documentation in `.gemini/skills/`.
