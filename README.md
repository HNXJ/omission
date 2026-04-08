# Omission Hierarchy

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview
A comprehensive Python-based analysis suite for large-scale neurophysiological investigations into the neural representations of predicted but absent stimuli (omissions). This project analyzes multi-scale data (Spikes, MUAe, LFP, and Oculomotor behavior) across 11 cortical areas (V1 to PFC) during a sequential visual omission paradigm to map the hierarchy of predictive coding and active inference.

## Repository Architecture

The repository is divided into two primary domains: `codes/` (the execution environment) and `context/` (the documentation source of truth).

### `codes/` - Source Code & Analysis Package
The codebase is structured to enforce separation of concerns, portability, and reproducibility:
* **`config/`**: Centralized path and environment configuration (`paths.py`, `settings.py`).
* **`functions/`**: Reusable, topic-driven subpackages:
  * `lfp/`: 15-step pipeline, preprocessing, TFR, connectivity, and laminar mapping.
  * `spiking/`: Mean-Matched Fano Factor (MMFF) variability quenching and spike-LFP coordination.
  * `behavior/`: Oculomotor analysis (DVA, Pupil, Saccades).
  * `io/` & `events/`: NWB extraction, metadata handling, and strict photodiode timing validation.
  * `visualization/`: Standardized Plotly figure generation adhering to project aesthetic mandates.
* **`scripts/`**: Runnable entrypoints organized by intent:
  * `pipelines/`: Canonical orchestrators for major analysis tracks.
  * `analysis/`: Reusable analysis runners (e.g., decoding, manifold trajectories).
  * `qc/`: Quality control, timing verification, and data inspection tools.
* **`tests/`**: Unit and integration tests for core extraction logic.

### `context/` - Source of Truth Documentation
Detailed scientific planning and specifications reside in the `context/` directory.

## Canonical Entrypoints

The analysis workflow is driven by canonical orchestration scripts.

- **LFP 15-Step Pipeline**: `codes/scripts/pipelines/master-lfp-pipeline.py`
- **Spiking Dynamics & Quenching**: `codes/scripts/pipelines/run-spiking-dynamics-suite.py`
- **Eye & Behavioral Proxies**: `codes/scripts/pipelines/run-omission-dynamics-lfp-eye.py`
- **Population Decoding**: `codes/scripts/analysis/decode-omission-identity.py`
- **Data QC & Validation**: `codes/scripts/qc/verify-trial-counts.py`

## Data Flow & Reproducibility

1. **Path Configuration**: 
   The suite relies on `codes/config/paths.py`. It dynamically resolves data and output directories based on environment variables. To run the code on a new machine, set:
   - `OMISSION_DATA_DIR`: Path to the directory containing raw NWB and behavioral files.
   - `OMISSION_OUTPUT_DIR`: Path where generated figures, reports, and processed arrays will be saved.
   If unset, they default to relative paths `data/` and `outputs/` at the repository root.

2. **Ingestion & Validation**:
   Raw NWB files are validated against a strict schema. The Golden Standard timing alignment uses the onset of Presentation 1 (Code 101.0) as `t=0ms`.

3. **Processing & Caching**:
   Heavy intermediate steps (like TFR spectrograms or binned spike counts) are aggregated into structured representations (e.g., `global_processed_data`) to prevent redundant computation across figure generation steps.

4. **Statistical Rigor**:
   - LFP spectral comparisons utilize 2D Cluster-based permutation testing to control Family-Wise Error Rates (FWER).
   - Neural variability quenching utilizes the Mean-Matched Fano Factor algorithm to decouple variance changes from firing rate modulations.
   - PSTHs are smoothed using Gaussian kernels to avoid phase-shift artifacts.

## Installation

```bash
git clone https://github.com/HNXJ/omission.git
cd omission
pip install -r requirements.txt
```
