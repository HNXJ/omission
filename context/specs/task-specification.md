---
status: canonical
scope: specs
source_of_truth: true
supersedes:
  - context/plans/task-details.md
  - context/plans/task-details-full.md
  - context/plans/gamma-task-specification.md
  - context/plans/bhv-task-details.md
  - context/plans/task-details-bhv.md
last_reviewed: 2026-04-06
---

# Task Specification: Sequential Visual Omission

## 1. Overview & Objective
This project uses a **controlled sequential visual omission paradigm** to investigate the neural implementation of **predictive coding and active inference** in the primate brain.

The core objective is to isolate **pure top-down predictive signals** ("ghost signals") by removing an expected stimulus within a temporally structured sequence while maintaining identical sensory input (a luminance-matched gray screen).

## 2. Stimulus Sequence & Condition Logic
The task consists of sequences of four visual presentations ($p1, p2, p3, p4$) separated by delays ($d1, d2, d3, d4$).

### Stimulus Identities
- **A**: Circular drifting grating (45° orientation, 2Hz temporal frequency).
- **B**: Circular drifting grating (135° orientation, 2Hz temporal frequency).
- **R**: Random stimulus (either A or B, decided per trial).
- **X**: Omission (expected stimulus removed, screen remains gray).

### Condition Groups
| Group | Sequence | Probability | Description |
|:---:|:---:|:---:|:---|
| **AAAB** | A-A-A-B | ~70% | Frequent structured sequence (Block A) |
| **AXAB** | A-X-A-B | ~10% | Rare omission of $p2$ |
| **AAXB** | A-A-X-B | ~10% | Rare omission of $p3$ |
| **AAAX** | A-A-A-X | ~10% | Rare omission of $p4$ |
| **BBBA** | B-B-B-A | ~70% | Frequent structured sequence (Block B) |
| **BXBA** | B-X-B-A | ~10% | Rare omission of $p2$ |
| **RRRR** | R-R-R-R | ~40% | Random control sequence |
| **RXRR** | R-X-R-R | ~20% | Rare omission of $p2$ in random context |

## 3. Omission Definition
An omission occurs when an expected stimulus is removed, but the sensory environment (luminance-matched gray screen) remains identical to the inter-stimulus intervals and delays.
- **Logic**: $Omission = Expected Stimulus - Sensory Input$
- **Ghost Signal**: Neural activity occurring during the identical sensory window but differing based on internal expectation.

## 4. Event Timings & Windows (ms)
All times are relative to the onset of $p1$ (**Code 101.0**).

| Event | Relative Time (ms) | Description |
|:---|:---:|:---|
| Fixation Start | -500 | Pre-stimulus baseline anchor |
| **p1 Onset** | **0** | **Primary alignment anchor** |
| d1 Onset | 531 | First delay |
| p2 Onset | 1031 | Second presentation (or omission) |
| d2 Onset | 1562 | Second delay |
| p3 Onset | 2062 | Third presentation (or omission) |
| d3 Onset | 2593 | Third delay |
| p4 Onset | 3093 | Fourth presentation (or omission) |
| d4 Onset | 3624 | Fourth delay |
| End Fixation | 4124 | Fixation offset |
| Reward | ~4150 | Juice delivery for correct trial |

## 5. Behavioral Task Control
- **System**: MonkeyLogic 2.2 (NIMH).
- **Requirement**: Maintain eye fixation within a small window (~1-2° radius) for ~4500ms.
- **Inputs**: Eye position sampled at 1000Hz, calibrated to **Degrees of Visual Angle (DVA)** (57 cm screen distance).
- **Paradigm**: No-report (passive observation during fixation).
- **Classification**:
  - **Saccades**: Velocity > 30 DVA/s and Amplitude > 1.5°.
  - **Microsaccades**: Amplitude < 1.5° during stable fixation periods.

### Condition Number Mapping (NWB `task_condition_number`)
- **AAAB**: 1, 2
- **AXAB**: 3
- **AAXB**: 4
- **AAAX**: 5
- **BBBA**: 6, 7
- **BXBA**: 8
- **BBXA**: 9
- **BBBX**: 10
- **RRRR**: 11-26
- **RXRR**: 27-34
- **RRXR**: 35, 37, 39, 41
- **RRRX**: 36, 38, 40, 42, 43-50

## 6. Neural Interpretation Notes
- **Gamma Band**: Associated with feedforward sensory processing; expected to be stable/absent during omission.
- **Beta Band**: Associated with feedback and top-down prediction; expected to show **increased coherence/synchrony** during omission.
- **Hierarchy Effect**: Prediction signals are expected to originate in High-Order areas (PFC, FEF) and propagate downward to Low-Order areas (V1, V2).
- **Sparse Coding**: Omission-selective responses are expected to be sparse in single-unit populations.

## 7. Canonical Terminology
- **Correct Trial**: Full fixation maintained (TrialError == 0).
- **No Report**: Passive viewing without a behavioral choice task.
- **Luminance Matching**: Background and stimuli have matched luminance to prevent bottom-up photodiode changes.
- **Golden Standard**: Alignment to Code 101.0 (P1 onset).
