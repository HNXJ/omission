import pandas as pd
from pynwb import NWBHDF5IO
from pathlib import Path
import re

def extract_units(nwb_path, out_path):
    print(f"Extracting units from {nwb_path}...")
    try:
        with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
            nwb = io.read()
            units_df = nwb.units.to_dataframe()
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
    nwb_dir = Path(r"C:\Users\nejath\My Drive\Workspace\Analysis\NWBData\misc")
    out_dir = Path(r"D:\drive\data\metadata")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for nwb_path in nwb_dir.glob("*.nwb"):
        # Skip the massive raw ones if they have a _rec version
        if "rec" not in nwb_path.name and (nwb_dir / nwb_path.name.replace(".nwb", "_rec.nwb")).exists():
            print(f"Skipping {nwb_path.name} in favor of _rec version")
            continue
            
        ses_match = re.search(r"ses-(\d+)", nwb_path.name)
        if ses_match:
            ses_id = ses_match.group(1)
            out_path = out_dir / f"units_ses-{ses_id}.csv"
            extract_units(str(nwb_path), str(out_path))
