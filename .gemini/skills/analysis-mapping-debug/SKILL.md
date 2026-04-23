---
name: analysis-mapping-debug
---
# analysis-mapping-debug

## Purpose
Traces unit-to-area assignment step-by-step through NWB electrode tables. Diagnoses mislocalization from compound labels or segment-based mapping errors.

## Input
| Name | Type | Description |
|------|------|-------------|
| nwb_path | str | Path to `.nwb` file |
| unit_idx | int | Index of the unit to trace |
| CHANNELS_PER_PROBE | int | 128 (constant) |
| AREA_MAPPING | dict | Label normalization (e.g. `{'DP': 'V4'}`) |

## Output
| Name | Type | Description |
|------|------|-------------|
| debug_trace | dict | `{unit_idx, peak_channel_id, probe_id, raw_label, assigned_area}` |

## Example
```python
import pynwb
io = pynwb.NWBHDF5IO('ses-230818.nwb', 'r')
nwb = io.read()
chan_id = int(nwb.units[42]['peak_channel_id'])
probe_id = chan_id // 128
raw_loc = nwb.electrodes[chan_id, 'location']
print(f"""[trace] Unit 42: ch={chan_id}, probe={probe_id}, raw={raw_loc}""")
```

## Files
- [debug_mapping.py](file:///D:/drive/omission/codes/scripts/debug_mapping.py) — Source