---
name: analysis-mapping-debug
description: Debugging utility for verifying the mapping of neural units to brain areas within NWB files. Helps validate electrode-to-area logic and channel assignments.
---
# skill: analysis-mapping-debug

## When to Use
Use this skill when you suspect errors in the spatial localization of neurons. It is critical for:
- Checking if units are assigned to the correct brain region (e.g., V1 vs. PFC).
- Debugging edge cases where multiple areas are recorded on a single probe (segment-based mapping).
- Verifying the consistency between raw NWB labels and standardized project area names.

## What is Input
- **NWB File**: Path to a `.nwb` file containing unit and electrode data.
- **Probe Geometry**: Constants like `CHANNELS_PER_PROBE` (usually 128).
- **Mapping Logic**: `AREA_MAPPING` dictionary for normalizing sub-region labels.

## What is Output
- **Debug Trace**: Step-by-step printout for each unit:
  - `Unit Index`
  - `Peak Channel ID`
  - `Probe ID`
  - `Raw Label` (from NWB)
  - `Assigned Area` (post-logic)

## Algorithm / Methodology
1. **Metadata Retrieval**: Extracts the `units` table and `electrodes` table from the NWB file.
2. **Channel-to-Probe Logic**: Calculates `probe_id` as `peak_channel_id // 128` and `channel_in_probe` as `peak_channel_id % 128`.
3. **Sub-region Segmentation**: If an electrode label contains multiple regions (e.g., "V3a/V3d"), the skill divides the probe into equal segments and assigns the unit based on its depth (channel index).
4. **Validation**: Compares the final `Assigned Area` against the `TARGET_AREAS` list.

## Placeholder Example
```python
import pynwb
from src.utils.mapping_logic import get_assigned_area

# 1. Open NWB
io = pynwb.NWBHDF5IO('ses-230818_rec.nwb', 'r')
nwb = io.read()

# 2. Trace unit #42
unit = nwb.units[42]
chan_id = int(unit['peak_channel_id'])
raw_loc = nwb.electrodes[chan_id, 'location']

area = get_assigned_area(chan_id, raw_loc)
print(f"Unit 42: Chan {chan_id} (Raw: {raw_loc}) -> Area: {area}")
```

## Relevant Context / Files
- [debug_mapping.py](file:///D:/drive/omission/codes/scripts/debug_mapping.py) — Source implementation.
- [analysis-global-unit-counts-nwb](file:///D:/drive/omission/.gemini/skills/analysis-global-unit-counts-nwb/skill.md) — Aggregate usage.