import numpy as np
import h5py
from pathlib import Path
from scipy.signal import spectrogram
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

ARRAY_DIR = Path(r'D:\drive\data\arrays')
OUTPUT_DIR = Path(r'D:\drive\omission\outputs\oglo-figures\figure-6')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CANONICAL_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']

def get_area_lfp_chunked(area, condition, window_idx):
    for h5_file in ARRAY_DIR.glob('lfp_by_area_*.h5'):
        with h5py.File(h5_file, 'r', libver='latest', swmr=True) as f:
            for k in f.keys():
                areas = [a.strip() for a in k.split(',')]
                if area in areas:
                    if condition in f[k]:
                        data = f[k][condition]
                        idx = areas.index(area)
                        ch_per = data.shape[1] // len(areas)
                        for t in range(data.shape[0]):
                            yield data[t, idx*ch_per:(idx+1)*ch_per, window_idx[0]:window_idx[1]]

def generate_figure_6_v8():
    p2_onset = 2031
    win_start, win_end = p2_onset - 500, p2_onset + 1000
    fx_start, fx_end = 500, 1000
    
    for area in CANONICAL_AREAS:
        logging.info(f"Computing TFR for {area}...")
        
        # 1. Baseline
        base_powers = []
        for chunk in get_area_lfp_chunked(area, 'RRRR', (fx_start, fx_end)):
            # chunk shape (channels, time)
            f, _, Sxx = spectrogram(chunk, fs=1000, nperseg=64, noverlap=32, nfft=128)
            # Sxx is (channels, freqs, segments)
            base_powers.append(np.mean(Sxx, axis=(0, 2)))
        
        if not base_powers: continue
        base_power = np.array(base_powers).mean(axis=0) # (freqs,)
        
        # 2. Stim vs Omit (samples)
        stim_p_acc, omit_p_acc = [], []
        
        # Get chunks
        for i, (s_chunk, o_chunk) in enumerate(zip(get_area_lfp_chunked(area, 'RRRR', (win_start, win_end)),
                                                   get_area_lfp_chunked(area, 'RXRR', (win_start, win_end)))):
            if i > 20: break 
            f, t, S_stim = spectrogram(s_chunk, fs=1000, nperseg=64, noverlap=32, nfft=128)
            _, _, S_omit = spectrogram(o_chunk, fs=1000, nperseg=64, noverlap=32, nfft=128)
            # Average over channels (axis 0)
            stim_p_acc.append(np.mean(S_stim, axis=0)) # (freqs, segments)
            omit_p_acc.append(np.mean(S_omit, axis=0))
        
        stim_p = np.mean(stim_p_acc, axis=0) # (freqs, segments)
        omit_p = np.mean(omit_p_acc, axis=0)
        
        # 3. dB Transform
        db_stim = 10 * np.log10(np.maximum(stim_p, 1e-10) / np.maximum(base_power[:, np.newaxis], 1e-10))
        db_omit = 10 * np.log10(np.maximum(omit_p, 1e-10) / np.maximum(base_power[:, np.newaxis], 1e-10))
        
        # 4. Plotting
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, subplot_titles=(f"Stim", f"Omit", f"Diff"))
        fig.add_trace(go.Heatmap(x=t*1000, y=f, z=db_stim, colorscale='RdBu_r'), row=1, col=1)
        fig.add_trace(go.Heatmap(x=t*1000, y=f, z=db_omit, colorscale='RdBu_r'), row=2, col=1)
        fig.add_trace(go.Heatmap(x=t*1000, y=f, z=db_omit-db_stim, colorscale='PRGn'), row=3, col=1)
        fig.update_layout(title=f'Figure 6: {area} | Analysis script: github.com/HNXJ/omission/blob/main/codes/scripts/analysis/generate_figure_6.py')
        fig.write_html(OUTPUT_DIR / f'figure_6_{area}.html')
        logging.info(f"Saved figure for {area}")

if __name__ == "__main__":
    generate_figure_6_v8()
