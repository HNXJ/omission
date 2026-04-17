# core
import numpy as np
import scipy.signal
import plotly.graph_objects as go
from src.core.plotting import OmissionPlotter
from src.core.logger import log
from src.core.data_loader import DataLoader

def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = scipy.signal.butter(order, [low, high], btype='band')
    y = scipy.signal.filtfilt(b, a, data)
    return y

def generate_figure_6(output_dir: str = "D:/drive/outputs/oglo-8figs/f006"):
    """
    Generates Figure 6: Band-Specific LFP Dynamics for 11 Areas using real data.
    """
    log.progress(f"""[action] Generating Figure 6: Band-Specific LFP (11 Areas) in {output_dir}...""")
    
    loader = DataLoader()
    fs = 1000
    t = np.linspace(-1000, 5000, 6000)
    t_plot = t - 1000
    
    for area in loader.CANONICAL_AREAS:
        log.progress(f"""[action] Processing Area: {area} for Band Power""")
        
        lfp_axab_list = loader.get_signal(mode="lfp", condition="AXAB", area=area)
        
        if not lfp_axab_list:
            continue
            
        # Average across trials and channels (Evoked LFP)
        evoked_lfp_list = [np.mean(arr, axis=(0, 1)) for arr in lfp_axab_list if arr.size > 0]
        if not evoked_lfp_list:
            continue
        evoked_lfp = np.mean(np.vstack(evoked_lfp_list), axis=0)
        
        # Extract Bands
        beta_signal = butter_bandpass_filter(evoked_lfp, 15, 30, fs)
        gamma_signal = butter_bandpass_filter(evoked_lfp, 50, 90, fs)
        
        # Envelope (Analytic Amplitude)
        beta_env = np.abs(scipy.signal.hilbert(beta_signal))
        gamma_env = np.abs(scipy.signal.hilbert(gamma_signal))
        
        # Z-score normalization
        beta_z = (beta_env - np.mean(beta_env)) / np.std(beta_env)
        gamma_z = (gamma_env - np.mean(gamma_env)) / np.std(gamma_env)
        
        plotter = OmissionPlotter(
            title=f"Figure 6: {area} Band-Specific LFP Dynamics",
            subtitle="Beta (Feedback) vs Gamma (Feedforward) during Omission (AXAB)"
        )
        plotter.set_axes("Time from Stimulus 1", "ms", "Normalized Power", "z-score")
        
        plotter.add_trace(go.Scatter(x=t_plot, y=beta_z, line=dict(color="#9400D3", width=3)), "Beta (15-30 Hz)")
        plotter.add_trace(go.Scatter(x=t_plot, y=gamma_z, line=dict(color="#CFB87C", width=3)), "Gamma (50-90 Hz)")
        
        vlines = [(0, "p1"), (531, "d1"), (1031, "p2 (Omission)"), (1562, "d2")]
        for x_val, name in vlines:
            plotter.add_xline(x_val, name, color="gray")
            
        plotter.fig.update_xaxes(range=[-200, 2000])
        plotter.save(output_dir, f"fig6_band_power_{area}")
        
    log.progress(f"""[action] Figure 6 complete for all areas.""")

if __name__ == "__main__":
    generate_figure_6()