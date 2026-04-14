# Neurodata Without Borders (NWB) Signal Reference

## 1. Electrophysiology Signals

### LFP (Local Field Potential)
- **Description**: Low-frequency component of the extracellular signal (< 300-500 Hz).
- **NWB Type**: `LFP` (stored in an `ElectricalSeries`).
- **Processing**: Often decimated/downsampled from raw broadband data.
- **Location**: Typically stored in `processing/ecephys`.

### Single Units (Spikes)
- **Description**: Action potentials attributed to individual neurons.
- **NWB Type**: `Units` table.
- **Key Columns**: `spike_times` (essential), `electrodes`, `unit_name`, `peak_channel`.
- **Metadata**: Often includes cluster quality metrics (SNR, isolation distance).

### MUA (Multi-Unit Activity)
- **Description**: High-frequency extracellular activity (> 300 Hz) representing the combined spiking of multiple nearby neurons.
- **NWB Type**: Often stored as `ElectricalSeries` in `processing` if rectified/integrated, or identified in `Units` as "unsorted" or "MUA" clusters.

## 2. Behavioral Signals

### Continuous Tracking
- **Description**: Position (x, y, z), velocity, or joint angles.
- **NWB Type**: `SpatialSeries` (inside a `Position` or `Compass` object).
- **Location**: `acquisition` (raw) or `processing/behavior` (cleaned).

### Discrete Events
- **Description**: Trial starts, reward delivery, lick events.
- **NWB Type**: `TimeIntervals` (for durations) or `Events` (for timestamps).

## 3. Library Reference: PyNWB
- **Initialization**: `NWBFile(session_description, identifier, session_start_time, ...)`
- **Device/Electrode Setup**: `create_device`, `create_electrode_group`, `add_electrode`.
- **Data Insertion**:
    - `add_unit`: For single-unit data.
    - `add_acquisition`: For raw data.
    - `add_processing_module`: For LFP/Behavior.
