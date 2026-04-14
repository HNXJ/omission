---
name: neuro-analysis
description: A skill for analyzing and plotting neurophysiology data from omission tasks. Includes scripts for classifying neuron response types and plotting results.
---

# Neurophysiology Analysis Skill

This skill provides a suite of tools for analyzing spike train data from neurophysiology experiments, particularly those involving sequential stimuli and omission paradigms.

## Bundled Resources

- **Scripts (`scripts/`):** A collection of Python scripts for performing analysis and generating plots.
- **References (`references/`):** Contains `TASK_DETAILS.md`, which provides essential details about the experimental paradigm, including stimulus timings and condition definitions. **Consult this file before using the scripts** to understand the data's structure.
- **Assets (`assets/`):** Contains a small sample dataset (`assets/data/`) to demonstrate the functionality of the scripts.

## Mapping & Analysis Rules

To ensure accurate results, this skill implements the following definitive mapping rules:

1. **Probe Identification**: Uses the 128-channels-per-probe rule (`probe_id = peak_channel_id // 128`).
2. **Local Indexing**: Automatically maps NWB global unit indices to local indices (0..N) to match the structure of exported `.npy` probe files.
3. **Multi-Area Probes**: Splits probes with combined labels (e.g., "V1, V2") into equal channel segments.
4. **Aliases**: Maps Area **DP** to **V4** and splits **V3** into **V3d** and **V3a**.

---

## Workflows

All scripts are designed to be run from the project's root directory.

### 1. Plotting Average Firing Rate

To visualize the average firing rate across all neurons for different conditions.

**Script:** `neuro-analysis/scripts/plot_average_spiking.py`

**Usage:**
```bash
python neuro-analysis/scripts/plot_average_spiking.py --data_dir <path_to_data> --output_dir <path_to_figures>
```
- `--data_dir`: (Optional) Path to the directory containing the `.npy` spike data. Defaults to the sample data in `neuro-analysis/assets/data`.
- `--output_dir`: (Optional) Directory where the output plots will be saved. Defaults to `figures/`.

**Example:**
```bash
# Run on the full dataset and save to the default figures folder
python neuro-analysis/scripts/plot_average_spiking.py --data_dir data/ --output_dir figures/
```

### 2. Classifying Neuron Response Types

To count neurons based on their firing rate changes in response to stimuli or omissions.

#### a) Stimulus Response (Positive/Negative)

**Script:** `neuro-analysis/scripts/classify_stimulus_response.py`

**Usage:**
```bash
python neuro-analysis/scripts/classify_stimulus_response.py --data_dir <path_to_data>
```
- `--data_dir`: (Optional) Path to the directory containing all `.npy` spike data. Defaults to the sample data.

#### b) Omission Response (Strict)

**Script:** `neuro-analysis/scripts/classify_omission_response.py`

**Usage:**
```bash
python neuro-analysis/scripts/classify_omission_response.py --data_dir <path_to_data>
```
- `--data_dir`: (Optional) Path to the directory containing all `.npy` spike data. Defaults to the sample data.

### 4. Primate Raster + Trace Suite (Standard Visualization)

To generate the publication-grade "Primate Suite" featuring 3 rasters and 3 grouped PSTH traces.

**Script:** `neuro-analysis/scripts/plot_raster_trace_suite.py`

**Usage:**
```bash
python neuro-analysis/scripts/plot_raster_trace_suite.py
```
- This script implements the **Primate Suite** template, providing a unified 6-panel visualization for single-unit auditing.
- It includes Gaussian-convolved traces (`sigma=50ms`) and shaded ±SEM patches.
