# PENDING TASK
Target Agent: `antigravity`
Author Agent: `omission-core`
Date: 2026-04-22

## Task: Master Execution Plan for Laminar Connectivity Suite (f044-f045)

Hello `antigravity`. I have reviewed your architectural draft for f044 and f045, and verified your excellent visual QA fixes for f042. Your proposed methodologies—Tort's Modulation Index (MI) with surrogate z-scoring for PAC, and Imaginary Coherence (iCOH) for inter-areal connectivity—are perfectly aligned with our rigor standards.

I have expanded your draft into a **Master Execution Payload** by injecting our specialized institutional skills and explicit execution directives. 

**You are now cleared for execution based strictly on the comprehensive instructions below.**

---

## 1. Context & Skill Injection (MANDATORY)
Before writing any computation code, you MUST activate and leverage the following institutionalized skills (using the `activate_skill` tool or your internal memory):
- **`analysis-neuro-omission-pac-analysis`**: Use this skill to strictly enforce the Tort MI algorithm, the exact 200-surrogate shuffling methodology, and the specific phase/amplitude frequency bins for Deep-to-Superficial PAC.
- **`analysis-neuro-omission-functional-connectivity`**: Use this skill to correctly compute Imaginary Coherence (iCOH) to eliminate volume conduction, specifically between V1 layers and PFC layers.
- **`laminar-stratification`**: Continue enforcing the Canonical LaminarMapper logic (Superficial [0-40], L4 [40-70], Deep [70-128]).
- **`plotting-visualization-standards`**: All outputs must be interactive HTMLs using the Madelane Golden Dark aesthetic (#CFB87C / #9400D3) with Kaleido-Free exports. Polar plots must have explicit borders and visible text.

## 2. Phase 5.5: Data Ingestion & Alignment
- **Target Population**: Restrict analysis to the 5,416 'Stable-Plus' high-fidelity units (`D:\drive\outputs\oglo-8figs\f041-laminar-analysis\strict_population_summary.csv`).
- **Memory Management**: Use `mmap_mode='r'` to lazy-load the LFP arrays from `D:\drive\data\arrays`. DO NOT load full arrays into RAM.
- **Family-Aware Timing**: Ensure your analysis windows are locked to the specific omission onset indices (p2=1031ms, p3=2062ms, p4=3093ms relative to P1). Baseline is strictly -250ms to -50ms from omission onset.

## 3. Phase 5.6: Laminar Phase-Amplitude Coupling (f044)
**Objective**: Quantify how low-frequency phase modulates high-frequency amplitude within the strata of V1 and PFC.
**Methodology**:
1. Filter the localized LFP into low-frequency phase bands (e.g., Delta 0.5-4Hz, Theta 4-8Hz) and high-frequency amplitude bands (e.g., Gamma 40-80Hz).
2. Compute the Tort Modulation Index (MI) for Deep-layer phase vs. Superficial-layer amplitude.
3. Compute MI for 200 chunk-shuffled surrogates to generate a null distribution, then z-score the empirical MI against this distribution.
**Output**: Save to `D:\drive\outputs\oglo-8figs\f044-laminar-pac\f044_laminar_pac.html`. Include commodulograms (phase vs. amplitude frequency matrices) showing significant z-scored coupling.

## 4. Phase 5.7: Laminar Functional Connectivity (f045)
**Objective**: Measure inter-areal spectral coherence between V1 and PFC strata during omissions.
**Methodology**:
1. Compute the cross-spectral density between specific layer pairs (e.g., V1 Deep to PFC Deep, V1 L4 to PFC Superficial).
2. Extract the **Imaginary Coherence (iCOH)** to isolate true interactions from volume conduction. Focus heavily on the Beta (15-30Hz) band, which signifies top-down feedback.
**Output**: Save to `D:\drive\outputs\oglo-8figs\f045-laminar-coherence\f045_laminar_coherence.html`. Use matrix heatmaps or edge-bundled graphs to visualize the layer-to-layer iCOH strengths.

## 5. Resolution & Version Control Routing (CRITICAL)
Upon successful execution and visual QA of both `f044` and `f045`:
1. Generate the corresponding `README.md` files summarizing the execution.
2. Update the dashboard manifest using `D:\drive\omission\src\scripts\generate_dashboard_manifest.py`.
3. Rename this payload to `RESOLVED_antigravity_execute_laminar_connectivity_suite.md`.
4. **VCS MANDATE:** You must automatically execute a git commit, pull, and push for the `omission` repository to save the generated scripts and logs. Use the command: `git add . ; git commit -m "feat: execute Phase 5 f044-f045 Laminar Connectivity" ; git pull --rebase ; git push`.
5. Halt execution and report your status.
