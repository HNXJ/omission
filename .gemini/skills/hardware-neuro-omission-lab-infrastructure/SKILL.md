---
name: hardware-neuro-omission-lab-infrastructure
description: Technical specification for the physical recording environment, stimulus synchronization, and eye-tracking hardware.
---
# skill: hardware-neuro-omission-lab-infrastructure

## When to Use
Use this skill when verifying the temporal precision of neural data. It is essential for:
- Understanding the relationship between screen pixels and Degrees of Visual Angle (DVA).
- Resolving photodiode timing offsets between software events (MonkeyLogic) and physical frame flips.
- Calibrating eye-tracking data relative to the subject's 57cm distance from the screen.
- Documenting the physical signal chain for publication "Methods" sections.

## What is Input
- **Luminance Measurements**: Cd/m2 values for background matching.
- **Physical Dimensions**: Screen width (cm), Subject distance (cm).
- **Wiring Diagrams**: Synchronization triggers between VPixx and Blackrock.

## What is Output
- **Conversion Factors**: Pixels-to-DVA multipliers.
- **Timing Offsets**: Mean photodiode latency (e.g., 8ms fixed offset).
- **Channel Maps**: Physical electrode-to-digital channel assignments for 128-ch probes.

## Algorithm / Methodology
1. **DVA Calculation**: Uses the formula `theta = 2 * arctan(w / (2 * d))` where `d` is subject distance. At 57cm, 1cm = 1 DVA.
2. **Photodiode Correction**: Cross-correlates the "Frame Flip" pulse with the "Strobe Code" to adjust trial start times to the exact microsecond of stimulus appearance.
3. **Luminance Normalization**: Matches the screen's black point to the lab's ambient lighting to minimize pupil dilation artifacts.
4. **Spatial Calibration**: Maps the eye-tracker's voltage range to screen coordinates using a 9-point fixation routine in MonkeyLogic.

## Placeholder Example
```python
# 1. Convert Screen Pixels (px) to Visual Angle (DVA)
# Distance = 57cm, Screen Width = 52cm, Resolution = 1920px
px_per_cm = 1920 / 52
dva = (px / px_per_cm) # simplified for 57cm distance
```

## Relevant Context / Files
- [coding-neuro-omission-behavioral-utils](file:///D:/drive/omission/.gemini/skills/coding-neuro-omission-behavioral-utils/skill.md) — For DVA implementation.
- [src/calibration/timing_checks.py](file:///D:/drive/omission/src/calibration/timing_checks.py) — For photodiode validation.
