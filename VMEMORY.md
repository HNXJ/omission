---
name: vmemory
description: The long-term memory, personality, and foundational knowledge base of the Gemini CLI assistant for this workspace. Formatted as a skill to be easily referenced or loaded when deep context is needed.
---

# VMEMORY: Long-Term Context & Personality

This document serves as the extended "personality" and long-term memory bank. It stores the foundational aesthetic, architectural, and procedural knowledge that doesn't need to clutter the immediate working memory (`GEMINI.md`) but is essential for maintaining a consistent, highly-tailored user experience.

## 1. Aesthetic & Visual Identity
- **Madelane Golden Dark**: The strict visual standard for UIs, plots, and websites.
  - **Primary Gold**: Vanderbilt Gold (`#CFB87C`)
  - **Background**: Deep Black (`#000000`)
- **Plotting Standards**:
  - Always use appropriate smoothing (e.g., 1D Gaussian `sigma=0.5` or `1.0`) depending on the data type.
  - Titles must be comprehensive but clean (e.g., including Kappa values, specific target frequencies like 38Hz).
  - Use `aspect='auto'`, `origin='lower'` for PSD heatmaps to align with neuro-standard spectrograms.

## 2. Infrastructure & Compute
- **The Engine**: Office M3 Max (128GB RAM) is the powerhouse.
  - Setup as a dedicated automated local LLM engine (Llama 3 / Qwen) via LM Studio and Cloudflare.
- **Remote Access**:
  - Cloudflare Tunnels are used for continuous connection.
  - Custom command `/office` proxies prompts directly to the local LLM (Qwen 3.5 122B).
  - Wan 2.1 14B models are used for high-end video generation.
- **Background Execution**: "Deep" tasks (GSDR training loops >100 trials, Wan rendering, massive dataset analysis) *must* be sent to the background (`is_background=True`).
- **Multi-Device Orchestration**:
  - **Branching Rule**: The Windows PC (Local) commits exclusively to branch `W`. The Gemini CLI Agent (Main) controls the `main` branch and is responsible for auditing, editing, and merging `W` into `main`.
  - **Task Dispatch**: Use secure messaging (e.g., GitHub-based command queues or Cloudflare API) to send instructions to the Office Mac or Windows PC for heavy lifting.

## 3. Core Research Themes (Neuroscience & ML)
- **Project GSDR01**: 
  - Focused on the Genetic Stochastic Delta Rule (`AAE.gsdr` package).
  - Validating the biological realism of a 50-neuron NetEIG model (E, IG, IL populations).
  - **Goal**: Achieve high-frequency Gamma (38-40Hz) during stimulation while driving inter-neuron synchrony (Fleiss' Kappa) to biological minimums (~0.1).
  - **MCDP**: Mutual-correlation dependent plasticity. A critical biophysical scaling factor.
- **Project Study-Eval**: 
  - Framework for systematic research paper evaluation (`study-eval-actions`).
  - Uses the 36-factor TcGLO predictive coding glossary (H1, H2, H3) across LO/GO contexts.
  - Literature Database: `/Users/hamednejat/workspace/HPC/HPC/Data/hpc_table_260225.csv`
- **Biological Data Highlights**:
  - Macaque MT/MST, PFC, FEF, V4 electrophysiology (Sessions 0818, 0825, 0831, 0901, 0720).
  - Raw data stored in `workspace/Analysis/nwb/nwbdata/` as large NWB files (90-200GB).
  - Probe Mappings (standard):
    - **Session 230831**: probe_0 (FEF), probe_1 (MT/MST), probe_2 (V4/TEO).
    - **Session 230901**: probe_0 (PFC), probe_1 (MT/MST), probe_2 (V3/V4).
    - **Session 230720**: probe_0 (V1/V2), probe_1 (V3d/V3a).
  - Parameters: Sampling Rate = 1000Hz (LFP/MUAe), Electrode Spacing = 40um (0.04mm).
- **Spectrolaminar Motif Identification**:
  - Tool: `vFLIP2` class in `AAE/NWB/jnwb.py`.
  - Analyzes the spectral crossover between Deep (Alpha/Beta) and Superficial (Gamma) layers.


## 4. Operational "Personality" (How to Act)
- **Proactive & Assertive**: Do not just point out errors; write the script, run the analysis, and present the visualized result.
- **Git-First**: The `AAE` package and `hnxj-gemini` skills must be perfectly synchronized with GitHub. Newly written functions go into the repo *immediately* after passing tests.
- **Surgical Precision**: Be highly specific when replacing code. Don't overwrite whole files if a small regex/replace will do.
- **Collaborative Brainstorming**: While a script is running in the background, use the "free" time to update skills, draft documentation, or ask about the next architectural step.
