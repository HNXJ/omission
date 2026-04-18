# core
import numpy as np
import scipy.signal
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
from src.analysis.io.loader import DataLoader

def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = scipy.signal.butter(order, [low, high], btype='band')
    return scipy.signal.filtfilt(b, a, data)

def get_band_power(data, lowcut, highcut, fs):
    band_signal = butter_bandpass_filter(data, lowcut, highcut, fs)
    env = np.abs(scipy.signal.hilbert(band_signal))
    return env ** 2

from src.analysis.lfp.lfp_pipeline import get_lfp_signal
from src.analysis.lfp.lfp_tfr import compute_multitaper_tfr, collapse_band_power
from src.analysis.lfp.lfp_preproc import preprocess_lfp, baseline_normalize

def generate_figure_8(output_dir: str = "D:/drive/outputs/oglo-8figs/f008"):
    """
    Generates Figure 8: Cross-Area Spectral Coordination.
    """
    log.progress(f"[action] Generating Figure 8: Spectral Coordination in {output_dir}...")
    
    loader = DataLoader()
    areas = loader.CANONICAL_AREAS
    n = len(areas)
    
    beta_omit = np.zeros((n, 2000))
    gamma_omit = np.zeros((n, 2000))
    
    for i, area in enumerate(areas):
        # Use modular get_lfp_signal with omission alignment
        lfp = get_lfp_signal(area, "AXAB", align_to="omission")
        if lfp.size == 0: continue
            
        # Preprocess
        lfp_clean = preprocess_lfp(lfp)
        
        # Evoked LFP for envelope correlation proxy
        evoked = np.mean(lfp_clean, axis=(0, 1))
        
        # Power traces
        beta_power = get_band_power(evoked, 13, 30, 1000)
        gamma_power = get_band_power(evoked, 35, 80, 1000)
        
        beta_omit[i, :] = beta_power
        gamma_omit[i, :] = gamma_power
        
    def compute_corr_matrix(data_matrix, window=(1000, 1531)):
        # window is relative to the 2000ms slice
        corr_mat = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                seg_i = data_matrix[i, window[0]:window[1]]
                seg_j = data_matrix[j, window[0]:window[1]]
                if np.std(seg_i) > 1e-10 and np.std(seg_j) > 1e-10:
                    corr_mat[i, j] = np.corrcoef(seg_i, seg_j)[0, 1]
        return corr_mat
        
    mats = {
        "Beta_Baseline": compute_corr_matrix(beta_omit, window=(750, 950)),
        "Beta_Omission": compute_corr_matrix(beta_omit, window=(1000, 1531)),
        "Gamma_Baseline": compute_corr_matrix(gamma_omit, window=(750, 950)),
        "Gamma_Omission": compute_corr_matrix(gamma_omit, window=(1000, 1531))
    }
    
    for name, mat in mats.items():
        band, window = name.split("_")
        plotter = OmissionPlotter(
            title=f"Figure 8: {band} Band Power Correlation",
            subtitle=f"{window} Window (11x11 Cross-Area Harmony)"
        )
        plotter.set_axes("Target Area", "Hierarchy", "Source Area", "Hierarchy")
        
        # Determine color scale: Stimulus = Gamma dominated, Omission = Beta dominated
        colorscale = "Viridis" if band == "Beta" else "Plasma"
        
        heatmap = go.Heatmap(
            z=mat, x=areas, y=areas, colorscale=colorscale,
            colorbar=dict(title="Pearson r (Power)"),
            zmin=-0.5, zmax=1.0 # Standardize scales to see the flip visually
        )
        plotter.add_trace(heatmap, name=name)
        
        plotter.save(output_dir, f"fig8_spectral_harmony_{name}")
        
    log.progress(f"[action] Figure 8 spectral harmony matrices generated.")

if __name__ == "__main__":
    generate_figure_8()