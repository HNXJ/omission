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
    """
    log.progress(f"""[action] Generating Figure 5: TFR Spectrograms (11 Areas) in {output_dir}...""")
    
    loader = DataLoader()
    fs = 1000  # 1000 Hz sampling rate
    
    for area in loader.CANONICAL_AREAS:
        log.progress(f"""[action] Processing Area: {area} for TFR""")
        
        # Load Omission arrays for LFP
        lfp_axab_list = loader.get_signal(mode="lfp", condition="AXAB", area=area)
        
        if not lfp_axab_list:
            log.warning(f"""Skipping {area}: No data available.""")
            continue
            
        # Average across trials and channels to get a single 1D mean LFP array for the area
        # Note: In a full rigorous pipeline, TFR is computed per-trial, then averaged.
        # For pipeline execution efficiency here, we average the signal first (Evoked TFR).
        evoked_lfp_list = [np.mean(arr, axis=(0, 1)) for arr in lfp_axab_list if arr.size > 0]
        
        if not evoked_lfp_list:
            continue
            
        evoked_lfp = np.mean(np.vstack(evoked_lfp_list), axis=0) # Shape: (6000,)
        
        # Compute Spectrogram
        f, t_spec, Sxx = scipy.signal.spectrogram(evoked_lfp, fs=fs, window='hann', nperseg=256, noverlap=200)
        
        # Convert to dB
        Sxx_db = 10 * np.log10(Sxx + 1e-10)
        
        # Limit frequency to 1-100 Hz
        freq_mask = (f >= 1) & (f <= 100)
        f_plot = f[freq_mask]
        Sxx_plot = Sxx_db[freq_mask, :]
        
        # Adjust time relative to P1 (sample 1000 -> 0ms)
        t_spec_ms = (t_spec * 1000) - 1000
        
        plotter = OmissionPlotter(
            title=f"Figure 5: {area} Time-Frequency Spectrogram",
            subtitle="Evoked dB Power Change (Omission AXAB)"
        )
        plotter.set_axes("Time from Stimulus 1", "ms", "Frequency", "Hz")
        
        heatmap = go.Heatmap(
            z=Sxx_plot, x=t_spec_ms, y=f_plot, colorscale="Jet", zmid=np.median(Sxx_plot),
            colorbar=dict(title="dB Power")
        )
        plotter.add_trace(heatmap, name="TFR")
        
        # Add timing lines
        vlines = [(0, "p1"), (531, "d1"), (1031, "p2 (Omission)"), (1562, "d2")]
        for x_val, name in vlines:
            plotter.add_xline(x_val, name, color="black")
            
        plotter.fig.update_xaxes(range=[-200, 2000])
        plotter.save(output_dir, f"fig5_TFR_{area}")
        
    log.progress(f"""[action] Figure 5 complete for all areas.""")

if __name__ == "__main__":
    generate_figure_5()