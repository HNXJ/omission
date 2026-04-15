import numpy as np
import h5py
from pathlib import Path
from scipy.signal import butter, filtfilt, hilbert
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

ARRAY_DIR = Path(r'D:\drive\data\arrays')
OUTPUT_DIR = Path(r'D:\drive\omission\outputs\oglo-figures\figure-7')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CANONICAL_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']

BANDS = {
    'Theta (4-8 Hz)': (4, 8),
    'Alpha (8-13 Hz)': (8, 13),
    'Beta (13-30 Hz)': (13, 30),
    'Low Gamma (30-60 Hz)': (30, 60),
    'High Gamma (60-100 Hz)': (60, 100)
}

def get_area_lfp_chunked(area, condition, window_idx):
    """Memory-efficient generator for LFP data."""
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

def butter_bandpass_filter(data, lowcut, highcut, fs=1000, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data, axis=-1)

def generate_figure_7_optimized():
    p2_onset = 2031
    win_start, win_end = p2_onset - 500, p2_onset + 1000
    times_rel = np.arange(win_end - win_start) - 500
    
    for area in CANONICAL_AREAS:
        logging.info(f"Computing Band Dynamics for {area}...")
        
        # Prepare band-specific accumulators (list of arrays)
        band_envelopes_stim = {band: [] for band in BANDS}
        band_envelopes_omit = {band: [] for band in BANDS}
        
        # Process chunks
        for s_chunk, o_chunk in zip(get_area_lfp_chunked(area, 'RRRR', (win_start, win_end)),
                                    get_area_lfp_chunked(area, 'RXRR', (win_start, win_end))):
            for band, (low, high) in BANDS.items():
                # Filter and Hilbert
                f_stim = butter_bandpass_filter(s_chunk, low, high)
                f_omit = butter_bandpass_filter(o_chunk, low, high)
                
                # Envelope: (channels, time)
                env_s = np.abs(hilbert(f_stim, axis=-1))
                env_o = np.abs(hilbert(f_omit, axis=-1))
                
                # Average over channels
                band_envelopes_stim[band].append(np.mean(env_s, axis=0))
                band_envelopes_omit[band].append(np.mean(env_o, axis=0))
        
        # Aggregate
        fig = make_subplots(rows=len(BANDS), cols=1, shared_xaxes=True,
                            subplot_titles=list(BANDS.keys()), vertical_spacing=0.04)
        
        for idx, (band, _) in enumerate(BANDS.items(), start=1):
            if not band_envelopes_stim[band]: continue
            
            mean_s = np.mean(band_envelopes_stim[band], axis=0)
            mean_o = np.mean(band_envelopes_omit[band], axis=0)
            
            fig.add_trace(go.Scatter(x=times_rel, y=mean_s, name="Stim", line=dict(color='royalblue', width=2), legendgroup="Stim", showlegend=(idx==1)), row=idx, col=1)
            fig.add_trace(go.Scatter(x=times_rel, y=mean_o, name="Omit", line=dict(color='crimson', width=2, dash='dash'), legendgroup="Omit", showlegend=(idx==1)), row=idx, col=1)
            
            fig.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.3, row=idx, col=1)
            fig.add_vline(x=531, line_dash="dash", line_color="black", opacity=0.3, row=idx, col=1)
            fig.update_yaxes(title_text="uV", row=idx, col=1)

        fig.update_layout(title=f'Figure 7: {area} | Analysis script: github.com/HNXJ/omission/blob/main/codes/scripts/analysis/generate_figure_7.py', 
                          height=1200, width=1000, template="plotly_white")
        fig.write_html(OUTPUT_DIR / f'figure_7_{area}.html')
        logging.info(f"Saved figure for {area}")

if __name__ == "__main__":
    generate_figure_7_optimized()
