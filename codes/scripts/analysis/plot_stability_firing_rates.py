"""
Script: plot_stability_firing_rates.py
Plots average firing rates (Hz) for presence ratio bins (e.g., 0-0.5, 0.5-0.75, ..., 1.0)
for the RRRR condition across the sequence (fx, p1-p4, d1-d4).
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from scipy.ndimage import gaussian_filter1d

# Paths
ARRAY_DIR = Path('data/arrays')
META_PATH = Path('outputs/unit_nwb_profile.csv')
OUTPUT_DIR = Path('outputs/stability-analysis')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define Presence Ratio Bins
# <0.5, 0.5-0.75, 0.75-0.9, 0.9-0.95, 0.95-0.98, 0.98-0.99, 0.99-1.0, 1.0
BINS = [0.0, 0.5, 0.75, 0.9, 0.95, 0.98, 0.99, 1.0]
BIN_LABELS = ['<0.5', '0.5-0.75', '0.75-0.9', '0.9-0.95', '0.95-0.98', '0.98-0.99', '0.99-1.0', '1.0']

def get_bin(val):
    for i, b in enumerate(BINS[1:]):
        if val <= b:
            return BIN_LABELS[i]
    return BIN_LABELS[-1]

def main():
    print("Loading metadata...")
    df = pd.read_csv(META_PATH)
    
    # Assign bins
    df['presence_bin'] = df['presence_ratio'].apply(get_bin)
    
    # Load RRRR data to calculate average firing rate over the full window
    # We aggregate firing rates by session and bin
    print("Aggregating firing rates (RRRR)...")
    
    fig = go.Figure()
    
    for bin_label in BIN_LABELS:
        bin_df = df[df['presence_bin'] == bin_label]
        if len(bin_df) == 0: continue
        
        # We need a representative trace for this group. 
        # Using a simple mean across all units in this bin.
        # Note: This loads all units, which might be memory intensive.
        # Optimization: Aggregate by session-probe-unit indices.
        
        # Logic: for each unit, load RRRR array, take mean, average across units in bin.
        all_traces = []
        for _, row in bin_df.iterrows():
            # session_nwb: sub-C31o_ses-230630_rec.nwb
            # extract 230630
            raw_sess = row['session_nwb']
            sess = raw_sess.split('_')[1].split('-')[1]
            
            # Map probe name to index: probeA -> 0, probeB -> 1, probeC -> 2
            probe_map = {'probeA': 0, 'probeB': 1, 'probeC': 2}
            probe_raw = row['probe']
            probe = probe_map.get(probe_raw, 0) # Fallback to 0
            u_idx = row['unit_id_in_session']
            
            # Construct path (e.g., ses230630-units-probe0-spk-RRRR.npy)
            path = ARRAY_DIR / f"ses{sess}-units-probe{probe}-spk-RRRR.npy"
            if path.exists():
                try:
                    arr = np.load(path)
                    if u_idx < arr.shape[1]:
                        # Average trials
                        trace = arr[:, u_idx, :].mean(axis=0) * 1000
                        all_traces.append(trace)
                except: continue
        
        if all_traces:
            mean_trace = np.mean(all_traces, axis=0)
            fig.add_trace(go.Scatter(
                x=np.arange(-1000, 5000), 
                y=gaussian_filter1d(mean_trace, 50),
                name=bin_label
            ))
            
    fig.update_layout(
        title="Mean Firing Rate Trace by Presence Ratio (RRRR)",
        xaxis_title="Time from P1 (ms)",
        yaxis_title="Firing Rate (Hz)",
        template="plotly_white"
    )
    
    fig.write_image(OUTPUT_DIR / 'firing_rate_stability_trace.svg')
    fig.write_html(OUTPUT_DIR / 'firing_rate_stability_trace.html')
    print("Done. Saved to", OUTPUT_DIR)

if __name__ == "__main__":
    main()
