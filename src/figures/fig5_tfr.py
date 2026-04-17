# core
import numpy as np
import scipy.signal
import plotly.graph_objects as go
from src.core.plotting import OmissionPlotter
from src.core.logger import log
from src.core.data_loader import DataLoader

def generate_figure_5(output_dir: str = "D:/drive/outputs/oglo-8figs/f005"):
    """
    Generates Figure 5: Time-Frequency Spectrograms (TFR) for all 11 Areas using real data.
    Implements STFT via scipy.signal.spectrogram (100ms Hanning, 98% overlap) 
    and Relative Power Change (dB) baseline normalization.
    """
    log.progress(f"""[action] Generating Figure 5: TFR Spectrograms (11 Areas) in {output_dir}...""")
    
    loader = DataLoader()
    fs = 1000  # 1000 Hz sampling rate
    nperseg = int(0.100 * fs) # 100ms Hanning window
    noverlap = int(0.098 * fs) # 98% overlap (2ms steps)
    
    for area in loader.CANONICAL_AREAS:
        log.progress(f"""[action] Processing Area: {area} for TFR""")
        
        lfp_axab_list = loader.get_signal(mode="lfp", condition="AXAB", area=area)
        
        if not lfp_axab_list:
            continue
            
        # Average across trials and channels (Evoked LFP)
        evoked_lfp_list = [np.mean(arr, axis=(0, 1)) for arr in lfp_axab_list if arr.size > 0]
        if not evoked_lfp_list:
            continue
        evoked_lfp = np.mean(np.vstack(evoked_lfp_list), axis=0) # Shape: (6000,)
        
        # Compute Spectrogram
        f, t_spec, Sxx = scipy.signal.spectrogram(evoked_lfp, fs=fs, window='hann', nperseg=nperseg, noverlap=noverlap)
        
        # Baseline Normalization: average power per frequency during fixation/pre-stimulus (-1000ms to 0ms -> first 1000 samples)
        # Sxx is (freqs, time_bins). t_spec corresponds to window centers in seconds.
        # Find time bins corresponding to t_spec < 1.0 (since signal starts at -1000ms, t=1.0 is 0ms relative to P1)
        baseline_mask = t_spec < 1.0
        baseline_power = np.mean(Sxx[:, baseline_mask], axis=1, keepdims=True)
        
        # Relative Power Change (dB)
        Sxx_db = 10 * np.log10((Sxx + 1e-10) / (baseline_power + 1e-10))
        
        # Limit frequency to 1-150 Hz
        freq_mask = (f >= 1) & (f <= 150)
        f_plot = f[freq_mask]
        Sxx_plot = Sxx_db[freq_mask, :]
        
        # Adjust time relative to P1 (sample 1000 -> 0ms)
        t_spec_ms = (t_spec * 1000) - 1000
        
        # Safety Guard: Skip if all NaNs or zeros
        if np.all(np.isnan(Sxx_plot)) or np.all(Sxx_plot == 0):
            log.warning(f"""Skipping {area}: TFR contains all NaNs or zeros.""")
            continue
            
        plotter = OmissionPlotter(
            title=f"Figure 5: {area} Time-Frequency Spectrogram",
            subtitle="Relative Power Change (dB) from Baseline (Omission AXAB)"
        )
        plotter.set_axes("Time from Stimulus 1", "ms", "Frequency", "Hz")
        
        # Plotly heatmap
        heatmap = go.Heatmap(
            z=Sxx_plot, x=t_spec_ms, y=f_plot, colorscale="Jet", zmid=0,
            colorbar=dict(title="Relative Power (dB)")
        )
        plotter.add_trace(heatmap, name="TFR")
        
        # Add timing lines
        vlines = [(0, "p1"), (531, "d1"), (1031, "p2 (Omission)"), (1562, "d2")]
        for x_val, name in vlines:
            plotter.add_xline(x_val, name, color="black")
            
        plotter.fig.update_xaxes(range=[-1000, 2000])
        plotter.save(output_dir, f"fig5_TFR_{area}")
        
    log.progress(f"""[action] Figure 5 complete for all areas.""")

if __name__ == "__main__":
    generate_figure_5()