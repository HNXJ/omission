# Figure 4: Neural Variability Hierarchy & Post-Omission Scaling

## 🎯 Intent
To determine if cortical variability follows a structured hierarchy during unexpected sensory voids and to test the hypothesis that omissions refine predictive precision, leading to enhanced quenching in subsequent stimulus presentations.

## 🔬 Methodology
- **Data Source**: 13 NWB sessions, 6,040 mapped neurons.
- **Metric**: Across-trial variance (time-resolved) for each neuron.
- **Baselining**: Hard-corrected to 0 during the pre-stimulus fixation window (-500ms to 0ms).
- **Hierarchy Analysis (4A)**: Average baseline-corrected variance during the omission window (p2 of RXRR, p3 of RRXR, p4 of AAAX) across all units per area.
- **Scaling Analysis (4B)**: Comparison of variability during stimuli immediately following an omission (e.g., p3 after omit p2) vs. standard presentations (p3 of RRRR).
- **Statistics**: Mean and SEM calculated across the neuron population within each of the 11 areas.

## 📊 Observations
- **4A (Omission Hierarchy)**: Areas show a clear progression in variability magnitude, typically mirroring the firing rate latency hierarchy from V1 to PFC.
- **4B (Post-Omission Scaling)**: Stimulus presentations immediately following an omission show a significant reduction in variability compared to standard trials, supporting the "Refined Prediction" hypothesis.

## 📝 Caption & Labels
**Figure 4. Hierarchy of Stability and Predictive Precision.** (A) Baseline-corrected variability (ΔVariance) across 11 brain areas during the omission window. (B) Comparison of variability during standard stimulus presentations (blue) vs. stimuli immediately following an omission (orange). Error bars indicate ±SEM across neurons.

## 🗺️ Narrative Context
Figure 4 establishes that omissions are not just "passive voids" but active events that refine the network's predictive state, leading into the population manifold analysis in Figure 5.
