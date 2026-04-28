# Methods: Phase 1 - Data Acquisition & Preprocessing

## 🔬 Recording Infrastructure
Neural activity was recorded using high-density linear probes (128 channels) inserted into 11 distinct cortical areas across the visual-prefrontal axis, including V1, V2, V3, V4, MT, MST, TEO, FST, FEF, and PFC. Recordings were performed in two adult macaques (Macaca mulatta) performing a rhythmic visual task.

## 🔬 Behavioral Task & Omission Logic
The animals were trained to fixate on a central point while sequences of four visual stimuli (P1, P2, P3, P4) were presented at a rhythmic rate of 2Hz (500ms stimulus-to-stimulus interval). Three sequence types were utilized:
1. **AAAB (Standard)**: Rhythmic repetition of stimulus A followed by a deviant B.
2. **BXBA (Alternative)**: Rhythmic repetition of B followed by deviant A.
3. **AXAB (Omission)**: Stochastic omission of the second stimulus (P2), resulting in a "predicted absence."

## 🔬 Population Selection (Stable-Plus)
To ensure high-fidelity analysis, we restricted all analytical operations to a vetted "Stable-Plus" neuronal population. Units were included only if they met the following criteria:
- **Firing Rate (FR)**: > 1Hz across the entire session.
- **Signal-to-Noise Ratio (SNR)**: > 0.8.
- **Presence Ratio**: 100% trial presence.
A total of 842 units passed these rigorous stability filters across 13 sessions.

## 🔬 Statistical Tiers ($S_k$)
Significant modulation was determined using a tiered statistical framework ($S_k$):
- **Awesome (Tier 1)**: $p < 1e-5$, confirmed via permutation test (1000 shuffles).
- **Gold (Tier 2)**: $p < 0.01$.
- **Silver (Tier 3)**: $p < 0.05$.
- **Fail**: $p \ge 0.05$ or presence of data artifacts (NaN/Inf).
