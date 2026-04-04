"""
plot_psth_verification.py: Plots PSTH of top omission units using Plotly with standardized event shading.
"""
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.ndimage import gaussian_filter1d

DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
UNITS_PATH = r'D:\Analysis\Omission\local-workspace\checkpoints\real_omission_units_layered_v3.csv'

# Standardized Event Shading
EVENTS = {
    "fx": (0, 1000, 'rgba(128,128,128,0.08)'),
    "p1": (1000, 1531, 'rgba(128,128,128,0.12)'),
    "d1": (1531, 2031, 'rgba(128,128,128,0.08)'),
    "p2": (2031, 2562, 'rgba(255,0,0,0.12)'),   # Red for RXRR
    "d2": (2562, 3062, 'rgba(128,128,128,0.08)'),
    "p3": (3062, 3593, 'rgba(0,0,255,0.12)'),   # Blue for RRXR
    "d3": (3593, 4093, 'rgba(128,128,128,0.08)'),
    "p4": (4093, 4624, 'rgba(0,128,0,0.12)'),   # Green for RRRX
    "d4": (4624, 5124, 'rgba(128,128,128,0.08)')
}

def main():
    if not os.path.exists(UNITS_PATH):
        print(f"Error: {UNITS_PATH} not found.")
        return

    df = pd.read_csv(UNITS_PATH)
    # Filter for top omission units by omission response factor
    top_units = df.sort_values('r_fix', ascending=False).head(5)
    
    fig = make_subplots(rows=5, cols=1, 
                        subplot_titles=[f"{row['area']} Unit {row['unit_idx']} (Session {row['session_id']}, Cond {row['cond']})" 
                                        for _, row in top_units.iterrows()])
    
    time_axis = np.arange(6000) - 1000
    
    for i, (_, row) in enumerate(top_units.iterrows()):
        fpath = os.path.join(DATA_DIR, f"ses{row['session_id']}-units-probe{row['probe_id']}-spk-{row['cond']}.npy")
        if not os.path.exists(fpath): 
            print(f"Warning: Data file not found for unit: {fpath}")
            continue
        
        spikes = np.load(fpath, mmap_mode='r')
        # Average across trials
        psth = np.mean(spikes[:, int(row['unit_idx']), :], axis=0) * 1000
        psth_smooth = gaussian_filter1d(psth, sigma=15.0)
        
        # Add Shades
        for name, (start, end, color) in EVENTS.items():
            fig.add_vrect(x0=start-1000, x1=end-1000, fillcolor=color, line_width=0, 
                          annotation_text=name, annotation_position="top left",
                          row=i+1, col=1)
        
        # Add PSTH trace
        fig.add_trace(go.Scatter(x=time_axis, y=psth_smooth, mode='lines', 
                                 line=dict(color='black', width=1.5),
                                 name=f"{row['area']} U{row['unit_idx']}"),
                      row=i+1, col=1)
        
        fig.update_xaxes(title_text="Time (ms)", range=[-1000, 5000], row=i+1, col=1)
        fig.update_yaxes(title_text="FR (Hz)", row=i+1, col=1)

    fig.update_layout(height=1200, width=1000, title_text="Top Omission Units: PSTH Verification",
                      showlegend=False, template="plotly_white")
    
    os.makedirs('figures', exist_ok=True)
    fig.write_html(os.path.join('figures', 'FIG_S1_PSTH_Verification_TopUnits.html'))
    print("Verification plot saved to figures/FIG_S1_PSTH_Verification_TopUnits.html")

if __name__ == "__main__":
    main()
