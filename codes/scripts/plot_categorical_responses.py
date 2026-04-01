
import numpy as np
import pandas as pd
import glob
import os
import plotly.graph_objects as go
from scipy.signal.windows import gaussian
import re

TARGET_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
CAT_COLORS = {
    'Stim+': 'red',
    'Stim-': 'blue',
    'Omit': 'green',
    'Fix': 'purple',
    'Null': 'gray'
}

def plot_categories():
    # Load classifications
    cat_df = pd.read_csv('checkpoints/neuron_categories.csv')
    
    kernel = gaussian(100, 20)
    kernel /= np.sum(kernel)
    
    # Area -> Category -> List of Smoothed Mean Traces
    area_cat_traces = {area: {cat: [] for cat in CAT_COLORS} for area in TARGET_AREAS}

    # Group by session to minimize file loading
    for session_id, s_df in cat_df.groupby('session'):
        print(f"Aggregating traces for session {session_id}...")
        
        # We use AAAX to show omission response clearly
        spk_files = glob.glob(f'data/ses{session_id}-units-probe*-spk-AAAX.npy')
        cond_data = {}
        for f in spk_files:
            p_id = int(re.search(r'probe(\d+)', f).group(1))
            cond_data[p_id] = np.load(f, mmap_mode='r')

        for _, row in s_df.iterrows():
            p_id, u_idx, area, cat = row['probe'], row['unit_idx'], row['area'], row['category']
            if p_id in cond_data and area in TARGET_AREAS:
                # Mean across trials for this unit
                unit_mean = np.mean(cond_data[p_id][:, u_idx, :], axis=0) * 1000
                smoothed = np.convolve(unit_mean, kernel, mode='same')
                area_cat_traces[area][cat].append(smoothed)

    time_axis = np.linspace(-1000, 5000, 6000)
    os.makedirs('figures/final_reports', exist_ok=True)

    for area in TARGET_AREAS:
        fig = go.Figure()
        
        # Event shades
        fig.add_vrect(x0=3093, x1=3624, fillcolor='rgba(0,0,0,0.05)', line_width=0, annotation_text="p4 (Omit)")

        for cat, color in CAT_COLORS.items():
            traces = area_cat_traces[area][cat]
            if not traces: continue
            
            # Grand average for the category in this area
            grand_avg = np.mean(traces, axis=0)
            fig.add_trace(go.Scatter(x=time_axis, y=grand_avg, mode='lines', line=dict(color=color), name=f"{cat} (n={len(traces)})"))

        fig.update_layout(title=f"Categorical Neuron Responses: {area} (Condition: AAAX)",
                          xaxis_title="Time (ms)", yaxis_title="Firing Rate (Hz)",
                          xaxis_range=[-750, 4124], template="plotly_white")
        
        fig.write_html(f"figures/final_reports/{area}_categorical_responses.html")
        try: fig.write_image(f"figures/final_reports/{area}_categorical_responses.svg")
        except: pass
        print(f"Saved categorical plots for {area}.")

if __name__ == '__main__':
    plot_categories()
