import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import os

def plot_putative_cell_types(results: dict, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    areas = list(results.keys())
    if not areas:
        log.warning("No Putative Cell Type results to plot.")
        return
        
    e_means = [results[a]["e_mean"] for a in areas]
    e_sems = [results[a]["e_sem"] for a in areas]
    
    i_means = [results[a]["i_mean"] for a in areas]
    i_sems = [results[a]["i_sem"] for a in areas]
    
    plotter = OmissionPlotter(
        title="Figure f030: Putative Cell Type Omission Recruitment",
        subtitle="Excitatory (Broad) vs Inhibitory (Narrow) Firing Rate Delta (\u0394Hz)"
    )
    plotter.set_axes("Cortical Area", "", "Omission Response Delta", "\u0394Hz")
    
    plotter.add_trace(go.Bar(
        x=areas,
        y=e_means,
        error_y=dict(type='data', array=e_sems, visible=True),
        marker_color="#CFB87C" # GOLD
    ), name="Excitatory (E)")
    
    plotter.add_trace(go.Bar(
        x=areas,
        y=i_means,
        error_y=dict(type='data', array=i_sems, visible=True),
        marker_color="#9400D3" # VIOLET
    ), name="Inhibitory (I)")
    
    plotter.fig.update_layout(barmode='group')
    plotter.save(output_dir, "f030_putative_cell_types_summary")
    
    # 2. Ratio Plot (I/E)
    ratio_plotter = OmissionPlotter(
        title="Figure f030: I/E Omission Ratio",
        subtitle="Ratio of Inhibitory to Excitatory Omission Response"
    )
    ratio_plotter.set_axes("Cortical Area", "", "I/E Ratio", "")
    
    ratios = []
    for a in areas:
        e = results[a]["e_mean"]
        i = results[a]["i_mean"]
        # avoid div by zero
        ratios.append((i / e) if e > 0 else 0)
        
    ratio_plotter.add_trace(go.Bar(
        x=areas,
        y=ratios,
        marker_color="#4B0082"
    ), name="I/E Ratio")
    ratio_plotter.save(output_dir, "f030_putative_cell_types_ratio")
    
    log.progress("Putative Cell Type plots saved.")
