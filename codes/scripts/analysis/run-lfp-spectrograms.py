
from codes.config.paths import DATA_DIR, FIGURES_DIR, PROCESSED_DATA_DIR

import numpy as np
import pandas as pd
import os
from scipy.signal import spectrogram
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 🏺 Madelane Golden Dark Palette
GOLD = "#CFB87C"
BLACK = "#000000"
VIOLET = "#8F00FF"
SLATE = "#444444"

# Parameters
DATA_DIR = str(DATA_DIR)
CHECKPOINT_DIR = str(PROCESSED_DATA_DIR)
OUTPUT_DIR = str(FIGURES_DIR / 'part01')

def main(args=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    SESSIONS = ['230630', '230816', '230830']
    FS = 1000.0
    CONDITIONS = ['AAAB', 'AAAX'] # Standard vs Omission
    EVENT_LINES = {
    'fx': -500, 'p1': 0, 'd1': 531, 'p2': 1031, 'd2': 1562, 
    'p3': 2062, 'd3': 2593, 'p4': 3093, 'd4': 3624
    }
    def plot_spectrogram_suite():
    # Use mapping from data/checkpoints
    vflip_path = os.path.join(CHECKPOINT_DIR, 'enhanced_neuron_categories.csv')
    if not os.path.exists(vflip_path):
        print(f"Error: {vflip_path} not found.")
        return
    vflip_df = pd.read_csv(vflip_path)
    for sid in SESSIONS:
        print(f"🏺 TFR Analysis: Session {sid}")
        session_data = vflip_df[vflip_df['session_id'].astype(str).str.contains(sid)]
        if session_data.empty: continue
        for p_id in session_data['probe_id'].unique():
            probe_meta = session_data[session_data['probe_id'] == p_id].iloc[0]
            area = probe_meta['area']
            # Use representative channels (or just pick middle if crossover unknown)
            # For now, let's use channels 40 and 80 as sup/deep proxies if not in CSV
            ch_sup, ch_deep = 40, 80 
            fig = make_subplots(rows=2, cols=2, 
                                subplot_titles=(f"Sup (Ch{ch_sup}) - Standard", f"Sup (Ch{ch_sup}) - Omission",
                                               f"Deep (Ch{ch_deep}) - Standard", f"Deep (Ch{ch_deep}) - Omission"),
                                vertical_spacing=0.1, horizontal_spacing=0.1)
            for col_idx, cond in enumerate(CONDITIONS):
                fname = f'ses{sid}-probe{p_id}-lfp-{cond}.npy'
                f_path = os.path.join(DATA_DIR, fname)
                if not os.path.exists(f_path):
                    # Try local-workspace/data/
                    f_path = os.path.join(str(DATA_DIR), fname)
                    if not os.path.exists(f_path):
                        print(f"  Warning: {fname} missing.")
                        continue
                lfp = np.load(f_path, mmap_mode='r') # (trials, 128, time)
                for row_idx, ch in enumerate([ch_sup, ch_deep]):
                    # Trial-averaged spectrogram
                    # User Mandate: Hanning window, 98% overlap, 1-150Hz
                    nperseg = 256
                    noverlap = int(0.98 * nperseg)
                    trial_specs = []
                    # Average over trials (cap at 50 for speed/stability)
                    n_trials = min(50, lfp.shape[0])
                    for t_idx in range(n_trials):
                        f_vec, t_vec, Sxx = spectrogram(lfp[t_idx, ch, :], fs=FS, 
                                                        window='hann', 
                                                        nperseg=nperseg, 
                                                        noverlap=noverlap)
                        trial_specs.append(Sxx)
                    avg_spec = np.mean(trial_specs, axis=0)
                    # Mandate: Safety - check for NaN/0
                    if np.all(np.isnan(avg_spec)) or np.all(avg_spec == 0):
                        print(f"  ! Safety Violation: Plot {sid}_P{p_id}_{ch}_{cond} is empty.")
                        continue
                    log_spec = 10 * np.log10(avg_spec + 1e-12)
                    # Convert t_vec to ms (relative to P1 onset at Sample 1000)
                    t_ms = (t_vec * 1000.0) - 1000.0
                    fig.add_trace(go.Heatmap(
                        z=log_spec, x=t_ms, y=f_vec,
                        coloraxis="coloraxis",
                        zmin=-30, zmax=5,
                        hovertemplate="Time: %{x}ms<br>Freq: %{y}Hz<br>Power: %{z}dB<extra></extra>"
                    ), row=row_idx+1, col=col_idx+1)
                    # Add event lines
                    for label, t_event in EVENT_LINES.items():
                        fig.add_vline(x=t_event, line_dash="dash", 
                                      line_color="rgba(255,255,255,0.4)", 
                                      line_width=1, row=row_idx+1, col=col_idx+1)
            fig.update_layout(
                title=dict(
                    text=f"🏺 LFP TFR SUITE | {area} (Session {sid}, Probe {p_id})",
                    font=dict(color=GOLD, size=20)
                ),
                xaxis_title="Time (ms)", yaxis_title="Frequency (Hz)",
                coloraxis=dict(colorscale='Viridis', colorbar=dict(title="dB")),
                height=1000, width=1200,
                paper_bgcolor=BLACK, plot_bgcolor=BLACK,
                font=dict(color=GOLD, family="Consolas"),
                template="plotly_dark"
            )
            # Mandate: Frequency range 1-150Hz
            fig.update_yaxes(range=[1, 150])
            fig.update_xaxes(range=[-500, 4200]) # Window of interest
            out_file = os.path.join(OUTPUT_DIR, f"FIG_09_TFR_{sid}_{area}_{p_id}.html")
            fig.write_html(out_file)
            print(f"  - Saved: {out_file}")
    plot_spectrogram_suite()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
