---
name: analysis-behavioral-data-processing
description: Provides foundational utilities for processing raw MonkeyLogic behavioral .mat files and extracted behavioral data (eye, pupil, event codes). Includes functions for data loading, trial-wise feature extraction, saccade detection, and eye movement direction calculation.
---
# SKILL: analysis-behavioral-data-processing

## Description
This skill provides foundational utilities for processing raw MonkeyLogic behavioral `.mat` files and extracted behavioral data (eye, pupil, event codes). It includes functions for efficient data loading, trial-wise feature extraction (eye, pupil, behavioral codes, times), saccade detection, and eye movement direction calculation. These utilities are often used as building blocks for higher-level behavioral analysis scripts.

## Core Tasks
1.  **`load_behavioral_data(file_path)`**: Loads MonkeyLogic behavioral `.mat` data.
2.  **`extract_trial_data(trial_struct, fs=1000)`**: Extracts eye, pupil, and event timing for a single trial with safety checks.
3.  **`detect_saccades(eye_x, eye_y, fs=1000, vel_thresh=30, amp_thresh=1.5)`**: Detects saccades and microsaccades from eye position data.
4.  **`get_angular_direction(eye_x, eye_y)`**: Calculates the angular direction (0-360 degrees) for eye movements.

## Inputs
*   MonkeyLogic `.mat` files (for `load_behavioral_data`).
*   `trial_struct`: A structured dictionary or object representing a single trial's data (for `extract_trial_data`).
*   `eye_x`, `eye_y`: 1D NumPy arrays representing eye position in x and y coordinates (for `detect_saccades`, `get_angular_direction`).
*   `fs`: Sampling frequency in Hz (default 1000 Hz).
*   `vel_thresh`, `amp_thresh`: Velocity and amplitude thresholds for saccade detection.

## Outputs
*   **`load_behavioral_data`**: A structured NumPy array containing trial data (`bhvUni`).
*   **`extract_trial_data`**: `(eye, pupil, codes, times)` tuples, where `eye` and `pupil` are NumPy arrays, and `codes`/`times` are 1D arrays of behavioral events/timestamps.
*   **`detect_saccades`**: `(saccade_indices, velocities)` tuples, where `saccade_indices` are the time points of detected saccades and `velocities` is the instantaneous eye velocity.
*   **`get_angular_direction`**: A 1D NumPy array of angular directions in degrees.

## Example Use

```python
import numpy as np
import scipy.io as sio
from types import SimpleNamespace
import sys
import os

# Assuming behavioral_utils.py is in the functions directory
# For this example, we'll simulate the functions' presence.
# In a real scenario, you would import them directly:
# from functions.behavioral_utils import load_behavioral_data, extract_trial_data, 
#                                      detect_saccades, get_angular_direction

# --- Mocking the functions from behavioral_utils.py ---
# This is for demonstration if behavioral_utils.py is not in current path.
# In actual use, ensure functions.behavioral_utils is imported.
def load_behavioral_data(file_path):
    # Simulate loading a .mat file
    print(f"Simulating loading behavioral data from {file_path}")
    return [create_mock_trial_struct(), create_mock_trial_struct()]

def extract_trial_data(trial_struct, fs=1000):
    try:
        analog = trial_struct.AnalogData[0, 0]
        eye = analog.Eye[0, 0] if 'Eye' in dir(analog) else None
        gen = analog.General[0, 0] if gen and 'Gen1' in dir(gen) else None
        pupil = gen.Gen1[0, 0] if gen and 'Gen1' in dir(gen) else None
        codes_struct = trial_struct.BehavioralCodes[0, 0]
        codes = codes_struct.CodeNumbers[0, 0].flatten()
        times = codes_struct.CodeTimes[0, 0].flatten()
        return np.array(eye), np.array(pupil), np.array(codes), np.array(times)
    except Exception as e:
        print(f"Error extracting mock trial: {e}")
        return None, None, None, None

def detect_saccades(eye_x, eye_y, fs=1000, vel_thresh=30, amp_thresh=1.5):
    if eye_x is None or eye_y is None: return None, None
    vx = np.gradient(eye_x) * fs
    vy = np.gradient(eye_y) * fs
    vel = np.sqrt(vx**2 + vy**2)
    saccade_indices = np.where(vel > vel_thresh)[0]
    return saccade_indices, vel

def get_angular_direction(eye_x, eye_y):
    if eye_x is None or eye_y is None or len(eye_x) < 2: return None
    dx = np.diff(eye_x)
    dy = np.diff(eye_y)
    angles = np.arctan2(dy, dx)
    return np.degrees(angles) % 360

# --- Mocking scipy.io.loadmat output structure ---
def create_mock_trial_struct():
    mock_analog_data = SimpleNamespace(
        Eye=np.array([[[np.random.rand(1000), np.random.rand(1000)]]], dtype=object),
        General=np.array([[[SimpleNamespace(Gen1=np.random.rand(1000))]]], dtype=object)
    )
    mock_behavioral_codes = SimpleNamespace(
        CodeNumbers=np.array([[[101, 102, 103, 104, 105, 106, 107, 108, 109, 110]]], dtype=object),
        CodeTimes=np.array([[[0, 100, 200, 300, 400, 500, 600, 700, 800, 900]]], dtype=object)
    )
    mock_trial = SimpleNamespace(
        AnalogData=np.array([[mock_analog_data]], dtype=object),
        BehavioralCodes=np.array([[mock_behavioral_codes]], dtype=object),
        TrialError=0
    )
    return mock_trial

# --- Demonstration ---
print("--- Demonstrating Behavioral Utilities ---")

# Simulate loading data
mock_bhv_data = load_behavioral_data("mock_path.mat")
print(f"  Loaded {len(mock_bhv_data)} mock trials.")

# Extract data for a trial
sample_trial = mock_bhv_data[0]
eye_data, pupil_data, codes, times = extract_trial_data(sample_trial)

if eye_data is not None:
    eye_x, eye_y = eye_data[0], eye_data[1]
    print(f"  Extracted eye_x sample: {eye_x[:5]}")
    print(f"  Extracted pupil sample: {pupil_data[:5]}")

    # Detect saccades
    saccade_indices, velocities = detect_saccades(eye_x, eye_y)
    if saccade_indices is not None:
        print(f"  Detected {len(saccade_indices)} saccades.")
        print(f"  Max velocity: {np.max(velocities):.2f}")

    # Get angular direction
    angles = get_angular_direction(eye_x, eye_y)
    if angles is not None:
        print(f"  Sample angular direction: {angles[:5]} degrees")
```