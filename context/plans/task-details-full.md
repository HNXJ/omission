Below is a **fully expanded, standardized, and agent-ready version** of your task description.
I have:

* Clarified ambiguous parts
* Standardized terminology (NeurIPS / methods-grade)
* Added **computational + electrophysiological interpretation layers**
* Incorporated **poster-derived insights** (oscillations, hierarchy, omission signal) 
* Added **analysis + statistical expectations**
* Made it **code-ready for GAMMA / pipeline integration**

---

# 🧠 **Task Specification: Sequential Visual Omission Paradigm (Expanded + Standardized)**

---

# 🧩 1. OVERVIEW

This task is a **controlled sequential visual omission paradigm** designed to probe the neural implementation of **predictive coding / active inference** in the primate brain.

The key experimental manipulation is the **removal of an expected stimulus (omission)** within a temporally structured sequence while maintaining identical sensory input conditions (gray screen), enabling isolation of **pure top-down predictive signals**.

---

# 🎯 2. OBJECTIVE

The subject (monkey) must:

* Maintain fixation on a central fixation point for ~4500 ms
* Passively observe a sequence of visual stimuli
* Receive reward upon successful fixation completion

---

### Critical Design Principle

```id="p1f3d2"
Sensory Input = constant during omission
Neural Activity ≠ constant
```

👉 Therefore:

* Any neural change during omission = **internal model / prediction signal**

---

# 🧪 3. BEHAVIORAL TASK CONTROL

### System

* **Controller**: MonkeyLogic (NIMH)
* Real-time behavioral + stimulus synchronization
* Event-coded outputs (NWB compatible)

---

### Trial Types

| Type               | Description                      |
| ------------------ | -------------------------------- |
| Correct trial      | Full fixation maintained         |
| Incorrect trial    | Fixation broken                  |
| No-report paradigm | No behavioral report of stimulus |

---

### Interpretation

* Task isolates **implicit prediction processing**
* No motor or decision confounds

---

# 🖥️ 4. VISUAL STIMULUS SPECIFICATION

### Hardware

* PROPixx Pro projector
* Resolution: 1920 × 1080
* Refresh rate: 120 Hz
* Viewing distance: 57 cm

---

### Stimulus Properties

| Feature            | Value                     |
| ------------------ | ------------------------- |
| Type               | Circular drifting grating |
| Temporal frequency | 2 Hz                      |
| Orientation A      | 45°                       |
| Orientation B      | 135°                      |
| Background         | Gray (luminance matched)  |

---

### Critical Control

```id="x91kdf"
Luminance(stimulus) ≈ Luminance(background)
```

👉 Ensures:

* No photodiode change during omission
* No bottom-up signal

---

# 🧠 5. OMISSION DEFINITION (CRITICAL)

### Omission Condition

* One stimulus (p2, p3, or p4) is removed
* Screen remains identical (gray)

---

### Interpretation

```id="9dfk22"
Omission = Expected Stimulus − Sensory Input
```

From poster:

* No gamma increase
* Beta coherence increases 

---

### Functional Meaning

* Reveals **prediction without input**
* Pure **top-down inference state**

---

# 🧬 6. NEURAL REPRESENTATION FRAMEWORK

---

## 🧠 Multi-Scale Signals

### 1. SPK (Single Units)

* Spike-sorted neurons (Kilosort 2.5)
* Sparse encoding (~<2% omission responsive) 

---

### 2. MUAe (Population Activity)

* High-frequency envelope (>1000 Hz)
* Robust local response

---

### 3. LFP (Field Dynamics)

Key interpretation from poster:

| Band  | Role                  |
| ----- | --------------------- |
| Gamma | Feedforward / sensory |
| Beta  | Feedback / prediction |
| Alpha | Inhibitory modulation |

---

### Poster-derived insight

```id="j92lsd"
Omission → beta synchronization ↑
Gamma → unchanged
```

---

# 🧠 7. CORTICAL HIERARCHY STRUCTURE

---

### Areas

| Level | Regions               |
| ----- | --------------------- |
| Low   | V1, V2                |
| Mid   | V4, MT, MST, TEO, FST |
| High  | FEF, PFC              |

---

### Key Observation (Poster)

```id="3kdfla"
Prediction signal strength ↑ with hierarchy
```

* Weak in V1
* Strong in PFC

---

### Interpretation

* Prediction originates in higher cortex
* Propagates downward

---

# 🧪 8. CONDITION SPACE

---

### Structured Sequences

```id="3lskd9"
A = orientation 45°
B = orientation 135°
R = random A/B
X = omission
```

---

### Blocks

* Structured predictable blocks (AAAB, BBBA)
* Rare omission variants (~10%)
* Random control (RRRR)

---

### Key Design Feature

```id="8d2jfa"
Probability imbalance → expectation formation
```

---

# ⏱️ 9. TEMPORAL STRUCTURE

---

### Timeline (ms)

| Event          | Time |
| -------------- | ---- |
| Fixation start | -500 |
| p1             | 0    |
| d1             | 531  |
| p2             | 1031 |
| d2             | 1562 |
| p3             | 2062 |
| d3             | 2593 |
| p4             | 3093 |
| d4             | 3624 |
| End fixation   | 4124 |

---

### Key Window

```id="8skd92"
d1-p2-d2 = identical sensory input window
```

But:

* Neural activity differs (poster "ghost signal")

---

# 👻 10. “GHOST SIGNAL” (CRITICAL CONCEPT)

---

### Definition

```id="0slf93"
Ghost Signal = Neural activity during identical sensory input but different expectation
```

---

### Interpretation

* Brain generates internal model signal
* Independent of stimulus

---

### Poster Support

* Omission produces structured oscillatory changes
* Not random silence 

---

# 📊 11. ELECTROPHYSIOLOGY ALIGNMENT

---

### Reference Event

* Code 101.0 = p1 onset (gold standard)

---

### Temporal Validation

* V1 response latency: 40–60 ms

---

### Data Window

```id="0df9s2"
[0–1000] = baseline
[1000+] = task
```

---

# 🌊 12. SIGNAL DYNAMICS (POSTER-INTEGRATED)

---

### During Stimulus

* Gamma ↑ (feedforward)
* Local processing

---

### During Omission

* Gamma ≈ constant
* Beta ↑ (global synchrony)
* Alpha ↓

---

### Key Insight

```id="92dfk3"
Omission ≠ silence  
Omission = structured predictive state
```

---

# 📊 13. ANALYSIS PIPELINE (STANDARDIZED)

---

## 1. Time-Frequency Analysis

* Multitaper / wavelet
* Frequency bands:

  * Theta
  * Alpha
  * Beta
  * Gamma

---

## 2. Correlation Analysis

* Inter-area correlation matrices
* Band-specific

Poster:

* Gamma → stimulus correlation
* Beta → omission correlation

---

## 3. Spike Analysis

* PSTH per neuron
* Classification:

  * Stimulus excited
  * Stimulus inhibited
  * Omission selective

---

## 4. Population Statistics

* % responsive neurons per area
* Hierarchical distribution

---

# 📈 14. STATISTICAL TESTS (EXPECTED)

---

### Required

* Cluster-based permutation tests
* Baseline vs condition comparisons
* Cross-area correlation significance
* Latency comparisons

---

### Suggested

```id="2lskd9"
Wilcoxon / Rank-sum → layer differences
Permutation → time-frequency clusters
Bootstrap → confidence intervals
```

---

# 🧠 15. MECHANISTIC INTERPRETATION

---

### Predictive Coding Mapping

```id="92lsd9"
Prediction = beta
Error = gamma
```

---

### Omission Case

```id="82lsd2"
No stimulus → no error → gamma unchanged  
Prediction persists → beta synchrony ↑
```

---

### Poster Insight

* Few neurons control global state
* Network-level phenomenon dominates

---

# 🧩 16. AGENT IMPLEMENTATION NOTES

---

## Required Features

* Must detect omission windows
* Must separate LO vs GO contexts
* Must identify:

  * spectral shifts
  * hierarchy effects
  * sparse coding

---

## Failure Modes

Avoid:

* interpreting omission as “no signal”
* equating spiking with information
* ignoring beta coherence

---

# 📦 17. OUTPUT STRUCTURE (FOR PIPELINE)

```id="skd92l"
{
  "paradigm": "sequential omission",
  "key_window": "prediction-only",
  "signals": {
    "gamma": "stable",
    "beta": "increased coherence",
    "alpha": "suppressed"
  },
  "spiking": "sparse high-order",
  "hierarchy": "top-down dominant"
}
```

---

# 🚀 FINAL SUMMARY

---

### Scientific Meaning

Omission reveals:

> The brain encodes predictions not through firing rate magnitude, but through **network-level oscillatory coordination**

---

### Agent Meaning

Agents must:

* Treat omission as **latent predictive computation**
* Prioritize:

  * beta synchrony
  * hierarchical flow
  * sparse neuron control

---

# 🔧 If you want next

I can convert this into:

✅ HPC-36 scoring template
✅ Python-ready dataset parser
✅ NWB analysis pipeline
✅ Figure-ready methods section

Just tell me 👍
