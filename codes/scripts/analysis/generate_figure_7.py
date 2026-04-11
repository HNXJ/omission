import numpy as np
import h5py
from pathlib import Path
from scipy.signal import butter, filtfilt, hilbert
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

ARRAY_DIR = Path(r'D:\drive\data\arrays')
OUTPUT_DIR = Path(r'D:\drive\omission\outputs\oglo-figures\figure-7')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CANONICAL_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']

BANDS = {
    'Theta (θ) [4-8 Hz]': (4, 8),
    'Alpha (α) [8-13 Hz]': (8, 13),
    'Beta (β) [13-30 Hz]': (13, 30),
    'Low Gamma (γ1) [30-60 Hz]': (30, 60),
    'High Gamma (γ2) [60-100 Hz]': (60, 100)
}

def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs=1000, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data, axis=-1)
    return y

def get_area_lfp(area, condition, window_idx):
    all_data = []
    for h5_file in ARRAY_DIR.glob('lfp_by_area_*.h5'):
        try:
            with h5py.File(h5_file, 'r') as f:
                for k in f.keys():
                    areas_in_probe = [a.strip() for a in k.split(',')]
                    if area in areas_in_probe:
                        if condition in f[k]:
                            data = f[k][condition][()]
                            n_channels = data.shape[1]
                            n_areas = len(areas_in_probe)
                            ch_per_area = n_channels // n_areas
                            idx_in_probe = areas_in_probe.index(area)
                            ch_start = idx_in_probe * ch_per_area
                            ch_end = ch_start + ch_per_area
                            area_data = data[:, ch_start:ch_end, window_idx[0]:window_idx[1]]
                            all_data.append(area_data.reshape(-1, area_data.shape[2]))
        except Exception as e:
            continue
    if all_data:
        return np.vstack(all_data)
    return np.array([])

def extract_band_envelope(data, lowcut, highcut, fs=1000):
    # Filter
    filtered = bandpass_filter(data, lowcut, highcut, fs)
    # Process in batches to avoid memory issues with Hilbert
    batch_size = 500
    env = np.zeros_like(filtered)
    for i in range(0, filtered.shape[0], batch_size):
        analytic_signal = hilbert(filtered[i:i+batch_size], axis=-1)
        env[i:i+batch_size] = np.abs(analytic_signal)
    return env.mean(axis=0)

def generate_figure_7():
    print("Generating Figure 7: Band-Specific LFP Dynamics")
    
    # Target window: -500ms before p2 to +1000ms after p2 onset
    p2_onset = 2031
    win_start = p2_onset - 500 # 1531
    win_end = p2_onset + 1000  # 3031
    
    times_rel = np.arange(win_end - win_start) - 500
    
    for area in CANONICAL_AREAS:
        print(f"Processing {area}...")
        
        lfp_stim = get_area_lfp(area, 'RRRR', (win_start, win_end))
        lfp_omit = get_area_lfp(area, 'RXRR', (win_start, win_end))
        
        if lfp_stim.size == 0 or lfp_omit.size == 0:
            print(f"Skipping {area}, not enough data.")
            continue
            
        fig = make_subplots(rows=len(BANDS), cols=1, shared_xaxes=True,
                            subplot_titles=list(BANDS.keys()),
                            vertical_spacing=0.04)
        
        for idx, (band_name, (low, high)) in enumerate(BANDS.items(), start=1):
            env_stim = extract_band_envelope(lfp_stim, low, high)
            env_omit = extract_band_envelope(lfp_omit, low, high)
            
            fig.add_trace(go.Scatter(x=times_rel, y=env_stim, name=f"Stimulus (RRRR)", line=dict(color='royalblue', width=2), legendgroup="Stimulus", showlegend=(idx==1)), row=idx, col=1)
            fig.add_trace(go.Scatter(x=times_rel, y=env_omit, name=f"Omission (RXRR)", line=dict(color='crimson', width=2, dash='dash'), legendgroup="Omission", showlegend=(idx==1)), row=idx, col=1)
            
            # Mark p2 onset and offset
            fig.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.5, row=idx, col=1)
            fig.add_vline(x=531, line_dash="dash", line_color="black", opacity=0.5, row=idx, col=1)
            
            # Shaded region for expected stimulus
            fig.add_vrect(x0=0, x1=531, fillcolor="gold", opacity=0.1, layer="below", line_width=0, row=idx, col=1)
            
            fig.update_yaxes(title_text="Amplitude (uV)", row=idx, col=1)
            
        fig.update_xaxes(title_text="Time relative to p2 onset (ms)", row=len(BANDS), col=1)
        
        fig.update_layout(
            title=f"Figure 7: Band-Specific LFP Dynamics ({area})<br><i>Cross-frequency coordination during the predictive window</i>",
            height=1200, width=1000,
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        out_path = OUTPUT_DIR / f'figure_7_bands_{area}.html'
        fig.write_html(out_path)
        print(f"Saved {out_path}")

if __name__ == "__main__":
    generate_figure_7()
