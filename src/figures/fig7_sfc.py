# core
import numpy as np
import scipy.signal
import plotly.graph_objects as go
from src.core.plotting import OmissionPlotter
from src.core.logger import log
from src.core.data_loader import DataLoader

def compute_ppc_proxy(lfp_signal, spk_signal, fs=1000):
    """
    Computes a simplified Phase-of-Firing metric proxy for the Beta band.
    """
    nyq = 0.5 * fs
    b, a = scipy.signal.butter(4, [15/nyq, 30/nyq], btype='band')
    beta_lfp = scipy.signal.filtfilt(b, a, lfp_signal)
    analytic_sig = scipy.signal.hilbert(beta_lfp)
    phase = np.angle(analytic_sig)
    
    # Weight phase by spike probability
    phase_bins = np.linspace(-np.pi, np.pi, 36)
    hist, _ = np.histogram(phase, bins=phase_bins, weights=spk_signal)
    
    # Smooth circular histogram
    padded = np.pad(hist, 2, mode='wrap')
    hist_smooth = np.convolve(padded, np.ones(5)/5, mode='valid')
    return phase_bins[:-1], hist_smooth

def generate_figure_7(output_dir: str = "D:/drive/outputs/oglo-8figs/f007"):
    """
    Generates Figure 7: Spike-Field Coupling (SFC) for 11 areas.
    """
    log.progress(f"""[action] Generating Figure 7: Spike-Field Coupling in {output_dir}...""")
    
    loader = DataLoader()
    
    for area in loader.CANONICAL_AREAS:
        log.progress(f"""[action] Processing Area: {area} for SFC""")
        
        lfp_axab_list = loader.get_signal(mode="lfp", condition="AXAB", area=area)
        spk_axab_list = loader.get_signal(mode="spk", condition="AXAB", area=area)
        
        if not lfp_axab_list or not spk_axab_list:
            continue
            
        # Average to evoked for fast proxy
        evoked_lfp = np.mean(np.vstack([np.mean(a, axis=0) for a in lfp_axab_list if a.size>0]), axis=0)
        evoked_spk = np.mean(np.vstack([np.mean(a, axis=0) for a in spk_axab_list if a.size>0]), axis=0)
        
        # Focus on Omission Window (p2: 1031 to 1562 -> samples 2031 to 2562)
        lfp_omission = evoked_lfp[2031:2562]
        spk_omission = evoked_spk[2031:2562]
        
        if len(lfp_omission) == 0:
            continue
            
        phase, ppc = compute_ppc_proxy(lfp_omission, spk_omission)
        
        theta_deg = np.degrees(phase)
        theta_deg = np.where(theta_deg < 0, theta_deg + 360, theta_deg)
        
        # Sort for polar plot
        idx = np.argsort(theta_deg)
        theta_deg = theta_deg[idx]
        ppc = ppc[idx]
        
        plotter = OmissionPlotter(
            title=f"Figure 7: {area} Spike-Field Coupling (SFC)",
            subtitle="Phase-of-Firing Polar Plot (Beta Band) during Omission"
        )
        
        plotter.fig.add_trace(go.Scatterpolar(
            r=ppc, theta=theta_deg, mode='lines', fill='toself',
            name=f'{area} Units (PPC)', line_color='#9400D3'
        ))
        
        plotter.fig.update_layout(polar=dict(radialaxis=dict(visible=True)))
        plotter.save(output_dir, f"fig7_sfc_polar_{area}")
        
    log.progress(f"""[action] Figure 7 complete for all areas.""")

if __name__ == "__main__":
    generate_figure_7()