import numpy as np
from pathlib import Path
from scipy.signal import butter, filtfilt, hilbert
import plotly.graph_objects as go
from codes.functions.lfp.lfp_pipeline import get_signal_conditional

OUTPUT_DIR = Path(r'D:\drive\omission\outputs\oglo-figures\figure-6')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
NWB_DIR = Path(r'D:\analysis\nwb')

CANONICAL_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
BANDS = {'Theta': (4, 8), 'Alpha': (8, 12), 'Beta': (15, 30), 'Gamma': (30, 80)}
BAND_COLORS = {'Theta': '#00FFFF', 'Alpha': '#00FF00', 'Beta': '#D2B48C', 'Gamma': '#8A2BE2'}
WINDOW = (-1.0, 4.0)
FS = 1000

def butter_bandpass_filter(data, lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    # Filter along time axis (last dimension)
    return filtfilt(b, a, data, axis=-1)

def compute_band_power(epochs, fs=FS):
    # epochs: (trials, channels, time)
    if epochs.size == 0 or np.all(np.isnan(epochs)):
        return None
    powers = {}
    for band, (low, high) in BANDS.items():
        filtered = butter_bandpass_filter(epochs, low, high, fs)
        analytic = hilbert(filtered, axis=-1)
        power = np.abs(analytic)**2
        # Average over trials and channels
        powers[band] = np.nanmean(np.nanmean(power, axis=0), axis=0)
    return powers

def generate_figure_6(session_file=None):
    if session_file is None:
        session_file = NWB_DIR / 'sub-V198o_ses-230629_rec.nwb'
    
    print(f"Generating Figure 6 for session: {session_file.name}")
    time_vec = np.linspace(WINDOW[0]*1000, WINDOW[1]*1000, int((WINDOW[1]-WINDOW[0])*FS))
    
    for area in CANONICAL_AREAS:
        try:
            epochs = get_signal_conditional(session_file, area, signal_type='LFP', epoch_window=WINDOW)
            band_powers = compute_band_power(epochs)
            if band_powers is None:
                print(f"[infile] generate_figure_6.py [doing] Skipping {session_file.name} area {area}: No valid data.")
                continue
            mean_total = np.nanmean([p for p in band_powers.values()], axis=0)
            
            fig = go.Figure()
            for band, power in band_powers.items():
                rel_power = 10 * np.log10(np.maximum(power, 1e-6) / np.maximum(mean_total, 1e-6))
                fig.add_trace(go.Scatter(x=time_vec, y=rel_power, name=band, line=dict(color=BAND_COLORS[band], width=2)))
            
            fig.update_layout(
                title=f"Omission Power (dB) | {area} (Aligned to P1)",
                plot_bgcolor='#0B0C10', paper_bgcolor='#0B0C10',
                font=dict(color='#C5C6C7'),
                xaxis=dict(title='Time (ms)', gridcolor='#1F2833'), 
                yaxis=dict(title='Rel. Power (dB)', gridcolor='#1F2833'),
                shapes=[dict(type='line', x0=0, x1=0, y0=-5, y1=5, line=dict(color='White', dash='dash'))]
            )
            fig.write_html(OUTPUT_DIR / f'figure_6_{session_file.stem}_{area}.html')
            print(f"[infile] generate_figure_6.py [doing] Saved plot for {area}")
        except Exception as e:
            print(f"Error processing {area}: {e}")

if __name__ == "__main__":
    generate_figure_6()
