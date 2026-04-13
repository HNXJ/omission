import numpy as np
import pandas as pd
from pathlib import Path
from codes.functions.lfp.lfp_mapping import resolve_area_membership
from codes.functions.io.lfp_io import load_session

def get_signal_conditional(session_path: Path, area: str, signal_type: str = 'LFP', epoch_window: tuple = (-1.0, 4.0), align_to: str = 'P1', **kwargs):
    """
    Canonical accessor for neural signals from NWB.
    """
    print(f"[infile] lfp_pipeline.py [doing] Loading {signal_type} data for {area} from {session_path.name}")

    session_data = load_session(session_path)
    
    if signal_type in ['LFP', 'MUAe']:
        if session_data['lfp'] is None: raise ValueError(f"No LFP data found in {session_path}")
        
        # Resolve channels
        electrodes = session_data['electrodes']
        area_mask = electrodes['location'].apply(lambda loc: area in [a.strip() for a in str(loc).split(',')])
        area_channel_indices = np.where(area_mask)[0]
        if len(area_channel_indices) == 0: raise ValueError(f"No channels found for area {area} in {session_path}")

        raw_data = session_data['lfp'][area_channel_indices, :] # (channels, time)
        timestamps = session_data['lfp_timestamps']
        fs = 1 / np.mean(np.diff(timestamps))
        
        # Epoching - look for P1 onset (code 101)
        # Load the raw interval table to find codes
        from pynwb import NWBHDF5IO
        with NWBHDF5IO(str(session_path), 'r') as io:
            nwb = io.read()
            # Try trials table, then interval table
            if hasattr(nwb, 'trials') and nwb.trials is not None and align_to in nwb.trials.colnames:
                align_times = nwb.trials[align_to][:]
            elif 'omission_glo_passive' in nwb.intervals:
                # Filter for code 101 as P1 onset
                df = nwb.intervals['omission_glo_passive'].to_dataframe()
                if 'codes' not in df.columns: raise ValueError("No 'codes' in omission_glo_passive table")
                # Assume start_time is the reference for the interval containing code 101
                align_times = df[df['codes'] == 101]['start_time'].values
            else:
                raise ValueError("Could not find trial alignment data.")
        
        if len(align_times) == 0:
            print(f"[infile] lfp_pipeline.py [doing] No trials found for {area} in {session_path.name}")
            return np.array([])

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
                epochs[i, :, :segment.shape[1]] = segment
                
        return epochs

    elif signal_type == 'SPK':
        units = session_data['units']
        return units[units['location'] == area]['spike_times'].values if 'location' in units.columns else units['spike_times'].values
    
    raise ValueError(f"Unsupported signal_type: {signal_type}")

