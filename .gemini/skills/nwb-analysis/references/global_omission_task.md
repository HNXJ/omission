# Global Omission Task Reference

Understanding the experimental paradigm and event codes for sessions 230831, 230901, and 230720.

## 1. Task Paradigm
The task involves presenting sequences of visual stimuli (Gratings). Each sequence consists of multiple stimulus events (S1 to S5).

- **Sequence Types**:
    - **BBBA (Standard)**: All 5 stimuli are presented.
    - **AAAB (Omission)**: Stimulus 5 is omitted to study expectation violations.

## 2. Event Codes (Intervals: `flash` or `omission_glo_passive`)
| Code | Event Type | Description |
| :--- | :--- | :--- |
| **9** | Trial Start | Global trial initiation |
| **100** | S1 Onset | First stimulus / Fixation cue onset |
| **101** | S2 Onset | Second stimulus in sequence |
| **102** | S3 Onset | Third stimulus in sequence |
| **103** | S4 Onset | Fourth stimulus in sequence |
| **104** | S5 Onset | Fifth stimulus (Standard) or Omission point |
| **40** | Reward | Reward delivery for correct fixation |
| **50** | Trial End | Global trial termination |

## 3. Data Alignment Logic
- **Primary Trigger**: Align signals to **Code 100** (S1 Onset) or **Code 104** (S5/Omission Onset).
- **Epoch Window**: 
    - Standard: -1.0s pre-S1 to +5.0s post-S1.
    - Local: 500ms pre-event to 1000ms post-event.

## 4. Trial Filtering (Correctness)
Filter for trials where `correct == 1` in the `omission_glo_passive` or `flash` tables.
```python
import pandas as pd
df = nwb.intervals['omission_glo_passive'].to_dataframe()
# Ensure numeric
df['correct'] = pd.to_numeric(df['correct'], errors='coerce')
correct_trials = df[df['correct'] == 1]['trial_num'].unique()
```
