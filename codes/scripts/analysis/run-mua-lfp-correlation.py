import glob
import os
from pathlib import Path
import numpy as np
import pandas as pd
import re
import json # Added for saving results

import codes.functions.io.lfp_io as lfp_io
import codes.functions.lfp.lfp_tfr as lfp_tfr
from codes.functions.lfp.lfp_laminar_mapping import get_laminar_crossover, map_channels_to_layers
from codes.functions.lfp.lfp_preproc import apply_bipolar_ref, extract_epochs
from scipy.stats import spearmanr

# Helper function (copied from the script for clarity)
def compute_mua_diff(spike_times, trials_pred, trials_unpred, tfr_times, fs):
    """
    Computes the difference in MUA firing rate between unpredictable and predictable conditions.
    """
    # Helper to create PSTH for a set of trials
    def get_psth_for_condition(trials, spike_times, tfr_times, fs):
        all_trial_psth = []
        
        # Align MUA bins with TFR time bins (tfr_times is in ms)
        tfr_times_s = tfr_times / 1000.0
        if len(tfr_times_s) <= 1: return np.array([])
        
        bin_width = tfr_times_s[1] - tfr_times_s[0]
        
        for _, trial in trials.iterrows():
            trial_start_s = trial['start_time']
            trial_stop_s = trial['stop_time']
            
            # This is simplified: assumes tfr_times are relative to trial start
            # A more robust approach would align to a specific event within the trial
            bins_edges_s = trial_start_s + tfr_times_s - (bin_width / 2)
            bins_edges_s = np.append(bins_edges_s, bins_edges_s[-1] + bin_width)

            # Get spikes within this trial's time range for binning
            spikes_in_trial_range = spike_times[
                (spike_times >= bins_edges_s[0]) & (spike_times <= bins_edges_s[-1])
            ]
            
            if spikes_in_trial_range.size > 0:
                mua_counts, _ = np.histogram(spikes_in_trial_range, bins=bins_edges_s)
                mua_rate = mua_counts / bin_width
                all_trial_psth.append(mua_rate)

        if not all_trial_psth:
            return np.zeros(len(tfr_times))

        # Pad PSTHs to the same length if they differ, then average
        max_len = max(len(p) for p in all_trial_psth)
        padded_psth = [np.pad(p, (0, max_len - len(p)), 'constant') for p in all_trial_psth]
        
        return np.nanmean(padded_psth, axis=0)

    psth_pred = get_psth_for_condition(trials_pred, spike_times, tfr_times, fs)
    psth_unpred = get_psth_for_condition(trials_unpred, spike_times, tfr_times, fs)
    
    # Ensure they are the same length before subtracting
    len_diff = len(psth_unpred) - len(psth_pred)
    if len_diff > 0:
        psth_pred = np.pad(psth_pred, (0, len_diff), 'constant')
    elif len_diff < 0:
        psth_unpred = np.pad(psth_unpred, (0, -len_diff), 'constant')
        
    return psth_unpred - psth_pred


def get_unit_to_area_map_from_session(session_data):
    unit_to_area = {}
    electrodes_df = session_data.get('electrodes')
    units_df = session_data.get('units')

    if electrodes_df is None or units_df is None or 'peak_channel_id' not in units_df.columns or 'location' not in electrodes_df.columns:
        print("Warning: Missing electrodes, units, or required columns for unit-to-area mapping.")
        return unit_to_area

    for unit_id, unit in units_df.iterrows():
        peak_channel = int(float(unit['peak_channel_id']))
        if peak_channel in electrodes_df.index:
            area = electrodes_df.loc[peak_channel]['location']
            unit_to_area[unit_id] = area
    return unit_to_area

def run_analysis():
    """
    Main function to run the MUA-LFP correlation analysis for Supplemental Figure 2.
    """
    nwb_data_dir = "D:/analysis/nwb"
    nwb_files = glob.glob(f"{nwb_data_dir}/**/*.nwb", recursive=True)
    
    if not nwb_files:
        print(f"No NWB files found in {nwb_data_dir}")
        return

    all_electrode_results = [] # To store correlation results for each electrode

    for nwb_file in nwb_files:
        session_id = Path(nwb_file).stem
        print(f"Processing session: {session_id}")
        session_data = lfp_io.load_session(Path(nwb_file))

        trials_df = session_data.get('trials')
        if trials_df is None:
            print(f"  No trials found for session {session_id}. Skipping.")
            continue

        # Load the condition table and merge it with the trials data
        # Let's assume the condition table is in the NWB file's directory
        condition_table = lfp_io.load_condition_table(Path(nwb_file).parent)
        if condition_table.empty:
            # As a fallback, check the 'omission' project root
            from codes.config.paths import PROJECT_ROOT
            project_root_cond_table = PROJECT_ROOT / "condition_table.csv"
            if project_root_cond_table.exists():
                print(f"  No condition_table.csv in session dir, using one from project root.")
                condition_table = lfp_io.load_condition_table(PROJECT_ROOT)
        if condition_table.empty:
            print(f"  No condition_table.csv found for session {session_id}. Skipping.")
            continue
            
        # Ensure 'trial_id' is of the same type for merging
        if 'trial_id' not in trials_df.columns:
            trials_df['trial_id'] = trials_df.index
        
        trials_df['trial_id'] = trials_df['trial_id'].astype(int)
        condition_table['trial_id'] = condition_table['trial_id'].astype(int)
        
        # Merge the condition information into the trials DataFrame
        trials_df = pd.merge(trials_df, condition_table[['trial_id', 'condition']], on='trial_id', how='left')

        if 'condition' not in trials_df.columns or trials_df['condition'].isnull().all():
            print(f"  'condition' column could not be added to trials for session {session_id}. Skipping.")
            continue
            
        predictable_trials = trials_df[trials_df['condition'] == 'predictable']
        unpredictable_trials = trials_df[trials_df['condition'] == 'unpredictable']
        
        if predictable_trials.empty or unpredictable_trials.empty:
            print(f"  Not enough predictable/unpredictable trials for session {session_id}. Skipping.")
            continue
        
        # Determine layers for all channels in this session
        channels_with_layers = pd.DataFrame()
        fs = 1000.0 # Assuming fs=1000Hz, this should be confirmed from NWB file if possible
        
        for probe_entry in session_data.get("lfp_probes", []):
            probe_id = probe_entry['id']
            lfp_data_probe_raw = probe_entry['data'] # Shape (n_timepoints, n_channels_on_probe)
            probe_electrode_ids = probe_entry['electrodes_ids']

            if lfp_data_probe_raw.ndim != 2 or lfp_data_probe_raw.shape[1] < 2:
                print(f"    Skipping probe {probe_id}: LFP data has unsupported dimensions or too few channels.")
                continue

            # Transpose LFP data for epoch extraction: (Channels, Samples)
            lfp_data_probe_transposed = lfp_data_probe_raw.T

            # Extract epochs for all trials to perform laminar mapping
            # Using a window that covers the trial duration, e.g., -1.25 to 1.25s
            # Note: extract_epochs expects event_table with 'start_time' in seconds
            # and returns (Trials, Channels, Samples)
            lfp_epochs = extract_epochs(
                lfp_data_probe_transposed,
                trials_df,
                window_ms=(-1250, 1250),
                fs=fs
            )

            if lfp_epochs.size == 0:
                print(f"    Skipping probe {probe_id}: Could not extract LFP epochs.")
                continue

            electrode_df_probe = session_data['electrodes'].loc[probe_electrode_ids].copy()
            if 'depth' not in electrode_df_probe.columns:
                print(f"    Warning: 'depth' column not found for probe {probe_id}. Cannot map layers.")
                electrode_df_probe['layer'] = 'Unknown'
                channels_with_layers = pd.concat([channels_with_layers, electrode_df_probe])
                continue

            crossover_idx = get_laminar_crossover(
                lfp_epochs,
                fs=fs,
                session_id=session_id,
                probe_id=probe_id
            )

            if not np.isnan(crossover_idx):
                probe_channels_with_layers = map_channels_to_layers(electrode_df_probe, crossover_idx)
                channels_with_layers = pd.concat([channels_with_layers, probe_channels_with_layers])
            else:
                print(f"    Could not determine L4 crossover for probe {probe_id}. All channels assigned 'Unknown' layer.")
                electrode_df_probe['layer'] = 'Unknown'
                channels_with_layers = pd.concat([channels_with_layers, electrode_df_probe])

        if channels_with_layers.empty:
            print(f"  No channels with layer information for session {session_id}. Skipping.")
            continue
            
        print(f"  Found {len(channels_with_layers)} channels with layer info.")
        
        # Apply bipolar referencing to LFP for each probe
        bipolar_lfp_probes = {}
        for probe_entry in session_data.get("lfp_probes", []):
            probe_id = probe_entry['id']
            lfp_data_probe_raw = probe_entry['data'] # (Samples, Channels)
            
            # apply_bipolar_ref expects (Channels, Samples), so we transpose
            lfp_transposed = lfp_data_probe_raw.T
            bipolar_lfp_transposed = apply_bipolar_ref(lfp_transposed)
            
            # Store the bipolar LFP data for this probe, mapping electrode IDs to their data
            # The output of apply_bipolar_ref is also (Channels, Samples)
            bipolar_lfp_probes[probe_id] = {
                'electrode_ids': probe_entry['electrodes_ids'],
                'data': bipolar_lfp_transposed # Keep it as (Channels, Samples)
            }
        
        # Loop through each electrode for per-electrode analysis
        units_df = session_data.get('units')
        
        for electrode_id, electrode_row in channels_with_layers.iterrows():
            print(f"    Processing electrode {electrode_id}...")

            # Find the probe this electrode belongs to
            probe_id_for_electrode = None
            probe_data = None
            for pid, p_data in bipolar_lfp_probes.items():
                if electrode_id in p_data['electrode_ids']:
                    probe_id_for_electrode = pid
                    probe_data = p_data
                    break
            
            if probe_id_for_electrode is None:
                print(f"      Could not find probe for electrode {electrode_id}. Skipping.")
                continue

            # 1. Get LFP data for this electrode (after bipolar ref)
            electrode_idx_in_probe = probe_data['electrode_ids'].index(electrode_id)
            lfp_electrode_continuous = probe_data['data'][electrode_idx_in_probe, :] # (Samples,)

            # 2. Get MUA data for this electrode
            if units_df is None:
                print(f"      No units data available for this session. Skipping electrode.")
                continue
            
            units_on_electrode = units_df[units_df['peak_channel_id'] == electrode_id]
            if units_on_electrode.empty:
                print(f"      No MUA data for electrode {electrode_id}. Skipping.")
                continue
            
            spike_times_on_electrode = np.concatenate(units_on_electrode['spike_times'].values)
            
            # --- Per-electrode processing logic ---
            
            # Epoch LFP data for predictable and unpredictable conditions
            lfp_epochs_pred = extract_epochs(lfp_electrode_continuous, predictable_trials, window_ms=(-1250, 1250), fs=fs)
            lfp_epochs_unpred = extract_epochs(lfp_electrode_continuous, unpredictable_trials, window_ms=(-1250, 1250), fs=fs)
            
            if lfp_epochs_pred.size == 0 or lfp_epochs_unpred.size == 0:
                print(f"      Could not extract LFP epochs for both conditions for electrode {electrode_id}. Skipping.")
                continue

            # Compute LFP power difference
            _, _, power_pred = lfp_tfr.compute_tfr(np.nanmean(lfp_epochs_pred, axis=0).squeeze(), fs=fs)
            freqs, times, power_unpred = lfp_tfr.compute_tfr(np.nanmean(lfp_epochs_unpred, axis=0).squeeze(), fs=fs)
            
            if power_pred.size == 0 or power_unpred.size == 0:
                 print(f"      Could not compute TFR for both conditions for electrode {electrode_id}. Skipping.")
                 continue

            lfp_power_diff = np.squeeze(power_unpred) - np.squeeze(power_pred) # (Freqs, Time)

            # --- MUA Difference Calculation ---
            mua_diff_time = compute_mua_diff(
                spike_times_on_electrode,
                predictable_trials,
                unpredictable_trials,
                times, # TFR times in ms
                fs
            )

            # --- Spearman Correlation ---
            correlation_spectrum = []
            for freq_idx in range(len(freqs)):
                lfp_power_time_series = lfp_power_diff[freq_idx, :]
                
                # Use spearmanr, it returns (correlation, p-value)
                corr, _ = spearmanr(mua_diff_time, lfp_power_time_series)
                correlation_spectrum.append(corr)

            # Store result for this electrode
            all_electrode_results.append({
                'session_id': session_id,
                'electrode_id': electrode_id,
                'area': electrode_row['location'],
                'layer': electrode_row['layer'],
                'correlation_spectrum': correlation_spectrum,
                'freqs': freqs.tolist()
            })

    print("Finished processing all sessions.")
    
    # Save the detailed per-electrode results
    output_path = Path("D:/drive/outputs/mua_lfp_correlation_per_electrode_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(all_electrode_results, f, indent=4)
    print(f"Per-electrode results saved to {output_path}")

    # Plot the results
    from codes.functions.visualization.lfp_plotting_sup_fig2 import plot_supplemental_figure_2
    output_dir = Path("D:/drive/outputs/mua-lfp-correlation")
    plot_supplemental_figure_2(all_electrode_results, output_dir)

if __name__ == "__main__":
    run_analysis()
