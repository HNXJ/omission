# core
import numpy as np
import scipy.signal
import plotly.graph_objects as go
from src.core.plotting import OmissionPlotter
from src.core.logger import log
from src.core.data_loader import DataLoader

def butter_bandpass_filter(data, lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = scipy.signal.butter(order, [low, high], btype='band')
    return scipy.signal.filtfilt(b, a, data, axis=-1)

def get_band_power_db(lfp_trials, low, high, fs, baseline_power):
    """
    Computes relative power in dB for a band across trials.
    lfp_trials: (trials, time)
    """
    filtered = butter_bandpass_filter(lfp_trials, low, high, fs)
    # Compute power via Hilbert envelope
    analytic = scipy.signal.hilbert(filtered, axis=-1)
    power = np.abs(analytic)**2
    # Normalize to baseline
    rel_power = 10 * np.log10(power / (baseline_power + 1e-10))
    return rel_power

def generate_figure_6(output_dir: str = "D:/drive/outputs/oglo-8figs/f006"):
    """
    Generates Figure 6: Band-Specific LFP Dynamics with ±SEM shaded error bars.
    """
    log.progress(f"[action] Generating Figure 6: Band Power (11 Areas) in {output_dir}...")
    
    loader = DataLoader()
    fs = 1000
    bands = {
        "Delta (1-4 Hz)": (1, 4, "#9400D3"),
        "Theta (4-8 Hz)": (4, 8, "#4B0082"),
        "Alpha (8-13 Hz)": (8, 13, "#0000FF"),
        "Beta (13-30 Hz)": (13, 30, "#00FF00"),
        "Low Gamma (35-55 Hz)": (35, 55, "#FFFF00"),
        "High Gamma (65-100 Hz)": (65, 100, "#FF0000")
    }
    
    for area in loader.CANONICAL_AREAS:
        log.progress(f"[action] Processing Area: {area} for Band Power")
        
        lfp_list = loader.get_signal(mode="lfp", condition="AXAB", area=area)
        if not lfp_list: continue
        
        # Merge all session trials for this area
        all_lfp = np.vstack([np.mean(a, axis=1) for a in lfp_list if a.size > 0]) # (total_trials, time)
        
        # Define baseline power per band from the fixation window (-1000 to 0ms)
        # In AXAB, p1 starts at sample 1000. Fixation is 0:1000.
        
        plotter = OmissionPlotter(
            title=f"Figure 6: {area} Band-Specific LFP Dynamics",
            subtitle="Relative Power (dB) with ±SEM (AXAB Condition)"
        )
        plotter.set_axes("Time from Stimulus 1", "ms", "Relative Power", "dB")
        
        time_vec = np.linspace(-1000, 1562, all_lfp.shape[1])
        
        for name, (low, high, color) in bands.items():
            # Get baseline mean power for this band
            filt_full = butter_bandpass_filter(all_lfp, low, high, fs)
            pwr_full = np.abs(scipy.signal.hilbert(filt_full, axis=-1))**2
            base_pwr = np.mean(pwr_full[:, 0:1000]) # Mean power across trials and time in baseline
            
            # Compute dB trace per trial
            db_trials = 10 * np.log10(pwr_full / (base_pwr + 1e-10))
            
            mean_trace = np.mean(db_trials, axis=0)
            sem_trace = np.std(db_trials, axis=0) / np.sqrt(db_trials.shape[0])
            
            # Add shaded error bars via OmissionPlotter's native traces (using two scatters)
            # Upper bound
            plotter.add_trace(go.Scatter(
                x=time_vec, y=mean_trace + sem_trace,
                mode='lines', line=dict(width=0),
                showlegend=False, hoverinfo='skip'
            ), name=f"{name}_up")
            
            # Lower bound with fill
            plotter.add_trace(go.Scatter(
                x=time_vec, y=mean_trace - sem_trace,
                mode='lines', line=dict(width=0),
                fill='tonexty', fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}",
                showlegend=False, hoverinfo='skip'
            ), name=f"{name}_down")
            
            # Mean line
            plotter.add_trace(go.Scatter(
                x=time_vec, y=mean_trace,
                mode='lines', line=dict(color=color, width=3)
            ), name=name)
            
        plotter.add_xline(0, name="p1")
        plotter.add_xline(531, name="d1")
        plotter.add_xline(1031, name="p2 (Omission)")
        plotter.add_xline(1562, name="d2")
        plotter.save(output_dir, f"fig6_band_power_{area}")
        
    log.progress(f"[action] Figure 6 complete for all areas.")

if __name__ == "__main__":
    generate_figure_6()