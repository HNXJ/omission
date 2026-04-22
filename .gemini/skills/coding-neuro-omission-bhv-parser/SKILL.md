---
name: coding-neuro-omission-bhv-parser
description: Specialized engine for parsing MonkeyLogic 2.2 (.bhv2.mat) files to extract task event timing and stimulus metadata.
---
# skill: coding-neuro-omission-bhv-parser

## When to Use
Use this skill when implementing the initial data ingestion step of the NWB pipeline. It is essential for:
- Mapping `BehavioralCodes` (e.g., Code 100 for Trial Start) to absolute timestamps.
- Identifying stimulus identity (A, B, or R) from the `TaskObject` attributes.
- Filtering out "Trial Errors" (aborted trials, fixation breaks).
- Extracting the "Omission" flag for Phase 4/5 comparative analysis.

## What is Input
- **BHV2.mat Files**: Exported MATLAB structures containing `bhvUni` or `ML2` objects.
- **Event Code Schema**: A mapping of integers (e.g., 10, 11, 100) to task states.

## What is Output
- **Trial Dictionaries**: Cleaned Python objects containing `(trial_id, start_time, end_time, stimulus_id, is_omission)`.
- **Event Timecourse**: A precise mapping of every task event to the master neural clock.

## Algorithm / Methodology
1. **MATLAB Deserialization**: Uses `scipy.io.loadmat(squeeze_me=True)` to convert the MATLAB structure into a navigable Python dictionary.
2. **Trial Error Filtering**: Only processes trials where `TrialError == 0` (Success).
3. **Stimulus Mapping**: Parses the string path in `TaskObject.Attribute` (e.g., `images/stimA.png`) to assign a categorical Stimulus ID.
4. **Omission Detection**: Specifically looks for trials where the stimulus-on code is present but the analog stimulus-vblank is absent, or where a dedicated `Omission` tag is set in the trial header.
5. **Timestamp Alignment**: Offsets all relative trial times by the `AbsoluteTrialStartTime` to facilitate NWB synchronization.

## Placeholder Example
```python
import scipy.io as sio

# 1. Load the BHV2 structure
mat = sio.loadmat('session_230629.bhv2.mat', squeeze_me=True)
trials = mat['ML2']['TrialData']

# 2. Extract timing for correct trials
for t in trials:
    if t['TrialError'] == 0:
        stim_id = t['TaskObject']['Attribute'][0]
        onset_time = t['BehavioralCodes']['CodeTimes'][t['BehavioralCodes']['CodeNumbers'] == 100]
        print(f"Trial {t['Trial']}: Stim {stim_id} at {onset_time}ms")
```

## Relevant Context / Files
- [coding-neuro-omission-behavioral-utils](file:///D:/drive/omission/.gemini/skills/coding-neuro-omission-behavioral-utils/skill.md) — For DVA and Pupil conversion.
- [src/extract/bhv_parser.py](file:///D:/drive/omission/src/extract/bhv_parser.py) — The core implementation of this logic.
