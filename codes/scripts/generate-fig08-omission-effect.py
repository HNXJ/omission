"""
generate_fig08_omission_effect.py
OMISSION 2026: Individual Neuron Omission Contrast - V4 Refined
"""
import os
import glob
import json
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind
import plotly.graph_objects as go
from pathlib import Path

DATA_DIR = r'D:\Analysis\Omission\local-workspace\data\arrays'
OUTPUT_DIR = Path(__file__).parents[2] / "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Windows: P1 (1000-1531), P2 (2031-2562), P3 (3062-3593), P4 (4093-4624)
# Sampling rate is assumed 1000Hz (1ms/bin)
EPOCH_WINDOWS = {
    'p1': (1000, 1531),
    'p2': (2031, 2562),
    'p3': (3062, 3593),
    'p4': (4093, 4624),
}

# Mapping for matched stimulus baseline across conditions
# Format: (Omission_Condition, Omission_Pos) -> (Baseline_Condition, Baseline_Pos)
# We want to compare the stimulus AFTER the omission to its "standard" appearance.
# Omission at 2 (AXAB) -> Recovery at 3 ('A'). Baseline: AAAB p1 ('A')
# Omission at 3 (AAXB) -> Recovery at 4 ('B'). Baseline: BBBA p1 ('B') or AAAB p4 ('B')
COMPARISONS = [
    # Omission at 2
    {'om_cond': 'AXAB', 'om_pos': 'p3', 'base_cond': 'AAAB', 'base_pos': 'p1', 'label': 'A_after_X_vs_A_baseline'},
    {'om_cond': 'BXBA', 'om_pos': 'p3', 'base_cond': 'BBBA', 'base_pos': 'p1', 'label': 'B_after_X_vs_B_baseline'},
    {'om_cond': 'RXRR', 'om_pos': 'p3', 'base_cond': 'RRRR', 'base_pos': 'p1', 'label': 'R_after_X_vs_R_baseline'},
    # Omission at 3
    {'om_cond': 'AAXB', 'om_pos': 'p4', 'base_cond': 'AAAB', 'base_pos': 'p4', 'label': 'B_after_X_vs_B_baseline'},
    {'om_cond': 'BBXA', 'om_pos': 'p4', 'base_cond': 'BBBA', 'base_pos': 'p4', 'label': 'A_after_X_vs_A_baseline'},
    {'om_cond': 'RRXR', 'om_pos': 'p4', 'base_cond': 'RRRR', 'base_pos': 'p4', 'label': 'R_after_X_vs_R_baseline'},
]

def get_spike_counts(session_id, probe_id, condition, window_key):
    f_pattern = f'ses{session_id}-units-probe{probe_id}-spk-{condition}.npy'
    f_paths = glob.glob(os.path.join(DATA_DIR, f_pattern))
    if not f_paths: return None
    try:
        spikes = np.load(f_paths[0], mmap_mode='r')
        win_start, win_end = EPOCH_WINDOWS[window_key]
        # Sum spikes in the window: [trials, units, time] -> [trials, units]
        counts = np.nansum(spikes[:, :, win_start:win_end], axis=2)
        return np.nan_to_num(counts)
    except Exception:
        return None

def run():
    print("Generating Figure 08: Omission Effect (Individual Neurons)...")
    
    # Identify all available session-probe pairs
    spike_files = glob.glob(os.path.join(DATA_DIR, 'ses*-units-probe*-spk-*.npy'))
    sessions_probes = sorted(list(set([(f.split('ses')[1].split('-')[0], f.split('probe')[1].split('-')[0]) for f in spike_files])))

    for comp in COMPARISONS:
        label = comp['label']
        om_cond = comp['om_cond']
        base_cond = comp['base_cond']
        print(f"Processing contrast: {om_cond}({comp['om_pos']}) vs {base_cond}({comp['base_pos']})")
        
        all_unit_stats = []
        for ses, prb in sessions_probes:
            fr_om = get_spike_counts(ses, prb, om_cond, comp['om_pos'])
            fr_base = get_spike_counts(ses, prb, base_cond, comp['base_pos'])
            
            if fr_om is None or fr_base is None:
                continue
            
            # Ensure same number of units
            n_units = min(fr_om.shape[1], fr_base.shape[1])
            for u in range(n_units):
                vals_om = fr_om[:, u]
                vals_base = fr_base[:, u]
                
                # Check for zero variance
                if np.std(vals_om) == 0 and np.std(vals_base) == 0:
                    t, p = 0.0, 1.0
                else:
                    t, p = ttest_ind(vals_om, vals_base, equal_var=False)
                
                delta = np.mean(vals_om) - np.mean(vals_base)
                all_unit_stats.append({
                    'session': ses, 'probe': prb, 'unit': u,
                    'delta': delta, 'p_val': np.nan_to_num(p, nan=1.0)
                })

        if not all_unit_stats:
            print(f"No data for {label}. Skipping.")
            continue
            
        df = pd.DataFrame(all_unit_stats)
        
        # Identify significant cohorts (p < 0.01)
        sig_inc = df[(df['p_val'] < 0.01) & (df['delta'] > 0)]
        sig_dec = df[(df['p_val'] < 0.01) & (df['delta'] < 0)]
        
        # Plotting
        fig = go.Figure()
        
        # All neurons
        fig.add_trace(go.Histogram(
            x=df['delta'], 
            name='All Units', 
            marker_color='gray', 
            opacity=0.3,
            nbinsx=50
        ))
        
        # Significant Increased (Surprise)
        fig.add_trace(go.Histogram(
            x=sig_inc['delta'], 
            name=f'Sig Increased (N={len(sig_inc)})', 
            marker_color='#8F00FF', # Electric Violet
            nbinsx=50
        ))
        
        # Significant Decreased (Gain-Reset)
        fig.add_trace(go.Histogram(
            x=sig_dec['delta'], 
            name=f'Sig Decreased (N={len(sig_dec)})', 
            marker_color='#CFB87C', # Vanderbilt Gold
            nbinsx=50
        ))
        
        fig.update_layout(
            title=f"<b>Fig 08: Omission Effect - {label}</b><br><sup>{om_cond} vs {base_cond} | p < 0.01</sup>",
            xaxis_title="Delta Firing Rate (Spikes/Trial)",
            yaxis_title="Neuron Count",
            template="plotly_white",
            barmode='overlay',
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
        )
        
        # Triple Export
        base_path = os.path.join(OUTPUT_DIR, f'fig_08_omission_effect_{label}_{om_cond}_vs_{base_cond}')
        fig.write_html(base_path + '.html')
        fig.write_image(base_path + '.svg')
        fig.write_image(base_path + '.png')
        
        # Metadata
        metadata = {
            "contrast_label": label,
            "omission_condition": om_cond,
            "baseline_condition": base_cond,
            "total_units": len(df),
            "sig_increased_surprise": len(sig_inc),
            "sig_decreased_gain_reset": len(sig_dec),
            "alpha": 0.01,
            "theme": "plotly_white"
        }
        with open(base_path + '.metadata.json', 'w') as f:
            json.dump(metadata, f, indent=4)

if __name__ == '__main__':
    run()
