# VMEMORY: Project Status and Methodological Overview

*Updated: April 9, 2026 | Refactoring in Progress*

---

## 🧠 Core Methodology Overview

This project is undergoing refactoring to establish a clear and consistent methodology for analyzing neurophysiological data. The goal is to develop a robust, reproducible pipeline for investigating neural representations of predicted but absent stimuli (omissions) across multiple cortical areas.

Current efforts focus on:
- Establishing a single, canonical accessor for neural signals (`get_signal_conditional`).
- Ensuring LFP functions are either fully implemented or explicitly marked as placeholders.
- Sanitizing deprecated scripts and removing local machine assumptions.
- Making all documentation truthful and up-to-date with the current state of the repository.

### Current LFP Processing Parameters:
- **Canonical LFP sampling rate**: `FS_LFP = 1000.0 Hz` (defined in `lfp_constants.py`)
- **Frequency Bands** (authoritative, defined in `lfp_constants.py`):
  - Theta: 4–8Hz
  - Alpha: 8–13Hz
  - Beta: 13–30Hz
  - Gamma: 35–70Hz

## 🎨 Aesthetic & Technical Mandates
Refer to `GEMINI.md` for current aesthetic and technical mandates, including plotting standards.

## 📋 Session Metadata
- N=13 sessions, multi-area dense laminar, Utah/linear probes
- Alignment anchor: code 101.0 = photodiode p1 onset = 0ms
- Sampling rate: `FS_LFP = 1000.0 Hz` (hardcoded in `lfp_constants.py`)
- Electrode table: `location` column → area assignment; `depth` → laminar position