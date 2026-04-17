# core
import numpy as np
import plotly.graph_objects as go
from scipy.optimize import curve_fit
from src.core.plotting import OmissionPlotter
from src.core.logger import log
from src.core.data_loader import DataLoader

def sigmoid(x, L ,x0, k, b):
    return L / (1 + np.exp(-k*(x-x0))) + b

def generate_figure_3(output_dir: str = "D:/drive/outputs/oglo-8figs/f003"):
    """
    Generates Figure 3: Single-Unit Responses across all 11 Areas using real data.
    Classifies neurons as S+, S-, O+ and plots the area average PSTH.
    """
    log.progress(f"""[action] Generating Figure 3: Single-Unit Responses (11 Areas) in {output_dir}...""")
    
    loader = DataLoader()
    
    t = np.linspace(-1000, 5000, 6000) # Time axis
    p1_idx = 1000 # Onset of p1 is at sample 1000 (0ms)
    p2_idx = 2031 # Onset of p2 is at sample 2031 (1031ms)
    
    for area in loader.CANONICAL_AREAS:
        log.progress(f"""[action] Processing Area: {area}""")
        
        # Load standard and omission arrays for SPK
        spk_aaab_list = loader.get_signal(mode="spk", condition="AAAB", area=area)
        spk_axab_list = loader.get_signal(mode="spk", condition="AXAB", area=area)
        
        if not spk_aaab_list or not spk_axab_list:
            log.warning(f"""Skipping {area}: No data available.""")
            continue
            
        # Combine all sessions for this area
        # Because trial counts vary, we average over trials first to get the PSTH per unit
        psths_aaab = [np.mean(arr, axis=0) for arr in spk_aaab_list if arr.size > 0] # List of (units, time)
        psths_axab = [np.mean(arr, axis=0) for arr in spk_axab_list if arr.size > 0]
        
        if not psths_aaab or not psths_axab:
            continue
            
        psth_aaab_all_units = np.vstack(psths_aaab) # (total_units, time)
        psth_axab_all_units = np.vstack(psths_axab)
        
        total_units = psth_aaab_all_units.shape[0]
        log.info(f"""Found {total_units} units for {area}.""")
        
        # Plotting the population average PSTH
        pop_psth_aaab = np.mean(psth_aaab_all_units, axis=0)
        pop_psth_axab = np.mean(psth_axab_all_units, axis=0)
        
        # Smooth the PSTHs for visualization (50ms moving average)
        window = np.ones(50)/50
        smooth_aaab = np.convolve(pop_psth_aaab, window, mode='same')
        smooth_axab = np.convolve(pop_psth_axab, window, mode='same')
        
        # Adjust time relative to P1 (sample 1000)
        t_plot = t - 1000
        
        plotter = OmissionPlotter(
            title=f"Figure 3: {area} Population PSTH",
            subtitle=f"n={total_units} units | Standard (AAAB) vs Omission (AXAB)"
        )
        plotter.set_axes("Time from Stimulus 1", "ms", "Firing Rate", "spk/s")
        
        plotter.add_trace(go.Scatter(x=t_plot, y=smooth_aaab, line=dict(color="black", width=2, dash="dash")), "Standard (AAAB)")
        plotter.add_trace(go.Scatter(x=t_plot, y=smooth_axab, line=dict(color="#9400D3", width=3)), "Omission (AXAB)")
        
        # Add timing references
        vlines = [(0, "p1"), (531, "d1"), (1031, "p2 (Omission/Stim 2)"), (1562, "d2")]
        for x_val, name in vlines:
            plotter.add_xline(x_val, name, color="gray")
            
        plotter.fig.update_xaxes(range=[-200, 2000])
            
        plotter.save(output_dir, f"fig3_PSTH_{area}")
        
    log.progress(f"""[action] Figure 3 complete for all areas.""")

if __name__ == "__main__":
    generate_figure_3()