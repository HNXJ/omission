
import numpy as np
import pandas as pd
import os
import glob
from scipy.signal import hilbert, butter, filtfilt
import plotly.express as px
import plotly.graph_objects as go

# Parameters
DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
CHECKPOINT_DIR = r'D:\Analysis\Omission\local-workspace\checkpoints'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\final_reports\latencies'
os.makedirs(OUTPUT_DIR, exist_ok=True)

SESSIONS = ['230630', '230816', '230830']
SAMPLING_RATE = 1000.0
FS = 1000.0
BASELINE_WIN = (500, 950) # FX window
OMIT_ONSET = 4124
P1_ONSET = 1000

def bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='bandpass')
    return filtfilt(b, a, data, axis=-1)

def get_latency(signal, baseline_mean, baseline_std, expected_onset, threshold=2.0, min_duration=15):
    # signal: (time)
    # Focus on 0-600ms post-onset
    search_win = signal[expected_onset : expected_onset + 600]
    deviation = (search_win - baseline_mean) / (baseline_std + 1e-9)
    
    for i in range(len(deviation) - min_duration):
        if np.all(np.abs(deviation[i:i+min_duration]) > threshold):
            return i # Latency in ms
    return np.nan

def run_comprehensive_latency():
    # Load metadata
    units_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'neuron_categories.csv'))
    vflip_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'vflip2_mapping_v3.csv'))
    
    all_latencies = []
    
    # Process all available sessions in units_df
    SESSIONS_AVAIL = units_df['session'].unique().astype(str)
    
    for sid in SESSIONS_AVAIL:
        print(f"Latency Hierarchy: Session {sid}")
        
        # 1. Spikes
        session_units = units_df[units_df['session'] == int(sid)]
        for p_id in session_units['probe'].unique():
            conds = [('AAAX', OMIT_ONSET), ('AAAB', P1_ONSET), ('BBBA', P1_ONSET), ('RRRR', P1_ONSET)]
            for cond, onset in conds:
                f = os.path.join(DATA_DIR, f'ses{sid}-units-probe{p_id}-spk-{cond}.npy')
                if os.path.exists(f):
                    data = np.load(f, mmap_mode='r')
                    probe_units = session_units[session_units['probe'] == p_id]
                    for _, u_row in probe_units.iterrows():
                        u = int(u_row['unit_idx'])
                        if u >= data.shape[1]: continue
                        
                        psth = np.mean(data[:, u, :], axis=0)
                        psth_smooth = np.convolve(psth, np.ones(30)/30, mode='same')
                        
                        b_mean = np.mean(psth_smooth[BASELINE_WIN[0]:BASELINE_WIN[1]])
                        b_std = np.std(psth_smooth[BASELINE_WIN[0]:BASELINE_WIN[1]])
                        
                        lat = get_latency(psth_smooth, b_mean, b_std, onset)
                        all_latencies.append({
                            'session': sid, 'type': 'Spike', 'id': f"U{u}_P{p_id}",
                            'area': u_row['area'], 'layer': 'unknown', # Layer needs channel mapping
                            'condition': cond, 'latency_ms': lat
                        })

        # 2. LFP (Gamma Band)
        for p_id in [0, 1, 2]:
            crossover = vflip_df[(vflip_df['session_id'] == int(sid)) & (vflip_df['probe_id'] == p_id)]['crossover'].values
            l4 = crossover[0] if len(crossover) > 0 else 64
            area = vflip_df[(vflip_df['session_id'] == int(sid)) & (vflip_df['probe_id'] == p_id)]['area'].values[0] if len(crossover)>0 else 'unknown'
            
            for cond, onset in [('AAAX', OMIT_ONSET), ('AAAB', P1_ONSET)]:
                f = os.path.join(DATA_DIR, f'ses{sid}-probe{p_id}-lfp-{cond}.npy')
                if os.path.exists(f):
                    lfp = np.load(f, mmap_mode='r')
                    for ch in range(128):
                        avg_lfp = np.mean(lfp[:, ch, :], axis=0)
                        gamma = bandpass_filter(avg_lfp, 35, 80, FS)
                        env = np.abs(hilbert(gamma))
                        env_smooth = np.convolve(env, np.ones(30)/30, mode='same')
                        
                        b_mean = np.mean(env_smooth[BASELINE_WIN[0]:BASELINE_WIN[1]])
                        b_std = np.std(env_smooth[BASELINE_WIN[0]:BASELINE_WIN[1]])
                        
                        lat = get_latency(env_smooth, b_mean, b_std, onset)
                        layer = 'Superficial' if ch < l4 else 'Deep'
                        all_latencies.append({
                            'session': sid, 'type': 'LFP_Gamma', 'id': f"Ch{ch}_P{p_id}",
                            'area': area, 'layer': layer, 'condition': cond, 'latency_ms': lat
                        })

    df = pd.DataFrame(all_latencies)
    df.to_csv(os.path.join(CHECKPOINT_DIR, 'surprise_latency_hierarchy_v2.csv'), index=False)
    
    # Visualizations
    valid_df = df[df['latency_ms'].notna()]
    # Aggregate by Area and Type for Omission
    omit_df = valid_df[valid_df['condition'] == 'AAAX']
    
    AREA_ORDER = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
    def clean_area(x):
        for a in AREA_ORDER:
            if a in str(x): return a
        return 'Other'
    omit_df['area_clean'] = omit_df['area'].apply(clean_area)
    
    summary = omit_df.groupby(['type', 'area_clean', 'layer'])['latency_ms'].agg(['mean', 'std', 'count']).reset_index()
    summary = summary[summary['area_clean'].isin(AREA_ORDER)]
    summary['area_clean'] = pd.Categorical(summary['area_clean'], categories=AREA_ORDER, ordered=True)
    summary = summary.sort_values(['type', 'area_clean', 'layer'])

    # Bar Plot: Area Hierarchy
    fig = px.box(omit_df[omit_df['area_clean'].isin(AREA_ORDER)], 
                 x='area_clean', y='latency_ms', color='type', 
                 category_orders={'area_clean': AREA_ORDER},
                 title="Figure 08A: Surprise Latency Hierarchy (Omission AAAX)")
    fig.update_layout(yaxis_title="Latency (ms)", template="plotly_white")
    fig.write_html(os.path.join(OUTPUT_DIR, "FIG_08A_Latency_Boxplots.html"))

    # Layer Plot
    fig_layer = px.box(omit_df[omit_df['area_clean'].isin(AREA_ORDER)], 
                       x='layer', y='latency_ms', facet_col='area_clean', color='type',
                       title="Figure 08B: Laminar Surprise Latency (Omission)")
    fig_layer.write_html(os.path.join(OUTPUT_DIR, "FIG_08B_Laminar_Latencies.html"))
    
    print("Saved FIG_08A and 08B.")

if __name__ == '__main__':
    run_comprehensive_latency()
