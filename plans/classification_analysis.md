# Plan: Classification of Contexts & Behavioral Proxies

## 🎯 Objective
Decode task context, stimulus identity, and omission presence using a multi-modal feature set (Spiking, LFP, Pupil Diameter, and Eye Position).

## 📊 Signal Modalities
1.  **Neural**: Single-unit spiking activity and LFP (power/phase).
2.  **Behavioral**: Pupil diameter (tonic/phasic) and Eye-x-y gaze position.

## 🔬 Core Classification Tasks

### 1. Omission Detection (Binary)
- **Goal**: Classify the general presence of an omission (Something vs. Nothing) without differentiating the omission type.
- **Signals**: Spiking, LFP, Pupil, Combined.
- **Comparison**: Omission windows (p2-p4 in RXRR, RRXR, RRRX) vs. Standard windows (p2-p4 in RRRR).

### 2. Identity Decoding (A vs. B)
- **Goal**: Measure the performance of eye-pupil diameter in distinguishing Stimulus A from Stimulus B.
- **Contexts**: Compare AAAB vs. BBBA sequences.
- **Latency**: Identify the earliest point in the trial where pupil diameter diverges between identities.

### 3. Repetition vs. Local Oddball
- **Goal**: Contrast the neural/pupil response to a stimulus based on its position in the sequence.
- **Comparison 1**: Stim 2 & 3 (Identity B) in BBBA block vs. Stim 4 (Identity B) in AAAB block.
- **Comparison 2**: Stim 2 & 3 (Identity A) in AAAB block vs. Stim 4 (Identity A) in BBBA block.
- **Hypothesis**: The "Oddball" (Stim 4 in discordant block) will show higher classification accuracy/magnitude than the "Repeated" stimuli.

## 🛡️ Control Framework
To ensure the specificity of the omission signal, all classifiers must be validated against:
1.  **FX (Fixation)**: -500 to -50ms pre-stimulus baseline.
2.  **d1-d4 (Delays)**: Inter-stimulus intervals where the screen is physically identical to the omission.
3.  **RX (Unpredictable Omission)**: Omission in the random block (R) where identity is contextually unpredictable. This is the "Hard Control" (RX should not carry identity information).

## 🛠️ Implementation Pipeline
1.  **Data Extraction**: Extract synchronized Pupil/Eye and Spike/LFP data for the target windows.
2.  **Feature Engineering**: 
    - Pupil: Mean diameter, peak velocity, area under curve.
    - Neural: PSTH bins (20ms), LFP Band Power.
3.  **Model**: SVM/Logistic Regression with cross-validation.
4.  **Metric**: ROC-AUC and Decoding Accuracy vs. Time.

---
*Plan established by Gemini CLI. Integrated as Step 3 in the Master Roadmap.*
