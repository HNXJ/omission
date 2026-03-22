# Behavioral Data (.mat) Parser

The behavioral parser resolves stimulus identity and timing from MonkeyLogic 2.2 output files.

Core Tasks:
1. Filtering: Extract only Correct trials (`TrialError == 0`).
2. Timing: Map `BehavioralCodes` (Numbers and Times) to task events (Fixation, P1, P2, etc.).
3. Identity: Parse `TaskObject.Attribute` to identify if a stimulus was A, B, or R (Random).
4. Eye Traces: Calibrate raw analog signals into Degrees of Visual Angle (DVA).

Mapping Logic:
Stimuli are identified by their file paths (e.g., 'A.avi' = 45°). Omissions are identified by the absence of a stimulus code (e.g., Code 103 missing) and the presence of an Omission metadata tag.

Python Implementation:
```python
import scipy.io as sio

def parse_bhv(file_path):
    mat = sio.loadmat(file_path, squeeze_me=True)
    trials = mat['bhvUni']
    correct_trials = [t for t in trials if t['TrialError'] == 0]
    
    results = []
    for t in correct_trials:
        eye = t['AnalogData']['Eye'] # (N, 2)
        codes = t['BehavioralCodes']['CodeNumbers']
        times = t['BehavioralCodes']['CodeTimes']
        results.append({'eye': eye, 'codes': codes, 'times': times})
    return results
```

References:
1. Hwang, J., et al. (2019). MonkeyLogic: A Real-Time Behavioral Control and Data Acquisition System. Journal of Neuroscience Methods.
