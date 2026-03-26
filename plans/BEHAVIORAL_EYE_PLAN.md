# Plan: Behavioral Eye-Signal Classification & Directionality

## 🎯 Objective
Decode task context, stimulus identity, and internal expectations using high-fidelity oculomotor signals (Eye-X, Eye-Y) and Pupil diameter extracted from MonkeyLogic behavioral files.

## 🔬 Core Classification Targets
1.  **Stimulus Identity**: Distinguish between Stimulus A and Stimulus B (e.g., AAAB vs. BBBA).
2.  **Stimulus Order**: Classify the ordinal position in the sequence (P1, P2, P3, P4).
3.  **Omission Expected Identity**: Decode which stimulus was *expected* during a physical void (e.g., A-expected in AXAB vs. B-expected in BXBA).
4.  **Block/Condition**: Classify the global block context and trial-specific condition (RRRR vs. Omission variants).

## 🛠️ Implementation Pipeline

### Phase 1: Signal Processing & Event Detection
- **Source**: D:\Analysis\Omission\local-workspace\behavioral\omission_bhv\data (*.mat)
- **Extraction**: Extract `AnalogData.Eye` (DVA) and `AnalogData.Pupil` at 1000Hz.
- **Saccade Detection**: Identify saccades (Velocity > 30 DVA/s, Amp > 1.5°).
- **Microsaccade Detection**: Identify microsaccades (Amp < 1.5°) during stable fixation.
- **Directionality**: Compute the angular direction (0-360°) for every identified oculomotor event.

### Phase 2: Feature Engineering
- **Windowing**: Align to Code 101 (P1 Onset) with a 1000ms pre-stim buffer.
- **Intervals**: Fixation, P1-4, D1-4 (as defined in `bhv_task_details.md`).
- **Features**: Mean Eye X/Y, Velocity, Acceleration, Saccade Frequency, Polar Direction Histograms.

### Phase 3: Classification & Decoding
- **Model**: Linear SVM with 5-fold cross-validation.
- **Validation**: Balanced classes (50/50 downsampling).
- **Metric**: Decoding Accuracy vs. Time and ROC-AUC.

### Phase 4: Visualization (D:\Analysis\Omission\local-workspace\figures)
1.  **Rose Plots (Polar Histograms)**: Distribution of Eye-movement and Microsaccade directions for each task context.
2.  **Temporal Trajectories**: Average X/Y eye position traces across conditions (e.g., A vs. B divergence).
3.  **Decoding Maps**: Accuracy heatmaps across the trial sequence for each target.

## ✅ Verification
- Compare eye-based decoding performance with neural-based performance (Step 1-3).
- Confirm if oculomotor directions bias towards or away from the center of mass of the stimulus.

---
*Plan established by Gemini CLI. Inserted as Top Priority in the Phase 2 Roadmap.*
