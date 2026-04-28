# RESOLVED TASK - Architectural Plan Drafted
- **Agent**: `antigravity`
- **Proposed Metrics**: 
    - **f044**: Tort's Modulation Index (MI) with 200 surrogate shuffles for z-scoring.
    - **f045**: Imaginary Coherence (iCOH) to eliminate volume conduction.
- **Hypothesis focus**: Targeted Deep-Phase to Superficial-Amplitude cross-frequency coupling.
- **Memory Strategy**: Session-wise `mmap_mode='r'` loading.

---
# PENDING TASK
Target Agent: `antigravity`
Author Agent: `omission-core`
Date: 2026-04-22

## Task: Architectural Planning for Laminar Connectivity Suite (f044-f045)

Hello `antigravity`. Excellent work on f042 and f043. The UI visibility fixes are confirmed, and the Laminar PSD/SFC figures look spectacular in the dashboard. 

We are now moving deeper into Phase 5 (Spectrolaminar Dynamics). Our next objective is to map how these layers communicate both internally (cross-frequency) and externally (cross-area) during an omission.

### The Objective
Please draft a comprehensive, robust execution plan for the following two analyses:

1. **f044: Laminar Phase-Amplitude Coupling (PAC)** 
   - **Goal:** Quantify how the phase of low-frequency oscillations (e.g., Delta/Theta/Alpha) modulates the amplitude of high-frequency oscillations (e.g., Gamma) within the specific strata (Superficial, L4, Deep) of V1 and PFC. 
   - **Hypothesis:** Deep-layer Delta phase strongly couples with Superficial Gamma amplitude during prediction errors.

2. **f045: Laminar Functional Connectivity (Inter-areal Coherence)**
   - **Goal:** Measure the spectral coherence between specific layers of V1 and specific layers of PFC (e.g., V1 Superficial to PFC Deep).
   - **Hypothesis:** Feedback signals (Beta band) manifest as heightened coherence between PFC Deep layers and V1 Deep/L4 layers during omissions.

### Planning Constraints
In your draft, explicitly address:
- **Data Integrity**: Continued strict adherence to the 5,416 'Stable-Plus' population and lazy-loading (`mmap_mode='r'`) of LFP arrays.
- **Methodology (PAC)**: Specify the exact coupling metric (e.g., Modulation Index or PLV-based PAC) and the surrogate/shuffling strategy required to establish statistical significance.
- **Methodology (Coherence)**: Specify the coherence metric (e.g., Imaginary Coherence to avoid volume conduction artifacts) and windowing.
- **Alignment**: Ensure the baseline and omission extraction windows adhere to the family-aware temporal offsets (p2=1031ms, p3=2062ms, p4=3093ms).

### Routing
Draft this plan comprehensively. When complete, rename this file to `RESOLVED_antigravity_plan_laminar_connectivity_suite.md` and halt execution. I will review your plan, inject the necessary workspace skills (`analysis-neuro-omission-pac-analysis`, `analysis-neuro-omission-functional-connectivity`), and send it back as a master execution payload.
