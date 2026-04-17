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

def get_band_envelope(data, lowcut, highcut, fs):
    band_signal = butter_bandpass_filter(data, lowcut, highcut, fs)
    return np.abs(scipy.signal.hilbert(band_signal))

def generate_figure_6(output_dir: str = "D:/drive/outputs/oglo-8figs/f006"):
    """
    Generates Figure 6: Band-Specific LFP Dynamics for 11 Areas using real data.
    Extracts Delta, Theta, Alpha, Beta, Low Gamma, and High Gamma.
    Computes Relative Power Change (dB) from Baseline.
    """
    log.progress(f"""[action] Generating Figure 6: Band-Specific LFP (11 Areas) in {output_dir}...""")
    
    loader = DataLoader()
    fs = 1000
    t = np.linspace(-1000, 5000, 6000) # Entire 6000ms window
    t_plot = t - 1000 # Align 0 to P1 (sample 1000)
    
    bands = {
        "Delta (1-4 Hz)": (1, 4, "gray"),
        "Theta (4-8 Hz)": (4, 8, "cyan"),
        "Alpha (8-13 Hz)": (8, 13, "green"),
        "Beta (13-30 Hz)": (13, 30, "#9400D3"),
        "Low Gamma (35-55 Hz)": (35, 55, "#CFB87C"),
        "High Gamma (65-100 Hz)": (65, 100, "orange")
    }
    
    # Baseline mask (-1000ms to 0ms before P1)
    baseline_mask = (t_plot >= -1000) & (t_plot < 0)
    
    for area in loader.CANONICAL_AREAS:
        log.progress(f"""[action] Processing Area: {area} for Band Power""")
        
        lfp_axab_list = loader.get_signal(mode="lfp", condition="AXAB", area=area)
        
        if not lfp_axab_list:
            continue
            
        # Evoked LFP
        evoked_lfp_list = [np.mean(arr, axis=(0, 1)) for arr in lfp_axab_list if arr.size > 0]
        if not evoked_lfp_list:
            continue
        evoked_lfp = np.mean(np.vstack(evoked_lfp_list), axis=0)
        
        plotter = OmissionPlotter(
            title=f"Figure 6: {area} Band-Specific LFP Dynamics",
            subtitle="Relative Power (dB change from baseline) during Omission (AXAB)"
        )
        plotter.set_axes("Time from Stimulus 1", "ms", "Relative Power", "dB")
        
        valid_traces = 0
        for band_name, (low, high, color) in bands.items():
            env = get_band_envelope(evoked_lfp, low, high, fs)
            # Power is amplitude squared
            power = env ** 2
            
            # Baseline mean power
            base_power = np.mean(power[baseline_mask]) + 1e-10
            
            # Relative Power in dB
            rel_power_db = 10 * np.log10((power + 1e-10) / base_power)
            
            # Smooth the dB trace for plotting (e.g. 50ms moving average)
            smooth_rel_power = np.convolve(rel_power_db, np.ones(50)/50, mode='same')
            
            # Safety guard
            if np.all(np.isnan(smooth_rel_power)) or np.all(smooth_rel_power == 0):
                continue
                
            plotter.add_trace(go.Scatter(x=t_plot, y=smooth_rel_power, line=dict(color=color, width=2)), band_name)
            valid_traces += 1
            
        if valid_traces == 0:
            log.warning(f"""Skipping {area}: All band traces invalid.""")
            continue
            
        vlines = [(0, "p1"), (531, "d1"), (1031, "p2 (Omission)"), (1562, "d2")]
        for x_val, name in vlines:
            plotter.add_xline(x_val, name, color="black")
            
        plotter.fig.update_xaxes(range=[-500, 2000])
        plotter.save(output_dir, f"fig6_band_power_{area}")
        
    log.progress(f"""[action] Figure 6 complete for all areas.""")

if __name__ == "__main__":
    generate_figure_6()