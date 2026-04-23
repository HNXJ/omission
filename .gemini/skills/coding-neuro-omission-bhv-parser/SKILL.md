---
name: coding-neuro-omission-bhv-parser
---
# coding-neuro-omission-bhv-parser

## Purpose
Parses MonkeyLogic 2.2 `.bhv2.mat` files to extract event timing, stimulus identity (A/B/R), omission flags, and trial-error filtering.

## Input
| Name | Type | Description |
|------|------|-------------|
| bhv_path | str | Path to `.bhv2.mat` file |
| event_schema | dict | Code→state mapping (e.g. `{100: 'TrialStart', 101: 'P1Onset'}`) |

## Output
| Name | Type | Description |
|------|------|-------------|
| trial_dicts | list[dict] | `{trial_id, start_time, end_time, stimulus_id, is_omission}` |
| event_timecourse | list[tuple] | `(event_code, absolute_time)` per trial |

## Example
```python
import scipy.io as sio
mat = sio.loadmat('session.bhv2.mat', squeeze_me=True)
trials = mat['ML2']['TrialData']
for t in trials:
    if t['TrialError'] == 0:
        print(f"""[result] Trial {t['Trial']}: Stim={t['TaskObject']['Attribute'][0]}""")
```

## Files
- [bhv_parser.py](file:///D:/drive/omission/src/extract/bhv_parser.py) — Core logic
