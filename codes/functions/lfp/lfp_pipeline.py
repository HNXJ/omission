import numpy as np
import pandas as pd
from pathlib import Path
from codes.functions.io.lfp_io import load_session

def get_signal_conditional(session_path: Path, area: str, signal_type: str = 'LFP', epoch_window: tuple = (-1.0, 4.0), align_to: str = 'P1', **kwargs):
    """
    Canonical accessor for neural signals from NWB.
    """
    print(f"[infile] lfp_pipeline.py [doing] Loading {signal_type} data for {area} from {session_path.name}")

    session_data = load_session(session_path)
    
    if signal_type in ['LFP', 'MUAe']:
        if session_data['lfp'] is None: 
            print(f"[infile] lfp_pipeline.py [doing] No LFP found in {session_path.name}")
            return np.array([])
        
        # Resolve channels
        electrodes = session_data['electrodes']
        if 'location' not in electrodes.columns:
            print(f"[infile] lfp_pipeline.py [doing] No 'location' column in electrodes for {session_path.name}")
            return np.array([])

        area_mask = electrodes['location'].apply(lambda loc: area in [a.strip() for a in str(loc).split(',')])
        area_channel_indices = np.where(area_mask)[0]
        if len(area_channel_indices) == 0: 
            print(f"[infile] lfp_pipeline.py [doing] No channels found for {area} in {session_path.name}")
            return np.array([])

        raw_data = session_data['lfp'][area_channel_indices, :] # (channels, time)
        timestamps = session_data['lfp_timestamps']
        fs = 1 / np.mean(np.diff(timestamps))
        
        # Epoching - look for alignment
        # Check trials table or interval table
        align_times = None
        if 'trials' in session_data and not session_data['trials'].empty and align_to in session_data['trials'].columns:
            align_times = session_data['trials'][align_to].values
        
        if align_times is None:
            # Fallback to interval tables
            from pynwb import NWBHDF5IO
            with NWBHDF5IO(str(session_path), 'r') as io:
                nwb = io.read()
                for interval_name in nwb.intervals:
                    df = nwb.intervals[interval_name].to_dataframe()
                    if 'codes' in df.columns and 101 in df['codes'].values:
                        align_times = df[df['codes'] == 101]['start_time'].values
                        break
        
        if align_times is None or len(align_times) == 0:
            print(f"[infile] lfp_pipeline.py [doing] No alignment events found for {align_to} in {session_path.name}")
            return raw_data # Return continuous stream as fallback

        start_pts = np.searchsorted(timestamps, align_times + epoch_window[0])
        end_pts = np.searchsorted(timestamps, align_times + epoch_window[1])
        
        n_trials = len(align_times)
        n_channels = len(area_channel_indices)
        n_samples = int((epoch_window[1] - epoch_window[0]) * fs)
        
        epochs = np.full((n_trials, n_channels, n_samples), np.nan)
        for i in range(n_trials):
            s, e = start_pts[i], end_pts[i]
            if s >= 0 and e <= len(timestamps):
                segment = raw_data[:, s:e]
                # Adjust if segment length doesn't match n_samples (due to diff rounding)
                limit = min(n_samples, segment.shape[1])
                epochs[i, :, :limit] = segment[:, :limit]
                
        return epochs

    elif signal_type == 'SPK':
        units = session_data['units']
        return units[units['location'] == area]['spike_times'].values if 'location' in units.columns else units['spike_times'].values
    
    raise ValueError(f"Unsupported signal_type: {signal_type}")


