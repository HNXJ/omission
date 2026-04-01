"""
summarize_lfp_pev.py: Aggregates LFP PEV data by area and probe.
Uses data from omission_lfp_pev_v2.npz.
"""
import os
import numpy as np
import pandas as pd

PEV_PATH = r'D:\Analysis\Omission\local-workspace\LFP_Extractions\omission_lfp_pev_v2.npz'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\summary_stats'

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not os.path.exists(PEV_PATH):
        print(f"LFP PEV file not found at {PEV_PATH}. Skipping LFP summary.")
        return

    # Load the PEV data. allow_pickle=True is needed because .npz might contain objects.
    pev_data = np.load(PEV_PATH, allow_pickle=True)
    
    summary_data = []
    for key in pev_data.files:
        # Keys are like '230831_p0', '230720_p1'
        session_id, probe_part = key.split('_', 1)
        probe = probe_part.replace('p', '') # e.g., '0', '1', '2'
        
        try:
            data = pev_data[key] # Shape (Channels, Time)
            # Calculate average PEV over all channels and time points for this probe
            avg_pev = np.mean(data)
            median_pev = np.median(data)
            
            summary_data.append({
                'session_id': session_id,
                'probe_id': probe,
                'avg_PEV': avg_pev,
                'median_PEV': median_pev
            })
        except Exception as e:
            print(f"Error processing key '{key}': {e}")

    df_lfp_summary = pd.DataFrame(summary_data)
    df_lfp_summary.to_csv(os.path.join(OUTPUT_DIR, 'summary_lfp_pev_by_area.csv'), index=False)
    print(f"LFP PEV analysis complete. Saved summary to {OUTPUT_DIR}/summary_lfp_pev_by_area.csv")

if __name__ == "__main__":
    main()
