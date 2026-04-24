import pandas as pd
from pynwb import NWBHDF5IO
from pathlib import Path
import re
import numpy as np
from src.analysis.spiking.putative_classification import compute_waveform_metrics

def extract_units(nwb_path, out_path):
    print(f"Extracting and stabilizing units from {nwb_path}...")
    try:
        with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
            nwb = io.read()
            units_df = nwb.units.to_dataframe()
            
            # Stabilization: Re-calculate waveform metrics if waveform_mean is available
            # This fixes the F041 "full array duration" bug.
            if 'waveform_mean' in units_df.columns:
                print("  Re-calculating waveform metrics...")
                durations = []
                halfwidths = []
                for idx, row in units_df.iterrows():
                    w = row['waveform_mean']
                    # Assuming standard 30kHz for ephys recordings if not specified
                    metrics = compute_waveform_metrics(w, fs=30000.0)
                    durations.append(metrics['duration_us'] / 1000.0) # Store in ms
                    halfwidths.append(metrics['half_width_us'] / 1000.0)
                
                units_df['waveform_duration'] = durations
                units_df['waveform_halfwidth'] = halfwidths

            # Canonical columns for Omission project
            cols = [
                'waveform_duration', 'waveform_halfwidth', 'firing_rate', 
                'presence_ratio', 'snr', 'peak_channel_id'
            ]
            existing_cols = [c for c in cols if c in units_df.columns]
            units_df[existing_cols].to_csv(out_path)
            print(f"Saved units table to {out_path} ({len(units_df)} units)")
    except Exception as e:
        print(f"Failed {nwb_path}: {e}")

if __name__ == "__main__":
    # Use canonical paths
    nwb_dir = Path(r"C:\Users\nejath\My Drive\Workspace\Analysis\NWBData\misc")
    out_dir = Path(r"D:\drive\data\metadata")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Process only relevant sessions
    sessions_to_fix = ["230830", "230630", "230721"] # Example set
    
    for nwb_path in nwb_dir.glob("*.nwb"):
        ses_match = re.search(r"ses-(\d+)", nwb_path.name)
        if ses_match:
            ses_id = ses_match.group(1)
            # Only process if it's the _rec version (final curated spikes)
            if "_rec.nwb" in nwb_path.name:
                out_path = out_dir / f"units_ses-{ses_id}.csv"
                extract_units(str(nwb_path), str(out_path))
