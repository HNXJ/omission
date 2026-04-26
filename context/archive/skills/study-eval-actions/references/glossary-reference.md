# Neuroscience Predictive Coding Factors -- Glossary Reference

This document provides a human-readable reference of all 36 neuroscience predictive coding factors, organized by hypothesis group. Each factor includes its unique ID, name, definition, measurement tag, and the experimental contexts in which it applies.

**Tag Legend**

- **Quantitative** -- Factor is measured with continuous or numerical evidence.
- **Qualitative** -- Factor is assessed by presence/absence or categorical judgment.
- **Methodological** -- Factor relates to the method of observation rather than the mechanism itself.

**Context Legend**

- **LO** -- Local Oddball paradigm only.
- **LO+GO** -- Both Local Oddball and Global Oddball paradigms.

---

## H1: Predictive Suppression (IDs 1--12)

Factors in this group address the mechanisms by which the brain suppresses neural responses to expected or predictable stimuli.

| ID | Factor Name | Definition | Tag | Contexts |
|----|-------------|------------|-----|----------|
| 1 | Subtractive Inhibition (SST) | Linear suppression of input via somatic inhibition (Somatostatin-mediated). | Quantitative | LO+GO |
| 2 | Divisive Inhibition (PV) | Multiplicative gain reduction (Parvalbumin-mediated). | Quantitative | LO+GO |
| 3 | Inhibition (GABA) | Chloride-mediated inhibition for suppression of prediction. | Quantitative | LO+GO |
| 4 | Habituation to Sequence | Habituation suppresses local oddball response relative to a novel local oddball. | Quantitative | LO |
| 5 | Synaptic Depression (Adaptation) | Passive fatigue of synaptic efficacy due to repetition of stimulus. | Quantitative | LO |
| 6 | Activity Suppression | Reduction in firing rates for expected (predictable) stimuli. | Quantitative | LO+GO |
| 7 | Selective Sharpening | Selective sharpening of signal with suppressing noise (signal-to-noise increases when more predictable). | Quantitative | LO+GO |
| 8 | Alpha/Beta Mediated Suppression | Desynchronization in low-frequency bands due to prediction error. | Quantitative | LO+GO |
| 9 | VIP-Mediated Disinhibition of Prediction-Error | VIP interneurons inhibit SST/PV, releasing pyramidal cells from inhibition (disinhibition due to prediction-error). | Qualitative | LO+GO |
| 10 | Precision Weighting (Gain) | Top-down amplification of error units (attention). | Qualitative | LO+GO |
| 11 | E/I Balance Shift | Dynamic adjustment of excitation/inhibition ratio (more inhibition if predictable). | Quantitative | LO+GO |
| 12 | Omission Response | Neural response generated solely by the absence of an expected stimulus (lack of prediction-mediated suppression). | Quantitative | LO+GO |

---

## H2: Feedforward Error Propagation (IDs 13--24)

Factors in this group address how prediction-error signals are generated and transmitted in the feedforward (ascending) direction through the cortical hierarchy.

| ID | Factor Name | Definition | Tag | Contexts |
|----|-------------|------------|-----|----------|
| 13 | Feedforward Deviance Detection | Deviance signal propagation in the feedforward direction (separate from adaptation). | Quantitative | LO+GO |
| 14 | Feedforward AMPA | Fast excitatory drive conveying the primary error signal, in the feedforward direction. | Quantitative | LO+GO |
| 15 | Feedforward NMDA | Voltage-dependent amplification (bursting) of feedforward error signals. | Quantitative | LO+GO |
| 16 | Feedforward Ascending Gamma | Synchronization of feedforward errors in the gamma band (30--90 Hz). | Quantitative | LO+GO |
| 17 | Feedforward Specific Error | Prediction-error is specifically a feedforward signal. | Quantitative | LO+GO |
| 18 | Supragranular Activity (L2/3) | Error signaling neurons in Layer 2/3 of the cortical column. | Quantitative | LO+GO |
| 19 | Granular Activity (L4) | Prediction error first signals to neurons in Layer 4 of the cortical column. | Quantitative | LO+GO |
| 20 | Feedforward Directed Connectivity | Granger/Transfer Entropy showing increased lower-to-higher flow of prediction error. | Quantitative | LO+GO |
| 21 | Feedforward Activation | Feedforward activation from lower-order to higher-order areas. | Quantitative | LO+GO |
| 22 | Ascending Latency Shift | Systematic delay in error onset ascending the hierarchy. | Quantitative | LO+GO |
| 23 | Feedforward Error Propagation | Error signal is feedforward. | Qualitative | LO+GO |
| 24 | Ascending Cortical Hierarchy | Presence of prediction error in lower-order cortex ascending to higher-order cortex. | Qualitative | LO+GO |

---

## H3: Ubiquity (IDs 25--36)

Factors in this group address whether the predictive coding mechanism is a universal, consistent feature across cortical areas, hierarchical levels, modalities, and species.

| ID | Factor Name | Definition | Tag | Contexts |
|----|-------------|------------|-----|----------|
| 25 | Canonical Microcircuit Consistency | L2/3 Error and L5/6 Prediction motif repeats across areas. | Qualitative | LO+GO |
| 26 | Hierarchical Invariance | Mechanism functions identically in the cortical hierarchy from V1 to PFC. | Qualitative | LO+GO |
| 27 | Hierarchical Activity Consistency | Prediction-error related activity is present across all of the cortical hierarchy. | Quantitative | LO+GO |
| 28 | Hierarchical CSD Consistency | Laminar cortex current source density profiles match across levels. | Quantitative | LO+GO |
| 29 | Hierarchical Cross-Scale Consistency | Effects observable in both single units and population LFP. | Methodological | LO+GO |
| 30 | Low-Level Presence (V1) | Mechanism is also robustly detectable in primary sensory cortex. | Qualitative | LO+GO |
| 31 | Mid-Level Presence (V2/V4) | Mechanism is also robustly detectable in mid-level association areas. | Qualitative | LO+GO |
| 32 | High-Level Presence (PFC) | Mechanism is also robustly detectable in executive/frontal areas. | Qualitative | LO+GO |
| 33 | Cross-Modal Generality | Mechanism is present across cortical hierarchy for sensory modalities (visual, auditory, somatosensory). | Qualitative | LO+GO |
| 34 | Species Hierarchical Generality | Mechanism is conserved across the cortical hierarchy of species (e.g., mouse vs. primate). | Qualitative | LO+GO |
| 35 | Temporal Stability (Hierarchical) | Effect is stable over long recording sessions across the cortical hierarchy (not transient). | Quantitative | LO+GO |
| 36 | Hierarchical Order | Effect is not driven solely in one hierarchical pole. | Qualitative | LO+GO |

---

## Summary Statistics

| Hypothesis Group | ID Range | Total Factors | Quantitative | Qualitative | Methodological |
|------------------|----------|---------------|--------------|-------------|----------------|
| H1: Predictive Suppression | 1--12 | 12 | 10 | 2 | 0 |
| H2: Feedforward Error Propagation | 13--24 | 12 | 10 | 2 | 0 |
| H3: Ubiquity | 25--36 | 12 | 4 | 7 | 1 |
| **Total** | **1--36** | **36** | **24** | **11** | **1** |
