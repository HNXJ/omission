import os
import glob
import re
import pandas as pd
from pynwb import NWBHDF5IO
from collections import defaultdict

def extract_nwb_metadata():
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    data = []

    for nwb_path in nwb_files:
        session_id = re.search(r'ses-(\d+)', nwb_path).group(1)
        try:
            with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
                nwbfile = io.read()
                elec_df = nwbfile.electrodes.to_dataframe()
                
                # Group by probe (device)
                if 'device' in elec_df.columns:
                    probe_groups = elec_df.groupby('device')
                else:
                    # Fallback to group by the prefix of the label or some other logic
                    # Usually peak_channel_id // 128
                    elec_df['probe_id'] = elec_df.index // 128
                    probe_groups = elec_df.groupby('probe_id')

                for probe_id, group in probe_groups:
                    # Get unique areas for this probe
                    areas = group['location'].unique()
                    # Clean areas
                    areas = [str(a) for a in areas if pd.notna(a)]
                    area_str = ", ".join(areas)
                    
                    data.append({
                        'Session': session_id,
                        'Probe': probe_id,
                        'Areas': area_str,
                        'Channels': len(group)
                    })
        except Exception as e:
            print(f"Error reading {nwb_path}: {e}")

    df = pd.DataFrame(data)
    df = df.sort_values(['Session', 'Probe'])
    
    # Print as Markdown Table
    print(df.to_markdown(index=False))

if __name__ == "__main__":
    extract_nwb_metadata()
