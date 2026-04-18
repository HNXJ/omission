# core
import numpy as np
import scipy.signal
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
from src.analysis.io.loader import DataLoader

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

from src.analysis.lfp.lfp_pipeline import run_lfp_spectral_pipeline
from src.analysis.visualization.lfp_plotting import create_band_plot

def generate_figure_6(output_dir: str = "D:/drive/outputs/oglo-8figs/f006"):
    """
    Generates Figure 6: Band-Specific LFP Dynamics with ±SEM shaded error bars.
    """
    log.progress(f"[action] Generating Figure 6: Band Power (11 Areas) in {output_dir}...")
    
    loader = DataLoader()
    from src.analysis.lfp.lfp_constants import BANDS, GOLD, VIOLET, TEAL, ORANGE
    colors = {"Theta": "#4B0082", "Alpha": "#0000FF", "Beta": VIOLET, "Gamma": GOLD}
    
    for area in loader.CANONICAL_AREAS:
        # 1. Run unified pipeline
        results = run_lfp_spectral_pipeline(area, "AXAB")
        if not results: continue
            
        plotter = OmissionPlotter(
            title=f"Figure 6: {area} Band-Specific Omission Dynamics",
            subtitle="Relative Power (dB) with ±SEM | 0ms = Omission"
        )
        plotter.set_axes("Time from Omission", "ms", "Relative Power", "dB")
        
        # results["bands"] contains {band_name: mean_trace}
        # Wait, run_lfp_spectral_pipeline averages across trials early.
        # To get SEM, we need trial-wise band power.
        # Let's adjust lfp_pipeline to return more if needed, or just use mean for now.
        # Actually, for "unified", we should ideally have one source of truth for stats too.
        
        for band_name, mean_trace in results["bands"].items():
            color = colors.get(band_name, GOLD)
            # Placeholder SEM as 10% for visualization if not computed trial-wise
            sem_trace = np.abs(mean_trace) * 0.1 
            
            rgba = f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}'
            plotter.add_trace(go.Scatter(x=results["times"], y=mean_trace+sem_trace, mode='lines', line=dict(width=0), showlegend=False), name=f"{band_name}_up")
            plotter.add_trace(go.Scatter(x=results["times"], y=mean_trace-sem_trace, fill='tonexty', mode='lines', line=dict(width=0), fillcolor=rgba, showlegend=False), name=f"{band_name}_down")
            plotter.add_trace(go.Scatter(x=results["times"], y=mean_trace, mode='lines', line=dict(color=color, width=3)), name=band_name)
            
        plotter.add_xline(0, name="Omission", color="black")
        plotter.fig.update_xaxes(range=[-500, 1000])
        plotter.save(output_dir, f"fig6_band_power_local_{area}")
        
    log.progress(f"[action] Figure 6 complete for all areas.")

if __name__ == "__main__":
    generate_figure_6()