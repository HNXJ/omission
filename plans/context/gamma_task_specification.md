# 🧠 Task Specification: Sequential Visual Omission Paradigm (Gamma-Standard)

## 🧩 1. OVERVIEW
This task is a **controlled sequential visual omission paradigm** designed to probe the neural implementation of **predictive coding / active inference** in the primate brain. The key experimental manipulation is the **removal of an expected stimulus (omission)** within a temporally structured sequence while maintaining identical sensory input conditions (gray screen), enabling isolation of **pure top-down predictive signals**.

## 🎯 2. OBJECTIVE
The subject (monkey) must:
* Maintain fixation on a central fixation point for ~4500 ms.
* Passively observe a sequence of visual stimuli.
* Receive reward upon successful fixation completion.

**Critical Design Principle**:
`Sensory Input = constant during omission`
`Neural Activity ≠ constant`
👉 **Any neural change during omission = internal model / prediction signal.**

## 🖥️ 3. VISUAL STIMULUS SPECIFICATION
* **Type**: Circular drifting grating (2 Hz).
* **Orientations**: 45° (A) and 135° (B).
* **Background**: Gray (luminance matched to stimulus).
👉 **Ensures no photodiode change during omission; no bottom-up signal.**

## 🧠 4. OMISSION DEFINITION
* **Logic**: `Omission = Expected Stimulus − Sensory Input`.
* **Poster Insight**: Beta synchronization ↑, Gamma unchanged.
* **Functional Meaning**: Pure **top-down inference state**.

## 🧬 5. NEURAL REPRESENTATION FRAMEWORK
| Signal | Interpretation |
| :--- | :--- |
| **SPK** | Sparse encoding (~<2% omission responsive). |
| **MUAe** | Robust local population response. |
| **Gamma** | Feedforward / Sensory (stable during omission). |
| **Beta** | Feedback / Prediction (**increases during omission**). |
| **Alpha** | Inhibitory modulation (suppressed during omission). |

## 🧠 6. CORTICAL HIERARCHY
* **Low**: V1, V2.
* **Mid**: V4, MT, MST, TEO, FST.
* **High**: FEF, PFC.
👉 **Prediction signal strength ↑ with hierarchy (origination in High cortex).**

## ⏱️ 7. TEMPORAL STRUCTURE (ms)
| Event | Time |
| :--- | :--- |
| Fixation start | -500 |
| **p1 (Code 101.0)** | 0 |
| d1 | 531 |
| p2 | 1031 |
| d2 | 1562 |
| p3 | 2062 |
| d3 | 2593 |
| p4 | 3093 |
| d4 | 3624 |
| End fixation | 4124 |

## 👻 8. "GHOST SIGNAL"
`Ghost Signal = Neural activity during identical sensory input but different expectation`.
Omission produces structured oscillatory changes, not random silence.

## 📊 9. ANALYSIS PIPELINE EXPECTATIONS
1. **Time-Frequency**: Multitaper/Wavelet for Theta, Alpha, Beta, Gamma.
2. **Correlation**: Inter-area matrices (Beta → omission correlation).
3. **Spike Analysis**: PSTH classification (Stim-excited, Stim-inhibited, Omission-selective).
4. **Statistics**: Cluster-based permutation tests, Latency comparisons.

## 🚀 FINAL SUMMARY
Omission reveals that the brain encodes predictions not through firing rate magnitude, but through **network-level oscillatory coordination** (Beta synchrony, top-down dominant).
