# Analysis Plan: Population Decoding & Information Hierarchy

## 1. Stimulus Identity Decoding (V1 Population)
**Objective**: Quantify the neural representation of Stimulus A vs B.
- **Algorithm**: SVM (Linear Kernel) with 5-fold cross-validation.
- **Input**: Population firing rates (50ms bins).
- **Result**: Baseline accuracy (~62% in V1), establishing the "Content" of the sensory signal.

## 2. Omission Detection (Omit vs Delay)
**Objective**: Differentiate physically identical windows (gray screen) based on expectation.
- **Contrast**: `d1` (Delay 1) vs `p2_omit` (Omission at P2).
- **Control**: Both are physically the same, but only `p2_omit` has a missing expected stimulus.
- **Accuracy**: Hierarchical increase from V1 (~52%) to PFC (~58%).

## 3. Surprise Latency Hierarchy
**Objective**: Resolve the temporal propagation of the "Neural Surprise."
- **Detection**: First significant divergence point (AUC > 0.6) between Omission and Delay firing rates.
- **Direction**: **Top-Down Propagation** (PFC 50ms $\to$ V1 49ms) during omissions vs. sensory feedforward (V1 10ms $\to$ PFC 93ms) during stimuli.
- **Implication**: Confirms that prediction error is generated hierarchically and propagates "backwards" to sensory cortex.

## 4. Pupil & Eye Identity Decoding
**Objective**: Determine if the subject's oculomotor system encodes stimulus content and surprise.
- **Algorithm**: 3-Class decoding (A-Std, A-Omit, B-Omit).
- **Features**: Gaze position (x, y), velocity, acceleration, and pupil diameter.
- **Accuracy**: ~67% for Identity (A vs B) and ~60% for Context (Omit vs Delay).
- **Insight**: Eye movements are not passive; they systematically reflect the internal generative model.

## 5. Information Hub Identification
- **Unit Decoding**: SVM decoding on individual units (6,040 total) to identify "High-Information Hubs."
- **LFP Channel Decoding**: 128-channel decoding to map regional information density.
- **Metric**: Rank-order area contributions to global information content.
