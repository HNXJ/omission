# Crucial Debugging Notes: The "Zero Neuron" & Mapping Bug

## 1. The Issue
Initially, several brain areas (V3d, V3a, TEO, FST, MST) showed zero neurons or missed data during plotting, despite being present in the raw data.

## 2. Root Causes Identified
### A. Incomplete Summary Files
We initially relied on `all_units_stats.json`, which was a summary file that did not contain the full mapping for all areas.
**Lesson**: Always use the NWB metadata as the source of truth for area assignments.

### B. Combined Area Labels
Areas are often recorded on the same probe and labeled as a combined string (e.g., `"V1, V2"`, `"TEO, FST"`, `"V3, V4"`).
**Resolution**: We implemented a splitting logic based on the 128-channels-per-probe rule.

### C. Alias Mappings
- **Area DP**: Is an alias for **V4** in this dataset.
- **Area V3**: Needs to be split into **V3d** (dorsal) and **V3a** (ventral).

### D. Global vs. Local Indexing Bug
The most subtle bug: The NWB file uses a **Global Unit Index** (row number in the `units` table), but the `.npy` spike files are exported per probe, using a **Local Unit Index** (index 0..N within that probe's data).
**Resolution**: The mapping logic must group units by `probe_id` and sort them by their NWB index to assign the correct local index that matches the `.npy` array structure.

## 3. The Definitive Mapping Rules
1. **Probe ID**: `peak_channel_id // 128`
2. **Channel in Probe**: `peak_channel_id % 128`
3. **Multi-Area Split**: If a label has N areas, divide the 128 channels into N equal segments.
4. **V3 Special Case**: If a segment is "V3", split that segment 50/50 between V3d and V3a.

## 4. Prevention
- Use the `Jnwb` toolbox (`jnwb/core.py`) for all future mapping.
- Refer to `DATA_AVAILABILITY_SUMMARY.md` for the persisted rules.
