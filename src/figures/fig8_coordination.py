# core
import numpy as np
import plotly.graph_objects as go
from src.core.plotting import OmissionPlotter
from src.core.logger import log
from src.core.data_loader import DataLoader

def generate_figure_8(output_dir: str = "D:/drive/outputs/oglo-8figs/f008"):
    """
    Generates Figure 8: Cross-Area Coordination.
    Uses real evoked LFP from all 11 areas to compute a connectivity matrix during omission.
    """
    log.progress(f"""[action] Generating Figure 8: Cross-Area Coordination in {output_dir}...""")
    
    loader = DataLoader()
    areas = loader.CANONICAL_AREAS
    n = len(areas)
    
    # Store omission window LFP (samples 2031 to 2562)
    area_signals = []
    valid_areas = []
    
    for area in areas:
        log.progress(f"""[action] Extracting coordination signal for {area}""")
        lfp_list = loader.get_signal(mode="lfp", condition="AXAB", area=area)
        if not lfp_list:
            area_signals.append(np.zeros(531)) # Placeholder
            continue
        
        evoked_lfp = np.mean(np.vstack([np.mean(a, axis=0) for a in lfp_list if a.size>0]), axis=0)
        lfp_omission = evoked_lfp[2031:2562]
        
        if len(lfp_omission) == 531:
            area_signals.append(lfp_omission)
            valid_areas.append(area)
        else:
            area_signals.append(np.zeros(531))
            
    # Compute correlation matrix
    signal_matrix = np.vstack(area_signals) # (11, 531)
    
    # Ignore areas with all zeros
    corr_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if np.std(signal_matrix[i]) > 0 and np.std(signal_matrix[j]) > 0:
                corr_matrix[i, j] = np.corrcoef(signal_matrix[i], signal_matrix[j])[0, 1]
                
    plotter = OmissionPlotter(
        title="Figure 8: Cross-Area Coordination",
        subtitle="Evoked Correlation Matrix (Proxy for CCA) during Omission Window"
    )
    plotter.set_axes("Target Area", "Hierarchy", "Source Area", "Hierarchy")
    
    heatmap = go.Heatmap(
        z=corr_matrix, x=areas, y=areas, colorscale="Viridis",
        colorbar=dict(title="Correlation")
    )
    plotter.add_trace(heatmap, name="CCA Routing")
    
    plotter.save(output_dir, "fig8_cross_area_cca_real")
    log.progress(f"""[action] Figure 8 generation complete.""")

if __name__ == "__main__":
    generate_figure_8()