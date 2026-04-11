import numpy as np
import h5py
from pathlib import Path
from scipy.signal import spectrogram
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

ARRAY_DIR = Path(r'D:\drive\data\arrays')
OUTPUT_DIR = Path(r'D:\drive\omission\outputs\oglo-figures\figure-6')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CANONICAL_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']

def get_area_lfp(area, condition, window_idx):
    """
    Extracts LFP data for a specific area and condition across all sessions.
    window_idx: tuple of (start_idx, end_idx)
    Returns: shape (N_total_trials * N_channels, Time)
    """
    all_data = []
    
    for h5_file in ARRAY_DIR.glob('lfp_by_area_*.h5'):
        try:
            with h5py.File(h5_file, 'r') as f:
                for k in f.keys():
                    # Parse area strings like 'V1,V2' or 'V3d, V3a'
                    areas_in_probe = [a.strip() for a in k.split(',')]
                    
                    if area in areas_in_probe:
                        if condition in f[k]:
                            data = f[k][condition][()] # (trials, channels, time)
                            
                            # Channel selection (rough split if multiple areas on probe)
                            n_channels = data.shape[1]
                            n_areas = len(areas_in_probe)
                            ch_per_area = n_channels // n_areas
                            idx_in_probe = areas_in_probe.index(area)
                            ch_start = idx_in_probe * ch_per_area
                            ch_end = ch_start + ch_per_area
                            
                            # Flatten trials and selected channels
                            area_data = data[:, ch_start:ch_end, window_idx[0]:window_idx[1]]
                            all_data.append(area_data.reshape(-1, area_data.shape[2]))
        except Exception as e:
            print(f"Error reading {h5_file}: {e}")
            continue
            
    if all_data:
        return np.vstack(all_data)
    return np.array([])

def compute_tfr(lfp_data, fs=1000):
    """
    Computes Time-Frequency Representation (Spectrogram) for LFP data.
    lfp_data: shape (N_signals, Time)
    Returns: freqs, times, mean_power (freqs x times)
    """
    # Parameters for 1000 Hz data
    nperseg = 128
    noverlap = 112
    nfft = 512
    
    powers = []
    
    # Process in batches to save memory
    batch_size = 100
    for i in range(0, lfp_data.shape[0], batch_size):
        batch = lfp_data[i:i+batch_size]
        f, t, Sxx = spectrogram(batch, fs=fs, nperseg=nperseg, noverlap=noverlap, nfft=nfft, axis=1)
        powers.append(Sxx.mean(axis=0)) # Mean over signals in batch
        
    mean_power = np.mean(powers, axis=0) # (freqs, times)
    
    # Filter frequencies 1-100 Hz
    freq_mask = (f >= 1) & (f <= 100)
    
    return f[freq_mask], t * 1000, mean_power[freq_mask, :]

def generate_figure_6():
    print("Generating Figure 6: Time-Frequency Spectrograms")
    
    # We want to analyze the omission in p2 of RXRR vs presence in p2 of RRRR
    # Baseline for normalization: fx (500:1000)
    # Target window: -200ms before p2 to +800ms after p2 onset
    # p2 onset is at index 2031. Wait, p1 is 1000->1531. p2 is 1531->2062. Wait, let's check TASK_DETAILS.
    # fx: 500:1000 (-500 to 0)
    # p1: 1000:1531 (0 to 531)
    # d1: 1531:2031 (531 to 1031)
    # p2: 2031:2562 (1031 to 1562)
    
    p2_onset = 2031
    win_start = p2_onset - 500 # 1531 (d1 onset)
    win_end = p2_onset + 1000  # 3031 (mid d2)
    time_offset = p2_onset # Time 0 is p2 onset
    
    fx_start = 500
    fx_end = 1000
    
    for area in CANONICAL_AREAS:
        print(f"Processing {area}...")
        
        # Load Baseline (fx)
        # We can use RRRR for baseline
        lfp_fx = get_area_lfp(area, 'RRRR', (fx_start, fx_end))
        if lfp_fx.size == 0:
            print(f"Skipping {area}, no data.")
            continue
            
        _, _, power_fx = compute_tfr(lfp_fx)
        base_power = power_fx.mean(axis=1, keepdims=True) # Mean over time for each freq
        
        # Load Stimulus (RRRR p2)
        lfp_stim = get_area_lfp(area, 'RRRR', (win_start, win_end))
        freqs, times, power_stim = compute_tfr(lfp_stim)
        
        # Load Omission (RXRR p2)
        lfp_omit = get_area_lfp(area, 'RXRR', (win_start, win_end))
        _, _, power_omit = compute_tfr(lfp_omit)
        
        # Convert to dB relative to baseline
        db_stim = 10 * np.log10(power_stim / (base_power + 1e-10))
        db_omit = 10 * np.log10(power_omit / (base_power + 1e-10))
        db_diff = db_omit - db_stim
        
        # Times relative to p2 onset
        times_rel = times - 500 # since win_start is 500ms before p2 onset
        
        # Plotting
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            subplot_titles=(f"Stimulus (RRRR)", f"Omission (RXRR)", f"Difference (Omission - Stimulus)"),
                            vertical_spacing=0.08)
                            
        zmax = max(np.max(np.abs(db_stim)), np.max(np.abs(db_omit))) * 0.8 # Scale down slightly for better contrast
        zmax_diff = np.max(np.abs(db_diff)) * 0.8
        
        # Stimulus
        fig.add_trace(go.Heatmap(x=times_rel, y=freqs, z=db_stim, colorscale='RdBu_r', zmid=0, zmin=-zmax, zmax=zmax, colorbar=dict(title="dB", x=1.02, y=0.85, len=0.25)), row=1, col=1)
        # Omission
        fig.add_trace(go.Heatmap(x=times_rel, y=freqs, z=db_omit, colorscale='RdBu_r', zmid=0, zmin=-zmax, zmax=zmax, colorbar=dict(title="dB", x=1.02, y=0.5, len=0.25)), row=2, col=1)
        # Difference
        fig.add_trace(go.Heatmap(x=times_rel, y=freqs, z=db_diff, colorscale='PRGn', zmid=0, zmin=-zmax_diff, zmax=zmax_diff, colorbar=dict(title="dB Diff", x=1.02, y=0.15, len=0.25)), row=3, col=1)
        
        # Mark p2 onset and offset
        for i in range(1, 4):
            fig.add_vline(x=0, line_dash="dash", line_color="black", row=i, col=1)
            fig.add_vline(x=531, line_dash="dash", line_color="black", row=i, col=1)
            fig.update_yaxes(title_text="Frequency (Hz)", row=i, col=1)
            
        fig.update_xaxes(title_text="Time relative to p2 onset (ms)", row=3, col=1)
        
        fig.update_layout(
            title=f"Figure 6: Time-Frequency Representation ({area})<br><i>Power changes (dB) relative to Fixation Baseline</i>",
            height=900, width=1000,
            template="plotly_white"
        )
        
        out_path = OUTPUT_DIR / f'figure_6_tfr_{area}.html'
        fig.write_html(out_path)
        print(f"Saved {out_path}")

if __name__ == "__main__":
    generate_figure_6()
