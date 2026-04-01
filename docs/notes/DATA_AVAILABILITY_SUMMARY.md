# 📊 13-Session Data Availability Summary

|   Session |   Trials |   Conditions |   Units (SPK) | LFP   | Eye (x,y)   | Pupil   | Reward   |
|----------:|---------:|-------------:|--------------:|:------|:------------|:--------|:---------|
|    230630 |     2942 |           50 |           167 | Yes   | Yes         | Yes     | Yes      |
|    230816 |    15586 |           50 |           357 | Yes   | Yes         | Yes     | Yes      |
|    230818 |    15972 |           50 |           541 | Yes   | Yes         | Yes     | Yes      |
|    230823 |    18387 |           50 |           368 | Yes   | Yes         | Yes     | Yes      |
|    230825 |    16996 |           50 |           491 | Yes   | Yes         | Yes     | Yes      |
|    230830 |    15645 |           50 |           774 | Yes   | Yes         | Yes     | Yes      |
|    230831 |    16332 |           50 |           584 | Yes   | Yes         | Yes     | Yes      |
|    230901 |    15337 |           50 |           696 | Yes   | Yes         | Yes     | Yes      |
|    230629 |     4163 |           50 |           464 | Yes   | Yes         | Yes     | Yes      |
|    230714 |    16116 |           50 |           589 | Yes   | Yes         | Yes     | Yes      |
|    230719 |    14091 |           50 |           415 | Yes   | Yes         | Yes     | Yes      |
|    230720 |    14454 |           50 |           317 | Yes   | Yes         | Yes     | Yes      |
|    230721 |    15107 |           50 |           277 | Yes   | Yes         | Yes     | Yes      |

### 📦 Multi-Modal .npy Array Status
All arrays are formatted as `[Trial x Channel/Unit x Sample]`.

|   Session | SPK   | LFP        | BEHAV   | SPK Shape [T, U, S]   |   Window (ms) |
|----------:|:------|:-----------|:--------|:----------------------|--------------:|
|    230629 | ✅     | 2 Probes ✅ | ✅       | (48, 354, 6000)       |          6000 |
|    230630 | ✅     | 3 Probes ✅ | ✅       | (44, 29, 6000)        |          6000 |
|    230714 | ✅     | 2 Probes ✅ | ✅       | (221, 423, 6000)      |          6000 |
|    230719 | ✅     | 3 Probes ✅ | ✅       | (238, 288, 6000)      |          6000 |
|    230720 | ✅     | 2 Probes ✅ | ✅       | (240, 181, 6000)      |          6000 |
|    230721 | ✅     | 2 Probes ✅ | ✅       | (238, 57, 6000)       |          6000 |
|    230816 | ✅     | 3 Probes ✅ | ✅       | (370, 102, 6000)      |          6000 |
|    230818 | ✅     | 3 Probes ✅ | ✅       | (220, 192, 6000)      |          6000 |
|    230823 | ✅     | 3 Probes ✅ | ✅       | (219, 156, 6000)      |          6000 |
|    230825 | ✅     | 3 Probes ✅ | ✅       | (238, 173, 6000)      |          6000 |
|    230830 | ✅     | 3 Probes ✅ | ✅       | (224, 136, 6000)      |          6000 |
|    230831 | ✅     | 3 Probes ✅ | ✅       | (220, 137, 6000)      |          6000 |
|    230901 | ✅     | 3 Probes ✅ | ✅       | (247, 508, 6000)      |          6000 |

### 📦 Granular .npy Data Store
Files organized as `ses<ID>-<probe>-<modality>-<condition>.npy` in the `data/` folder.

|   Session | Behav (12)   | LFP (12/probe)            | Units (12/probe)          | Format            | Window   |
|----------:|:-------------|:--------------------------|:--------------------------|:------------------|:---------|
|    230629 | 12/12 ✅      | P0 (12), P1 (12)          | P0 (12), P1 (12)          | Trial_Chan_Sample | 6000ms   |
|    230630 | 12/12 ✅      | P0 (12), P1 (12), P2 (12) | P0 (12), P1 (12), P2 (12) | Trial_Chan_Sample | 6000ms   |
|    230714 | 12/12 ✅      | P0 (12), P1 (12)          | P0 (12), P1 (12)          | Trial_Chan_Sample | 6000ms   |
|    230719 | 12/12 ✅      | P0 (12), P1 (12), P2 (12) | P0 (12), P2 (12)          | Trial_Chan_Sample | 6000ms   |
|    230720 | 12/12 ✅      | P0 (12), P1 (12)          | P0 (12), P1 (12)          | Trial_Chan_Sample | 6000ms   |
|    230721 | 12/12 ✅      | P0 (12), P1 (12)          | P0 (12), P1 (12)          | Trial_Chan_Sample | 6000ms   |
|    230816 | 12/12 ✅      | P0 (12), P1 (12), P2 (12) | P0 (12), P1 (12), P2 (12) | Trial_Chan_Sample | 6000ms   |
|    230818 | 12/12 ✅      | P0 (12), P1 (12), P2 (12) | P0 (12), P1 (12), P2 (12) | Trial_Chan_Sample | 6000ms   |
|    230823 | 12/12 ✅      | P0 (12), P1 (12), P2 (12) | P0 (12), P1 (12), P2 (12) | Trial_Chan_Sample | 6000ms   |
|    230825 | 12/12 ✅      | P0 (12), P1 (12), P2 (12) | P0 (12), P1 (12), P2 (12) | Trial_Chan_Sample | 6000ms   |
|    230830 | 12/12 ✅      | P0 (12), P1 (12), P2 (12) | P0 (12), P1 (12), P2 (12) | Trial_Chan_Sample | 6000ms   |
|    230831 | 12/12 ✅      | P0 (12), P1 (12), P2 (12) | P0 (12), P1 (12), P2 (12) | Trial_Chan_Sample | 6000ms   |
|    230901 | 12/12 ✅      | P0 (12), P1 (12), P2 (12) | P0 (12), P2 (12)          | Trial_Chan_Sample | 6000ms   |

---

## 🔬 Definitive Metadata & Analysis Rules

To ensure consistency across analyses, the following rules for area mapping and probe identification MUST be followed. These rules are implemented in the `Jnwb` toolbox.

### 1. Probe Identification (Sequential Channel IDs)
Electrode channel IDs are sequential across probes. Each probe contains **128 channels**.
- **Probe 0 (A)**: IDs 0 - 127
- **Probe 1 (B)**: IDs 128 - 255
- **Probe 2 (C)**: IDs 256 - 383
- **Logic**: `probe_id = peak_channel_id // 128`

### 2. Area Mapping & Combined Labels
Many probes contain electrodes in multiple adjacent brain areas. The 128 channels of a probe are divided equally among the areas listed in the label.
- **Example (`V1, V2`)**: Channels 0-63 are mapped to V1, channels 64-127 are mapped to V2.
- **Logic**: Divide 128 by the number of areas in the comma-separated label. Assign the unit to the area corresponding to its `peak_channel_id` segment.

### 3. Area Aliases & Special Mappings
- **Area DP**: Always mapped to **V4**.
- **Area V3**: Always split 50/50 between **V3d** and **V3a**. 
- **V3 Expansion Logic**: If a probe segment is assigned to "V3", that segment is further divided in half to distinguish between dorsal (V3d) and ventral (V3a) units.

### 4. Primary Software Toolbox
The definitive logic for loading, mapping, and processing this data is stored in the `Jnwb` repository:
- **Repo**: [https://github.com/HNXJ/Jnwb](https://github.com/HNXJ/Jnwb)
- **Core Logic**: `jnwb/core.py` (specifically `get_unit_ids_for_area`)

*Updated March 16, 2026, to persist definitive mapping logic.*
