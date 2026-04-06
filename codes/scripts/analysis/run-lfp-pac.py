
from codes.config.paths import DATA_DIR, FIGURES_DIR, PROCESSED_DATA_DIR

import numpy as np
import pandas as pd
import os
import plotly.express as px
from scipy.signal import hilbert, butter, filtfilt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Parameters
DATA_DIR = str(DATA_DIR)
CHECKPOINT_DIR = str(PROCESSED_DATA_DIR)
OUTPUT_DIR = str(FIGURES_DIR / 'final_reports/lfp')

def main(args=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    SESSIONS = ['230630', '230816', '230830']
    FS = 1000.0
    OMIT_ONSET = 4093 # Gamma-Standard p4 onset
    WIN_SIZE = 531 # 531ms window
    def bandpass_filter(data, lowcut, highcut, fs, order=2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='bandpass')
    return filtfilt(b, a, data, axis=-1)
    def modulation_index(phase, amplitude, n_bins=18):
    # MI = (H_max - H) / H_max
    # H_max = ln(n_bins)
    bins = np.linspace(-np.pi, np.pi, n_bins+1)
    bin_idx = np.digitize(phase, bins) - 1
    mean_amp = []
    for i in range(n_bins):
        mask = bin_idx == i
        if np.any(mask):
            mean_amp.append(np.mean(amplitude[mask]))
        else:
            mean_amp.append(0)
    mean_amp = np.array(mean_amp)
    if np.sum(mean_amp) == 0: return 0
    p = mean_amp / np.sum(mean_amp)
    H = -np.sum(p * np.log(p + 1e-12))
    H_max = np.log(n_bins)
    return (H_max - H) / H_max
    def run_lfp_pac():
    vflip_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'vflip2_mapping_v3.csv'))
    results = []
    for sid in SESSIONS:
        print(f"LFP PAC: Session {sid}")
        session_vflip = vflip_df[vflip_df['session_id'] == int(sid)]
        for p_id in session_vflip['probe_id'].unique():
            area = session_vflip[session_vflip['probe_id'] == p_id]['area'].values[0]
            crossover = session_vflip[session_vflip['probe_id'] == p_id]['crossover'].values[0]
            # Rep channel (Superficial)
            ch = int(crossover - 10) if crossover > 10 else 30
            for cond in ['AAAB', 'AAAX']:
                f = os.path.join(DATA_DIR, f'ses{sid}-probe{p_id}-lfp-{cond}.npy')
                if not os.path.exists(f): continue
                lfp = np.load(f, mmap_mode='r')
                # (trials, ch, time)
                # Omission window
                sig = lfp[:, ch, OMIT_ONSET : OMIT_ONSET + WIN_SIZE]
                all_mi = []
                for t in range(min(50, sig.shape[0])): # Limit trials
                    raw = sig[t, :]
                    theta = bandpass_filter(raw, 4, 8, FS)
                    gamma = bandpass_filter(raw, 35, 70, FS)
                    phase = np.angle(hilbert(theta))
                    amp = np.abs(hilbert(gamma))
                    all_mi.append(modulation_index(phase, amp))
                results.append({
                    'session': sid, 'area': area, 'condition': cond, 'mi': np.mean(all_mi)
                })
    res_df = pd.DataFrame(results)
    res_df.to_csv(os.path.join(CHECKPOINT_DIR, 'lfp_pac_results.csv'), index=False)
    # Plotting
    fig = px.bar(res_df, x='area', y='mi', color='condition', barmode='group',
                 title="Figure 10: Theta-Gamma PAC (Modulation Index) across Areas")
    fig.write_html(os.path.join(OUTPUT_DIR, "FIG_10_PAC_Results.html"))
    run_lfp_pac()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
