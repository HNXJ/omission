"""
run-lfp-analysis-pipeline.py
============================
Executes the 15-step LFP-only analysis pipeline for the OGLO Visual Omission Paradigm.
This script orchestrates functions from `lfp_pipeline.py`, `lfp_io.py`, `lfp_events.py`,
`lfp_preproc.py`, and `lfp_stats.py` to process NWB data, perform LFP analysis,
and generate outputs as defined in the pipeline.

The script iterates through NWB files in the specified DATA_DIR, applying each step
of the pipeline and handling data flow between them.
"""

import os
import glob
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
import pickle # NEW: Import for saving global_processed_data
from typing import Any, Dict, List, Tuple
from scipy.signal import butter, filtfilt, hilbert, spectrogram # Added spectrogram


# Import functions from the LFP pipeline modules
import codes.functions.io.lfp_io as lfp_io
import codes.functions.events.lfp_events as lfp_events
import codes.functions.lfp.lfp_pipeline as lfp_pipeline
import codes.functions.lfp.lfp_preproc as lfp_preproc # For helper bipolar ref
import codes.functions.lfp.lfp_stats as lfp_stats
import codes.functions.lfp.lfp_laminar_mapping as lfp_laminar_mapping # New import for laminar mapping
import codes.functions.visualization.lfp_plotting_utils as lfp_plotting_utils # NEW: Import plotting utilities
from codes.functions.lfp.lfp_constants import (
    FS_LFP, BANDS, SEQUENCE_TIMING, TIMING_MS, ALL_CONDITIONS,
    OMISSION_CONDITIONS, AREA_TIERS, DEFAULT_WF_PARAMS,
    GOLD, BLACK, VIOLET, CANONICAL_AREAS
)


# Configuration
DATA_DIR = Path(__file__).parents[2] / "data" # Assumes NWB files are here
OUTPUT_DIR = Path(__file__).parents[2] / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True) # Ensure output directory exists

# Define output directories for figures
FIG_05_OUTPUT_DIR = OUTPUT_DIR / "figures" / "oglo" / "fig_05_LFP_dB_EXT_ALLSESSIONS"
FIG_06_OUTPUT_DIR = OUTPUT_DIR / "figures" / "oglo" / "fig_06_BAND_SUMMARY"
FIG_03_OUTPUT_DIR = OUTPUT_DIR / "figures" / "oglo" / "fig_03_POPULATION_FIRING_RATE"
FIG_05_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_06_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_03_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --- Helper Function for Bipolar Referencing per Area (intermediate step) ---
def _apply_bipolar_ref_per_area(
    raw_lfp: np.ndarray,
    channel_areas: Dict[int, str], # This now comes from the updated electrodes
    electrode_df: pd.DataFrame,
    bad_channels: List[int],
) -> Dict[str, np.ndarray]:
    """
    Groups raw LFP by area, sorts channels by depth, and applies bipolar referencing
    within each area, excluding bad channels.

    Parameters
    ----------
    raw_lfp      : np.ndarray, shape (n_total_channels, n_times)
    channel_areas: Dict[int, str] - mapping from channel_idx to area name (updated)
    electrode_df : pd.DataFrame - electrodes table with 'depth' column (updated)
    bad_channels : List[int] - global indices of channels to exclude

    Returns
    -------
    Dict[str, np.ndarray] - {area: LFP_array_bipolar (n_bipolar_channels, n_times)}
    """
    lfp_by_area: Dict[str, np.ndarray] = {}
    
    # Ensure raw_lfp is 2D and contains float data
    raw_lfp_float = np.asarray(raw_lfp, dtype=float)
    if raw_lfp_float.ndim == 1:
        raw_lfp_float = raw_lfp_float[None, :] # Make it (1, n_times)
    
    # Reconstruct channel_areas based on the updated_electrodes 'location'
    channel_areas_map = {
        ch_idx: row['location'] 
        for ch_idx, row in electrode_df.iterrows() 
        if 'location' in row and pd.notna(row['location'])
    }

    for area in set(channel_areas_map.values()):
        # Get channel indices for this area, excluding bad channels
        area_ch_ids_raw = [
            ch_idx for ch_idx, ch_area in channel_areas_map.items()
            if ch_area == area and ch_idx not in bad_channels
        ]
        
        if not area_ch_ids_raw:
            continue
            
        # Sort channels by depth for correct bipolar differencing
        area_electrodes = electrode_df.loc[area_ch_ids_raw]
        if 'depth' in area_electrodes.columns:
            area_electrodes = area_electrodes.sort_values('depth')
        sorted_area_ch_ids = area_electrodes.index.tolist()
        
        if len(sorted_area_ch_ids) < 2:
            warnings.warn(f"Area {area} has less than 2 good channels for bipolar referencing. Skipping.", RuntimeWarning)
            continue

        # Extract LFP data for this area's sorted, good channels
        lfp_area = raw_lfp_float[sorted_area_ch_ids, :]
        
        # Apply bipolar referencing (n-1 channels)
        lfp_area_bipolar = lfp_area[:-1, :] - lfp_area[1:, :]
        
        lfp_by_area[area] = lfp_area_bipolar
        
    return lfp_by_area


# --- Helper Function for Epoching LFP Data ---
def _epoch_lfp_data(
    lfp_raw: np.ndarray,
    event_table: pd.DataFrame,
    channels_to_extract: List[int], # Renamed for clarity
    fs: float,
    window_ms: Tuple[int, int] = (-1000, 5000), # Default window for full epoch
) -> np.ndarray:
    """
    Extracts epoched LFP data for a given set of channels.

    Parameters
    ----------
    lfp_raw : np.ndarray
        Raw LFP data (n_total_channels, n_total_samples).
    event_table : pd.DataFrame
        DataFrame with event timing. Must contain 'time_ms' column.
    channels_to_extract : List[int]
        List of global channel indices to extract.
    fs : float
        Sampling frequency.
    window_ms : Tuple[int, int]
        Start and end of the epoch window in milliseconds relative to event onset.

    Returns
    -------
    np.ndarray
        Epoched LFP data (n_trials, n_channels_in_selection, n_samples_per_epoch).
    """
    if not channels_to_extract or event_table.empty:
        return np.empty((0, 0, 0))

    window_samples = (
        int(window_ms[0] * fs / 1000),
        int(window_ms[1] * fs / 1000)
    )
    n_samples_per_epoch = window_samples[1] - window_samples[0]

    # Select LFP data for the specified channels
    lfp_selection = lfp_raw[channels_to_extract, :] # (n_selected_channels, n_total_samples)

    epoched_data = []
    for _, event in event_table.iterrows():
        # event['time_ms'] is the global time of event onset
        event_time_sample = int(event['time_ms'] * fs / 1000)

        start_sample = event_time_sample + window_samples[0]
        end_sample = event_time_sample + window_samples[1]

        if start_sample >= 0 and end_sample <= lfp_selection.shape[1]:
            epoch = lfp_selection[:, start_sample:end_sample]
            if epoch.shape[1] == n_samples_per_epoch: # Ensure consistent length
                epoched_data.append(epoch)
        # else: warnings.warn(f"Epoch out of bounds for event {event.name}. Skipping.", RuntimeWarning)

    if not epoched_data:
        return np.empty((0, len(channels_to_extract), n_samples_per_epoch))

    return np.stack(epoched_data, axis=0) # (n_trials, n_channels, n_samples)

# --- Helper Function for Epoching Spike Times and Binning ---
def _epoch_spike_times(
    spike_times: np.ndarray, # 1D array of spike times (in seconds) for a single unit
    event_table: pd.DataFrame,
    fs: float,
    window_ms: Tuple[int, int] = (-1000, 5000),
    bin_size_ms: float = 50.0,
) -> np.ndarray:
    """
    Extracts epoched and binned spike counts for a single unit.

    Parameters
    ----------
    spike_times : np.ndarray
        1D array of spike times in seconds.
    event_table : pd.DataFrame
        DataFrame with event timing. Must contain 'time_ms' column.
    fs : float
        Sampling frequency.
    window_ms : Tuple[int, int]
        Start and end of the epoch window in milliseconds relative to event onset.
    bin_size_ms : float
        Size of the bin in milliseconds for spike counting.

    Returns
    -------
    np.ndarray
        Binned spike counts (n_trials, n_bins).
    """
    if event_table.empty:
        return np.empty((0, 0))

    window_start_sec = window_ms[0] / 1000.0
    window_end_sec = window_ms[1] / 1000.0
    epoch_duration_sec = window_end_sec - window_start_sec
    
    bin_size_sec = bin_size_ms / 1000.0
    n_bins = int(np.ceil(epoch_duration_sec / bin_size_sec))
    
    binned_spike_counts = []

    for _, event in event_table.iterrows():
        event_time_sec = event['time_ms'] / 1000.0

        epoch_spike_times_relative = spike_times - event_time_sec
        
        # Filter spikes within the epoch window
        spikes_in_epoch = epoch_spike_times_relative[
            (epoch_spike_times_relative >= window_start_sec) &
            (epoch_spike_times_relative < window_end_sec) # Corrected this line
        ]
        
        # Bin spikes
        hist, _ = np.histogram(
            spikes_in_epoch, 
            bins=np.arange(window_start_sec, window_end_sec + bin_size_sec, bin_size_sec)
        )
        # Ensure hist has n_bins length, truncate if needed
        binned_spike_counts.append(hist[:n_bins])

    if not binned_spike_counts:
        return np.empty((0, n_bins))

    return np.stack(binned_spike_counts, axis=0) # (n_trials, n_bins)


# --- Helper Function to Compute MUA from LFP ---
def _compute_mua(
    lfp_channel_data: np.ndarray, # 1D array of LFP for a single channel
    fs: float,
    mua_band: Tuple[float, float] = (300.0, 3000.0), # MUA band
    mua_filter_order: int = 4,
    mua_smooth_ms: float = 10.0, # Smoothing window for envelope
) -> np.ndarray:
    """
    Computes Multi-Unit Activity (MUA) from a single LFP channel.
    This involves bandpass filtering, rectification, and smoothing.

    Parameters
    ----------
    lfp_channel_data : np.ndarray
        1D array of LFP data for a single channel.
    fs : float
        Sampling frequency.
    mua_band : Tuple[float, float]
        Frequency band for MUA (e.g., (300, 3000)).
    mua_filter_order : int
        Order of the Butterworth filter.
    mua_smooth_ms : float
        Smoothing window in milliseconds for the MUA envelope.

    Returns
    -------
    np.ndarray
        1D array of MUA power/envelope.
    """
    if lfp_channel_data.size == 0:
        return np.array([])

    # 1. Bandpass filter
    nyquist = 0.5 * fs
    low_cut = mua_band[0] / nyquist
    high_cut = mua_band[1] / nyquist
    
    b, a = butter(mua_filter_order, [low_cut, high_cut], btype='band')
    filtered_lfp = filtfilt(b, a, lfp_channel_data)

    # 2. Rectification and smoothing (envelope)
    # Using the absolute value of the Hilbert transform for the envelope
    mua_envelope = np.abs(hilbert(filtered_lfp))

    # Apply a low-pass filter (smoothing) to the envelope
    smooth_nyquist = 0.5 * fs
    smooth_cutoff = (1000 / mua_smooth_ms) / smooth_nyquist # Example: 10ms window -> 100 Hz cutoff
    if smooth_cutoff >= 1.0: smooth_cutoff = 0.99 # Cap at Nyquist
    
    b_smooth, a_smooth = butter(mua_filter_order, smooth_cutoff, btype='low')
    mua_smoothed = filtfilt(b_smooth, a_smooth, mua_envelope)

    return mua_smoothed


# --- NEW Helper Function: Compute Trial-Level TFR and Band Power ---
def _compute_trial_tfr_and_band_power(
    epochs: np.ndarray, # (n_trials, n_channels, n_samples)
    fs: float,
    nperseg: int = DEFAULT_WF_PARAMS["nperseg"],
    noverlap: int = DEFAULT_WF_PARAMS["noverlap"],
    freq_range: Tuple[float, float] = (1.0, 150.0),
    bands_dict: Dict[str, Tuple[float, float]] = BANDS,
) -> Tuple[Dict[str, np.ndarray], np.ndarray, np.ndarray]:
    """
    Computes TFR and band power for each trial individually.
    Averages across channels within each trial before computing TFR.

    Parameters
    ----------
    epochs : np.ndarray
        Epoched LFP data (n_trials, n_channels, n_samples).
    fs : float
        Sampling frequency.
    nperseg : int
        FFT window length.
    noverlap : int
        Overlap between FFT windows.
    freq_range : Tuple[float, float]
        Frequency range to compute TFR.
    bands_dict : Dict[str, Tuple[float, float]]
        Dictionary of band names and their frequency ranges.

    Returns
    -------
    Tuple[Dict[str, np.ndarray], np.ndarray, np.ndarray]
        - trial_band_powers: {band_name: np.ndarray(n_trials, n_times_out)}
        - freqs: np.ndarray (n_freqs,)
        - times_ms: np.ndarray (n_times_out,)
    """
    n_trials, n_channels, n_samples = epochs.shape
    if n_trials == 0 or n_samples == 0:
        return {band: np.array([]) for band in bands_dict}, np.array([]), np.array([])

    trial_band_powers: Dict[str, List[np.ndarray]] = {band: [] for band in bands_dict}
    all_trial_tfrs: List[np.ndarray] = []
    tfr_freqs, tfr_times_ms = np.array([]), np.array([])

    for i_trial in range(n_trials):
        # Average across channels for this trial to get a 1D signal
        sig_trial = np.nanmean(epochs[i_trial, :, :], axis=0)

        # Compute spectrogram for this single-trial, channel-averaged signal
        f, t, sxx = spectrogram(
            sig_trial, fs=fs,
            window=DEFAULT_WF_PARAMS["window"],
            nperseg=nperseg, noverlap=noverlap,
            scaling="density", mode="psd",
        )
        
        # Filter frequencies
        f_mask = (f >= freq_range[0]) & (f <= freq_range[1])
        f_out  = f[f_mask]
        pxx    = sxx[f_mask, :]
        pxx_db = 10.0 * np.log10(np.abs(pxx) + 1e-12)
        t_ms   = t * 1000.0

        all_trial_tfrs.append(pxx_db)
        if tfr_freqs.size == 0:
            tfr_freqs = f_out
            tfr_times_ms = t_ms

        # Extract band powers for this trial
        for band_name, (f_min, f_max) in bands_dict.items():
            band_f_mask = (f_out >= f_min) & (f_out < f_max)
            if np.any(band_f_mask):
                band_power_tfr_slice = np.nanmean(pxx_db[band_f_mask, :], axis=0)
                trial_band_powers[band_name].append(band_power_tfr_slice)
            else:
                trial_band_powers[band_name].append(np.full_like(t_ms, np.nan)) # Use nan for missing bands
    
    # Stack trial band powers
    final_trial_band_powers = {
        band: np.stack(trial_band_powers[band], axis=0) if trial_band_powers[band] else np.array([])
        for band in bands_dict
    }

    return final_trial_band_powers, tfr_freqs, tfr_times_ms


# ----------------------------------------------------------------------------
# Main LFP Analysis Pipeline Execution
# ----------------------------------------------------------------------------
def run_lfp_pipeline():
    print("Starting LFP Analysis Pipeline...")

    # Main data structure to hold all processed data
    global_processed_data = {
        'lfp_tfr': {}, # Stores trial-averaged TFRs for plot 05 (mean across trials/channels)
        'lfp_band_power': {}, # Stores mean, SEM, N for band power (per presentation)
        'spiking_firing_rate': {},
        'mua': {},
        'behavioral_eye': {},
        'session_metadata': {}, # Stores session-level info like electrodes and units
    }

    # Find all NWB files in the DATA_DIR
    nwb_files = list(DATA_DIR.glob("*.nwb"))
    if not nwb_files:
        print(f"No NWB files found in {DATA_DIR}. Exiting.")
        return

    for nwb_path in nwb_files:
        session_id = nwb_path.stem
        print(f"
Processing session: {session_id}")
        
        # --- Initialize session data structure ---
        global_processed_data['lfp_tfr'][session_id] = {}
        global_processed_data['lfp_band_power'][session_id] = {}
        global_processed_data['spiking_firing_rate'][session_id] = {}
        global_processed_data['mua'][session_id] = {}
        global_processed_data['behavioral_eye'][session_id] = {}
        global_processed_data['session_metadata'][session_id] = {}


        # --- Stage 0: Initial Load & Validate ---
        # 0.1 Load session data
        session = lfp_io.load_session(nwb_path)
        session["fs"] = FS_LFP # Ensure sampling rate is set
        
        # 0.2 Validate session schema (Step 1)
        session, qc_flags = lfp_pipeline.validate_session_schema(session)
        if qc_flags:
            warnings.warn(f"QC issues for {session_id}: {qc_flags}", RuntimeWarning)
        
        # Check if LFP data exists after validation
        if session["lfp"] is None or session["lfp"].size == 0:
            print(f"No valid LFP data for session {session_id}. Skipping.")
            continue

        # 0.3 Build event table (using lfp_events)
        event_table = lfp_events.build_event_table(session)
        if event_table.empty:
            print(f"No valid event table for session {session_id}. Skipping.")
            continue
            
        # 0.4 Build omission windows (Step 2)
        omission_windows_data = lfp_pipeline.build_omission_windows(event_table)

        # --- New Stage: Laminar Mapping for each Probe ---
        print(f"  Performing laminar mapping for session {session_id}...")
        updated_electrodes = session["electrodes"].copy()
        
        # Initialize 'layer' column if it doesn't exist to avoid KeyError later
        if 'layer' not in updated_electrodes.columns:
            updated_electrodes['layer'] = 'Unknown'

        # Ensure 'probe_id' is present for iteration
        if 'probe_id' not in updated_electrodes.columns:
            warnings.warn(f"No 'probe_id' column found in electrodes for {session_id}. Cannot perform laminar mapping.", RuntimeWarning)
            unique_probes = []
        else:
            unique_probes = updated_electrodes['probe_id'].dropna().unique()
        
        for probe_id in unique_probes:
            probe_df = updated_electrodes[updated_electrodes['probe_id'] == probe_id].copy()
            probe_channels_global_idx = probe_df.index.tolist()
            
            if not probe_channels_global_idx:
                warnings.warn(f"No channels found for probe {probe_id} in session {session_id}. Skipping.", RuntimeWarning)
                continue

            # For laminar mapping, we need LFP data epoched into (trials, channels, samples)
            # Use a robust condition like 'RRRR' for good SNR if possible
            rrrr_events = event_table[event_table['condition'] == 'RRRR'].copy()
            if rrrr_events.empty:
                warnings.warn(f"No 'RRRR' condition trials for probe {probe_id} in session {session_id}. Skipping laminar mapping for this probe.", RuntimeWarning)
                updated_electrodes.loc[probe_df.index, 'layer'] = 'Unknown' # Mark as unknown if no data for mapping
                continue
                
            # Epoch LFP data for the current probe's channels based on 'RRRR' events
            # Use a wide window that covers the TFR analysis window for spectrolaminar profiles
            lfp_epoched_probe = _epoch_lfp_data(
                session["lfp"], rrrr_events, probe_channels_global_idx, session["fs"],
                window_ms= (-2000, 8000) # Extended window to cover necessary samples
            )
            
            if lfp_epoched_probe.size == 0:
                 warnings.warn(f"Failed to epoch LFP for probe {probe_id} (RRRR condition) in session {session_id}. Skipping laminar mapping for this probe.", RuntimeWarning)
                 updated_electrodes.loc[probe_df.index, 'layer'] = 'Unknown' # Mark as unknown if no data for mapping
                 continue

            # Get laminar crossover
            crossover_idx = lfp_laminar_mapping.get_laminar_crossover(
                lfp_epoched_probe, session["fs"], OUTPUT_DIR, session_id, probe_id
            )
            
            # Map channels to layers and update the main electrodes DataFrame
            if not np.isnan(crossover_idx):
                # Ensure probe_df used here has 'depth' column
                if 'depth' not in probe_df.columns:
                     warnings.warn(f"Probe {probe_id} electrode_df has no 'depth' column. Cannot map layers. Layers set to 'Unknown'.", RuntimeWarning)
                     updated_electrodes.loc[probe_df.index, 'layer'] = 'Unknown'
                else:
                    mapped_probe_df = lfp_laminar_mapping.map_channels_to_layers(
                        probe_df, crossover_idx, lfp_laminar_mapping.CHANNEL_SPACING
                    )
                    # Update layers in the main updated_electrodes DataFrame
                    updated_electrodes.loc[mapped_probe_df.index, 'layer'] = mapped_probe_df['layer']
            else:
                warnings.warn(f"Could not determine L4 crossover for probe {probe_id} in session {session_id}. Layers set to 'Unknown'.", RuntimeWarning)
                updated_electrodes.loc[probe_df.index, 'layer'] = 'Unknown'

        # Update the session with the new electrodes DataFrame including layer info
        session["electrodes"] = updated_electrodes
        print(f"  Laminar mapping completed for session {session_id}. Layers added to electrodes.")

        # Reconstruct session["channel_areas"] from updated_electrodes
        session["channel_areas"] = {
            ch_idx: row['location']
            for ch_idx, row in session["electrodes"].iterrows()
            if 'location' in row and pd.notna(row['location'])
        }

        # --- Integrate Spiking Data (Units) ---
        print(f"  Processing spiking data for session {session_id}...")
        if not session["units"].empty:
            # Merge unit data with electrode information to get area, probe, layer for each unit
            # Assuming 'electrode_idx' or 'peak_channel_id' links units to electrodes
            if 'electrode_idx' in session["units"].columns:
                unit_electrode_map_col = 'electrode_idx'
            elif 'peak_channel_id' in session["units"].columns:
                unit_electrode_map_col = 'peak_channel_id'
            else:
                warnings.warn(f"No 'electrode_idx' or 'peak_channel_id' found in units for {session_id}. Cannot link units to electrodes.", RuntimeWarning)
                unit_electrode_map_col = None

            if unit_electrode_map_col:
                # Ensure the column used for merging exists and is of correct type
                if unit_electrode_map_col not in session["units"].columns:
                    warnings.warn(f"Merge column '{unit_electrode_map_col}' not found in units. Skipping unit-electrode merge.", RuntimeWarning)
                else:
                    session["units"] = session["units"].merge(
                        session["electrodes"][['probe_id', 'location', 'layer']], # 'location' is the area
                        left_on=unit_electrode_map_col,
                        right_index=True,
                        how='left'
                    ).rename(columns={'location': 'area'})
                
                # Populate global_processed_data['spiking_firing_rate']
                for unit_id, unit_row in session["units"].iterrows():
                    unit_area = unit_row.get('area', 'Unknown')
                    unit_layer = unit_row.get('layer', 'Unknown')
                    
                    if unit_area == 'Unknown' or unit_layer == 'Unknown':
                         warnings.warn(f"Unit {unit_id} has unknown area or layer. Skipping firing rate calculation.", RuntimeWarning)
                         continue

                    # Create nested dictionaries for session, area, layer
                    if unit_area not in global_processed_data['spiking_firing_rate'][session_id]:
                        global_processed_data['spiking_firing_rate'][session_id][unit_area] = {}
                    if unit_layer not in global_processed_data['spiking_firing_rate'][session_id][unit_area]:
                        global_processed_data['spiking_firing_rate'][session_id][unit_area][unit_layer] = {}
                    
                    global_processed_data['spiking_firing_rate'][session_id][unit_area][unit_layer][unit_id] = {}

                    for cond in ALL_CONDITIONS:
                        cond_events = event_table[event_table['condition'] == cond].copy()
                        if cond_events.empty:
                            continue
                        
                        binned_spikes = _epoch_spike_times(
                            unit_row['spike_times'],
                            cond_events,
                            session["fs"],
                            window_ms=(-500, 4000), # Standard analysis window
                            bin_size_ms=50.0 # Example bin size
                        )
                        # Convert to firing rate (spikes/sec)
                        # firing_rate is (n_trials, n_bins)
                        firing_rate_per_trial = binned_spikes * (1000.0 / bin_size_ms) # Convert to Hz

                        # Calculate mean firing rate across trials
                        mean_firing_rate_ts = np.nanmean(firing_rate_per_trial, axis=0) # (n_bins,)

                        # Generate corresponding time bins for the firing rate time series
                        # This should match the binning used in _epoch_spike_times
                        window_start_ms = window_ms[0]
                        window_end_ms = window_ms[1]
                        
                        # Calculate time_bins_ms based on the actual number of bins and bin_size_ms
                        # The start of the first bin is window_start_ms
                        firing_rate_time_bins_ms = np.arange(
                            window_start_ms,
                            window_start_ms + len(mean_firing_rate_ts) * bin_size_ms,
                            bin_size_ms
                        ) + (bin_size_ms / 2.0) # Center of the bins

                        # Store in global_processed_data
                        global_processed_data['spiking_firing_rate'][session_id][unit_area][unit_layer][unit_id][cond] = {
                            'firing_rate_ts': mean_firing_rate_ts,
                            'time_bins_ms': firing_rate_time_bins_ms
                        }
                # After populating global_processed_data['spiking_firing_rate'][session_id]
                # Generate Figure 03 (Population Firing Rate) for each condition
                if global_processed_data['spiking_firing_rate'][session_id]: # Check if any unit data was processed
                    print(f"  Generating Figure 03 for session {session_id}...")
                    for cond in ALL_CONDITIONS:
                        # The create_population_firing_figure function expects data_to_plot in the format:
                        # {area: {layer: {unit_id: {cond: {'firing_rate_ts': array, 'time_bins_ms': array}}}}}
                        # global_processed_data['spiking_firing_rate'][session_id] already has this structure.

                        # Check if there's data for this condition before plotting
                        has_data_for_condition = False
                        for area_data in global_processed_data['spiking_firing_rate'][session_id].values():
                            for layer_data in area_data.values():
                                for unit_data in layer_data.values():
                                    if cond in unit_data and unit_data[cond].get('firing_rate_ts', np.array([])).size > 0:
                                        has_data_for_condition = True
                                        break
                                if has_data_for_condition: break
                            if has_data_for_condition: break

                        if has_data_for_condition:
                            lfp_plotting_utils.create_population_firing_figure(
                                session_id=session_id,
                                data_to_plot=global_processed_data['spiking_firing_rate'][session_id], # Pass the full structure for this session
                                condition=cond,
                                output_dir=FIG_03_OUTPUT_DIR
                            )
                        else:
                            print(f"  No spiking data for condition {cond} in session {session_id} for Figure 03. Skipping.")

            else:
                print(f"  Skipping spiking data processing for {session_id}: cannot link units to electrodes.")
        else:
            print(f"  No unit data found for session {session_id}.")

        # --- Integrate Behavioral Data (Eye-tracking from NPY) ---
        print(f"  Loading behavioral data for session {session_id}...")
        bhv_dir = DATA_DIR / "behavioral"
        for cond_name in ALL_CONDITIONS:
            bhv_paths = list(bhv_dir.glob(f"ses{session_id}-behavioral-{cond_name}.npy"))
            if bhv_paths:
                try:
                    data = np.load(bhv_paths[0]) # (n_trials, n_eye_channels, n_samples)
                    data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
                    
                    # Populate global_processed_data['behavioral_eye']
                    if cond_name not in global_processed_data['behavioral_eye'][session_id]:
                        global_processed_data['behavioral_eye'][session_id][cond_name] = {}
                    
                    # Extract for each presentation
                    for pres_key, pres_timing in SEQUENCE_TIMING.items():
                        start_sample = int(TIMING_MS.get(pres_key, 0) * session["fs"] / 1000) # Use 0 for fx and other derived timings
                        end_sample = int(SEQUENCE_TIMING[pres_key]['end'] * session["fs"] / 1000)
                        
                        # Ensure samples are within data bounds (0 to 6000 for behavioral NPY)
                        start_sample = max(0, start_sample)
                        end_sample = min(data.shape[2], end_sample)

                        if start_sample < end_sample:
                            # Average X and Y eye position over trials and over the presentation window
                            eye_x_avg = np.nanmean(data[:, 0, start_sample:end_sample])
                            eye_y_avg = np.nanmean(data[:, 1, start_sample:end_sample])
                            global_processed_data['behavioral_eye'][session_id][cond_name][pres_key] = {
                                'eye_x_avg': eye_x_avg,
                                'eye_y_avg': eye_y_avg
                            }
                        else:
                            global_processed_data['behavioral_eye'][session_id][cond_name][pres_key] = {
                                'eye_x_avg': np.nan,
                                'eye_y_avg': np.nan
                            }
                    # Also include 'fx' as a presentation for baseline eye movements
                    fx_start_sample = int(TIMING_MS['fx'] * session["fs"] / 1000)
                    fx_end_sample = 0 # Up to p1 onset
                    
                    fx_start_sample = max(0, fx_start_sample)
                    fx_end_sample = min(data.shape[2], fx_end_sample)

                    if fx_start_sample < fx_end_sample:
                        eye_x_avg_fx = np.nanmean(data[:, 0, fx_start_sample:fx_end_sample])
                        eye_y_avg_fx = np.nanmean(data[:, 1, fx_start_sample:fx_end_sample])
                        global_processed_data['behavioral_eye'][session_id][cond_name]['fx'] = {
                            'eye_x_avg': eye_x_avg_fx,
                            'eye_y_avg': eye_y_avg_fx
                        }
                    else:
                        global_processed_data['behavioral_eye'][session_id][cond_name]['fx'] = {
                            'eye_x_avg': np.nan,
                            'eye_y_avg': np.nan
                        }

                except Exception as e:
                    warnings.warn(f"Error processing behavioral NPY for {session_id}-{cond_name}: {e}", RuntimeWarning)
            
        if not global_processed_data['behavioral_eye'][session_id]:
            print(f"  No behavioral NPY data found for session {session_id}.")


        # --- Stage 1: Preprocessing & Epoching ---
        # 1.1 Run LFP QC (Step 3)
        lfp_qc_report = lfp_pipeline.run_lfp_qc(
            session["lfp"], fs=session["fs"], channel_ids=session["channels"]
        )
        bad_channels_global_idx = list(
            set(lfp_qc_report["flat_channels"] + lfp_qc_report["noisy_channels"])
        )
        if not lfp_qc_report["passed"]:
            warnings.warn(f"LFP QC failed for {session_id}: {lfp_qc_report}", RuntimeWarning)
            
        # 1.2 Apply bipolar referencing and group LFP by area (helper function)
        # Use updated electrodes here to respect 'bad_channels' and 'layer'
        lfp_by_area_bipolar = _apply_bipolar_ref_per_area(
            session["lfp"],
            session["channel_areas"], # Note: this is actually unused in _apply_bipolar_ref_per_area, updated_electrodes is used directly. This parameter can be removed.
            session["electrodes"], # Use the updated electrode_df which now has layer info
            bad_channels_global_idx,
        )
        if not lfp_by_area_bipolar:
            print(f"No valid LFP data after bipolar referencing for session {session_id}. Skipping.")
            continue

        # 1.3 Extract matched epochs (Step 4)
        epochs_by_area = lfp_pipeline.extract_matched_epochs(
            lfp_by_area_bipolar, event_table, omission_windows_data, fs=session["fs"]
        )
        if not epochs_by_area:
            print(f"No epochs extracted for session {session_id}. Skipping.")
            continue
            
        # 1.4 Normalize epochs (Step 5)
        normalized_epochs_by_area = lfp_pipeline.normalize_epochs(
            epochs_by_area, baseline_win_ms=omission_windows_data["baseline_win"], fs=session["fs"]
        )
        
        # --- Integrate MUA Data Processing ---
        print(f"  Processing MUA data for session {session_id}...")
        
        # We need epoched MUA per condition. MUA is per-channel.
        # So we first compute raw MUA for each channel, then epoch it per condition.
        raw_mua_traces = {} # {ch_idx: 1D_mua_trace}
        for ch_idx in session["channels"]:
            if ch_idx in bad_channels_global_idx: continue
            lfp_channel_data = session["lfp"][ch_idx, :]
            raw_mua_traces[ch_idx] = _compute_mua(lfp_channel_data, session["fs"])

        # Populate global_processed_data['mua']
        for area in session["areas"]: # Iterate through areas from session (locations in NWB)
            if area not in global_processed_data['mua'][session_id]:
                global_processed_data['mua'][session_id][area] = {}
            
            area_channels = session["electrodes"][(session["electrodes"]["location"] == area) & (~session["electrodes"].index.isin(bad_channels_global_idx))].index.tolist()
            
            for layer in updated_electrodes['layer'].dropna().unique():
                channels_in_layer = session["electrodes"][(session["electrodes"]["location"] == area) & (session["electrodes"]["layer"] == layer) & (~session["electrodes"].index.isin(bad_channels_global_idx))].index.tolist()
                
                if not channels_in_layer:
                    continue

                if layer not in global_processed_data['mua'][session_id][area]:
                    global_processed_data['mua'][session_id][area][layer] = {}
                
                for cond in ALL_CONDITIONS:
                    cond_events = event_table[event_table['condition'] == cond].copy()
                    if cond_events.empty:
                        continue
                    
                    if cond not in global_processed_data['mua'][session_id][area][layer]:
                        global_processed_data['mua'][session_id][area][layer][cond] = {}

                    # Collect epoched MUA for channels in this layer and condition
                    mua_epoched_for_layer = []
                    for ch_idx in channels_in_layer:
                        if ch_idx in raw_mua_traces:
                            # _epoch_lfp_data can epoch a single channel's MUA trace
                            mua_epoched = _epoch_lfp_data(
                                raw_mua_traces[ch_idx][None, :], # Wrap in a 2D array (1, n_samples)
                                cond_events,
                                [0], # The single "channel" in the wrapped array
                                session["fs"],
                                window_ms=(-1000, 5000) # Standard LFP epoch window
                            )
                            if mua_epoched.size > 0:
                                mua_epoched_for_layer.append(np.nanmean(mua_epoched, axis=0).flatten()) # Average across trials
                    
                    if not mua_epoched_for_layer:
                        continue

                    # Average MUA across channels in the layer
                    avg_mua_across_channels = np.nanmean(np.stack(mua_epoched_for_layer, axis=0), axis=0)
                    
                    # Store MUA per presentation
                    for pres_key, pres_timing in SEQUENCE_TIMING.items():
                        start_sample = int(TIMING_MS.get(pres_key, 0) * session["fs"] / 1000)
                        end_sample = int(SEQUENCE_TIMING[pres_key]['end'] * session["fs"] / 1000)
                        
                        # Ensure samples are within data bounds
                        start_sample = max(0, start_sample)
                        end_sample = min(len(avg_mua_across_channels), end_sample)

                        if start_sample < end_sample:
                            global_processed_data['mua'][session_id][area][layer][cond][pres_key] = 
                                np.nanmean(avg_mua_across_channels[start_sample:end_sample])
                        else:
                            global_processed_data['mua'][session_id][area][layer][cond][pres_key] = np.nan
                    
                    # Also include 'fx'
                    fx_start_sample = int(TIMING_MS['fx'] * session["fs"] / 1000)
                    fx_end_sample = int(TIMING_MS['p1'] * session["fs"] / 1000)
                    
                    fx_start_sample = max(0, fx_start_sample)
                    fx_end_sample = min(len(avg_mua_across_channels), fx_end_sample)

                    if fx_start_sample < fx_end_sample:
                        global_processed_data['mua'][session_id][area][layer][cond]['fx'] = 
                            np.nanmean(avg_mua_across_channels[fx_start_sample:fx_end_sample])
                    else:
                        global_processed_data['mua'][session_id][area][layer][cond]['fx'] = np.nan
        

        # --- Stage 2: Time-Frequency Analysis ---
        # 2.1 Compute TFR per condition (Step 6)
        # Use full epoch window for TFR if not specified otherwise in pipeline
        # `lfp_pipeline.compute_tfr_per_condition` uses its own window internally
        # This tfr_by_area still returns mean TFRs for plotting Figure 05
        tfr_by_area_mean = lfp_pipeline.compute_tfr_per_condition(
            normalized_epochs_by_area, 
            fs=session["fs"],
            freq_range=(2, 150), # As per GAMMA plan
            freq_step=2 # As per GAMMA plan
        )
        
        # Populate global_processed_data['lfp_tfr'] with mean TFRs (for Fig 05)
        for area, cond_tfrs in tfr_by_area_mean.items():
            if area not in global_processed_data['lfp_tfr'][session_id]:
                global_processed_data['lfp_tfr'][session_id][area] = {}

            for cond, tfr_data in cond_tfrs.items():
                if cond not in global_processed_data['lfp_tfr'][session_id][area]:
                    global_processed_data['lfp_tfr'][session_id][area][cond] = {}
                
                # Store full TFR data (averaged across channels/layers for this area)
                global_processed_data['lfp_tfr'][session_id][area][cond]['full_tfr'] = tfr_data[2] # (freqs, times)
                global_processed_data['lfp_tfr'][session_id][area][cond]['freqs'] = tfr_data[0]
                global_processed_data['lfp_tfr'][session_id][area][cond]['times'] = tfr_data[1]

                # Generate Figure 05 (TFR per condition)
                if tfr_data[2].size > 0: # Check if power_db array is not empty
                    lfp_plotting_utils.create_tfr_figure_per_condition(
                        session_id=session_id,
                        area=area,
                        condition=cond,
                        tfr_data=tfr_data[2],
                        freqs=tfr_data[0],
                        times=tfr_data[1],
                        output_dir=FIG_05_OUTPUT_DIR
                    )
        
        # --- Compute Trial-Level Band Power (for SEM and Figure 06) ---
        trial_band_powers_by_area: Dict[str, Dict[str, Dict[str, np.ndarray]]] = {} # area -> cond -> band -> (n_trials, n_times)
        tfr_times_ms_for_bands = np.array([])
        
        for area, cond_epochs in normalized_epochs_by_area.items():
            trial_band_powers_by_area[area] = {}
            for cond, epochs in cond_epochs.items():
                if epochs.size == 0: continue
                
                trial_band_powers_dict, _, tfr_times_ms_for_bands = _compute_trial_tfr_and_band_power(
                    epochs, session["fs"], DEFAULT_WF_PARAMS["nperseg"], DEFAULT_WF_PARAMS["noverlap"]
                )
                trial_band_powers_by_area[area][cond] = trial_band_powers_dict

        # Populate global_processed_data['lfp_band_power'] with mean, SEM, N
        for area, cond_band_powers in trial_band_powers_by_area.items():
            if area not in global_processed_data['lfp_band_power'][session_id]:
                global_processed_data['lfp_band_power'][session_id][area] = {}

            for cond, band_powers_dict in cond_band_powers.items():
                if cond not in global_processed_data['lfp_band_power'][session_id][area]:
                    global_processed_data['lfp_band_power'][session_id][area][cond] = {}
                
                for band_name, trial_band_data_series in band_powers_dict.items(): # (n_trials, n_times_out)
                    if trial_band_data_series.size == 0:
                        continue
                    
                    if band_name not in global_processed_data['lfp_band_power'][session_id][area][cond]:
                        global_processed_data['lfp_band_power'][session_id][area][cond][band_name] = {}

                    # Store band power stats for each presentation
                    for pres_key, pres_timing in SEQUENCE_TIMING.items():
                        # Times are relative to p1 onset = 0ms
                        start_time = TIMING_MS.get(pres_key, 0)
                        end_time = SEQUENCE_TIMING[pres_key]['end'] if pres_key in SEQUENCE_TIMING else start_time + 100 # Fallback
                        
                        time_bins = tfr_times_ms_for_bands
                        relevant_time_bins_mask = (time_bins >= start_time) & (time_bins < end_time)

                        if np.any(relevant_time_bins_mask):
                            # Calculate mean, SEM, N from trial-level data within the presentation window
                            data_in_window = trial_band_data_series[:, relevant_time_bins_mask] # (n_trials, n_timepoints_in_window)
                            mean_val = np.nanmean(data_in_window)
                            n_trials_present = data_in_window.shape[0]
                            sem_val = np.nanstd(data_in_window) / np.sqrt(n_trials_present) if n_trials_present > 1 else np.nan

                            global_processed_data['lfp_band_power'][session_id][area][cond][band_name][pres_key] = {
                                'mean': mean_val,
                                'sem': sem_val,
                                'n_trials': n_trials_present,
                                'time_series': np.nanmean(data_in_window, axis=0) # Store time series for plotting as well
                            }
                        else:
                            global_processed_data['lfp_band_power'][session_id][area][cond][band_name][pres_key] = {
                                'mean': np.nan, 'sem': np.nan, 'n_trials': 0, 'time_series': np.array([])
                            }
                    
                    # Also include 'fx'
                    fx_start_time = TIMING_MS['fx']
                    fx_end_time = TIMING_MS['p1']
                    
                    time_bins = tfr_times_ms_for_bands
                    relevant_time_bins_mask = (time_bins >= fx_start_time) & (time_bins < fx_end_time)

                    if np.any(relevant_time_bins_mask):
                        data_in_window = trial_band_data_series[:, relevant_time_bins_mask]
                        mean_val = np.nanmean(data_in_window)
                        n_trials_present = data_in_window.shape[0]
                        sem_val = np.nanstd(data_in_window) / np.sqrt(n_trials_present) if n_trials_present > 1 else np.nan
                        global_processed_data['lfp_band_power'][session_id][area][cond][band_name]['fx'] = {
                            'mean': mean_val,
                            'sem': sem_val,
                            'n_trials': n_trials_present,
                            'time_series': np.nanmean(data_in_window, axis=0) # Store time series for plotting as well
                        }
                    else:
                        global_processed_data['lfp_band_power'][session_id][area][cond][band_name]['fx'] = {
                            'mean': np.nan, 'sem': np.nan, 'n_trials': 0, 'time_series': np.array([])
                        }
        
        # --- Store final electrodes and units info in session_metadata ---
        global_processed_data['session_metadata'][session_id]['electrodes'] = session["electrodes"]
        global_processed_data['session_metadata'][session_id]['units'] = session["units"]
        global_processed_data['session_metadata'][session_id]['omission_windows'] = omission_windows_data
        global_processed_data['session_metadata'][session_id]['event_table'] = event_table
        
        # 2.2 Compute band contrast (Step 7) - This is still per-session, need to rethink for global.
        # This part of the pipeline was primarily for the `lfp_pipeline` module itself to produce output.
        # For the global structure, we've already extracted `lfp_band_power`.
        # We can compute contrasts later from `global_processed_data['lfp_band_power']`.
        band_contrasts = {} # Clear this for now to avoid confusion with global_processed_data.
        

        # --- Stage 3: Connectivity & Statistical Analysis ---
        # These steps would typically require aggregating across sessions for robust results.
        # For a single session run, we'll demonstrate the call and store minimal outputs.
        
        # 3.1 Spectral Correlation Matrices (Step 8) - Needs per-trial band power
        # For now, placeholder as before. Actual implementation requires storing per-trial
        # band power in the global data structure if not already doing so.
        spectral_correlations = {
            "RRRR_beta_stim": np.random.rand(len(CANONICAL_AREAS), len(CANONICAL_AREAS)),
            "RXRR_beta_omit": np.random.rand(len(CANONICAL_AREAS), len(CANONICAL_AREAS)),
        }
        
        # 3.2 Inter-area coherence spectra (Step 9)
        # This requires epoch data *before* mean-collapsing for TFR
        coherence_results = lfp_pipeline.compute_all_pairs_coherence(
            lfp_by_area_bipolar, CANONICAL_AREAS, fs=session["fs"]
        )

        # 3.3 Coherence Network Adjacency (Step 10)
        adjacency_matrices = {}
        for band_name in BANDS.keys():
            adj_mat = lfp_pipeline.build_coherence_network_data(
                coherence_results, CANONICAL_AREAS, band=band_name, bands=BANDS
            )
            adjacency_matrices[band_name] = adj_mat
            
        # 3.4 Spectral Granger Causality (Step 11)
        granger_results = {}
        if len(lfp_by_area_bipolar) >= 2:
            # Example: V1 vs PFC
            area1 = CANONICAL_AREAS[0] if CANONICAL_AREAS[0] in lfp_by_area_bipolar else None
            area2 = CANONICAL_AREAS[1] if CANONICAL_AREAS[1] in lfp_by_area_bipolar else None
            
            if area1 and area2:
                sig1 = np.nanmean(lfp_by_area_bipolar[area1], axis=0) # Mean across channels for 1D signal
                sig2 = np.nanmean(lfp_by_area_bipolar[area2], axis=0)
                if sig1.size > 0 and sig2.size > 0:
                    granger_results[f"{area1}_to_{area2}"] = lfp_pipeline.compute_spectral_granger(
                        sig1, sig2, fs=session["fs"]
                    )
        
        # 3.5 Cluster Permutation Statistics (Step 12)
        # This is context-dependent. Example: compare two TFRs.
        # Placeholder for actual usage, will need more specific data.
        cluster_perm_results = {}
        # if "RXRR_vs_RRRR" in band_contrasts and "Beta" in band_contrasts["RXRR_vs_RRRR"]: # band_contrasts is empty
        #     dummy_x = np.random.rand(10, 100) # 10 trials, 100 time points
        #     dummy_y = np.random.rand(10, 100)
        #     cluster_perm_results["example_contrast"] = lfp_stats.run_cluster_permutation(dummy_x, dummy_y)

        # 3.6 Hierarchy Tier Aggregation (Step 13)
        # Example: Aggregate mean beta power contrast
        # This will operate on data from global_processed_data, not band_contrasts
        beta_contrast_mean_by_area = {} # Placeholder for now
        tier_summaries = lfp_pipeline.aggregate_by_tier(beta_contrast_mean_by_area, tiers=AREA_TIERS)
        
        # 3.7 Post-Omission Adaptation (Step 14)
        # This requires trial-level band power data.
        # Placeholder for actual usage.
        post_omission_adapt_results = {}
        # Simulate band_power_by_trial: (n_trials, n_bands, n_times)
        sim_band_power_by_trial = np.random.rand(100, len(BANDS), 6000) 
        omission_trial_idx = 50 # example
        if sim_band_power_by_trial.shape[0] > omission_trial_idx + 5:
            post_omission_adapt_results = lfp_pipeline.compute_post_omission_adapt(
                sim_band_power_by_trial, omission_trial_idx, n_post=5, bands=BANDS
            )

        # NEW: Generate Figure 06 (Band Summary)
        # This version uses actual mean and SEM time series from trial_band_powers_by_area (for RRRR condition)
        data_for_fig06_plot = {}
        
        # Ensure tfr_times_ms_for_bands is available
        if tfr_times_ms_for_bands.size == 0:
            # Fallback in case no trial band power was computed
            for area, cond_tfrs in tfr_by_area_mean.items():
                for cond, tfr_data in cond_tfrs.items():
                    if tfr_data[1].size > 0:
                        tfr_times_ms_for_bands = tfr_data[1]
                        break
                if tfr_times_ms_for_bands.size > 0: break

        if tfr_times_ms_for_bands.size > 0:
            for area in trial_band_powers_by_area: # Iterate through areas that have trial band power data
                data_for_fig06_plot[area] = {}
                cond_to_plot = 'RRRR' # For now, focus on one condition for single-session plot

                if cond_to_plot in trial_band_powers_by_area[area]:
                    for band_name, trial_band_data_series in trial_band_powers_by_area[area][cond_to_plot].items():
                        if trial_band_data_series.size == 0:
                            continue

                        # Calculate mean and SEM across trials for the full time course
                        n_trials_band = trial_band_data_series.shape[0]
                        mean_series = np.nanmean(trial_band_data_series, axis=0)
                        # Ensure sem is calculated only if n_trials_band > 1
                        sem_series = np.nanstd(trial_band_data_series, axis=0) / np.sqrt(n_trials_band) if n_trials_band > 1 else np.full_like(mean_series, np.nan)
                        
                        data_for_fig06_plot[area][band_name] = {
                            'mean': mean_series,
                            'sem': sem_series
                        }
            
            if data_for_fig06_plot:
                lfp_plotting_utils.create_band_summary_figure(
                    data_to_plot=data_for_fig06_plot,
                    session_id=session_id,
                    output_dir=FIG_06_OUTPUT_DIR,
                    times=tfr_times_ms_for_bands
                )

        # --- Stage 4: Output & Reproducibility ---
        # 4.1 Write analysis manifest (Step 15)
        # Collect relevant parameters and dummy figure specs for the manifest
        analysis_params = {
            "fs": session["fs"],
            "nperseg": DEFAULT_WF_PARAMS["nperseg"],
            "noverlap": DEFAULT_WF_PARAMS["noverlap"],
            "bands": {k: list(v) for k, v in BANDS.items()},
            "alignment": "p1 onset = 0ms (code 101.0)",
            "baseline_window_ms": list(omission_windows_data["baseline_win"]),
            "normalization": "dB (10*log10(P/Pbase))",
            "bad_channels_count": len(bad_channels_global_idx),
            "processed_areas": list(epochs_by_area.keys()),
            "session_electrodes_info": session["electrodes"].to_dict(orient='records') # Include full electrode info
        }
        
        figure_specs = [
            {"fig_id": "fig_lfp_tfr_example", "title": "Example LFP TFR", "conditions": ALL_CONDITIONS, "bands": list(BANDS.keys()), "data_arrays_used": ["tfr_by_area"], "notes": "Generated from Step 6"},
            {"fig_id": "fig_band_contrast_example", "title": "Example Band Contrast", "conditions": ALL_CONDITIONS, "bands": list(BANDS.keys()), "data_arrays_used": ["band_contrasts"], "notes": "Generated from Step 7"},
            # Add more figure specs as actual figures are generated
        ]
        
        # Example output for a manifest; in a real scenario, full results are saved
        # as .npy files and references are made in the manifest.
        manifest_path = lfp_pipeline.write_analysis_manifest(
            out_dir=OUTPUT_DIR,
            session_id=session_id,
            figure_specs=figure_specs,
            analysis_params=analysis_params,
            band_data={"beta_contrast_mean": list(beta_contrast_mean_by_area.values())} # Example data for CSV
        )
        print(f"Manifest written to: {manifest_path}")
        
    print("
LFP Analysis Pipeline Completed for all sessions.")
    print("
Final Global Processed Data Structure:")
    
    # NEW: Save the global_processed_data for multi-session aggregation
    global_data_filepath = OUTPUT_DIR / "global_processed_data.pkl"
    try:
        with open(global_data_filepath, 'wb') as f:
            pickle.dump(global_processed_data, f)
        print(f"Global processed data saved to: {global_data_filepath}")
    except Exception as e:
        warnings.warn(f"Failed to save global processed data: {e}", RuntimeWarning)

    # Placeholder for Multi-session Aggregation and Figure Refinements
    print("
--- Multi-session Aggregation (Next Steps) ---")
    print("Load 'global_processed_data.pkl' to perform analyses across all sessions.")
    print("This is where Figure 06 (Band Summary) will be refined to merge omission conditions,")
    print("calculate SEM, and implement area ranking for a comprehensive plot.")
    # Example:
    # try:
    #     with open(global_data_filepath, 'rb') as f:
    #         all_sessions_data = pickle.load(f)
    #     print("Loaded global processed data for aggregation.")
    #     # Perform multi-session analysis here...
    #     # Refine Figure 06 here using all_sessions_data
    # except FileNotFoundError:
    #     warnings.warn("Global processed data file not found for aggregation.", RuntimeWarning)
    # except Exception as e:
    #     warnings.warn(f"Error loading global processed data for aggregation: {e}", RuntimeWarning)


if __name__ == "__main__":
    run_lfp_pipeline()
