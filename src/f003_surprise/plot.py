import plotly.graph_objects as go
import numpy as np
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def plot_surprise(results: dict, output_dir: str):
    """
    Plots a bar chart of the Surprise Index across the hierarchy.
    """
    print(f"[action] Plotting Surprise Index Bar Chart")
    areas = list(results.keys())
    # Global stats for the summary plot
    global_stars = ""
    global_p = 1.0
    global_tier = "Null"
    if areas:
        # Take mean or max sig across areas for the global subtitle
        global_p = np.min([results[a]['stats']['p'] for a in areas])
        from src.analysis.stats.tiers import get_significance_tier
        global_tier, k, global_stars = get_significance_tier(global_p)

    plotter = OmissionPlotter(
        title=f"Figure f003: Population Surprise Index {global_stars}",
        x_label="Cortical Area (S_k Tier)",
        y_label="Surprise Index",
        subtitle=f"Global Surprise: {global_tier} (p={global_p:.2e}) | Window: [0, 500]ms",
        y_unit="a.u."
    )
    
    # Format labels with stats: Area ***
    display_labels = []
    for a in areas:
        stars = results[a]['stats']['stars']
        display_labels.append(f"{a}<br>{stars if stars else 'n.s.'}")
        
    means = [results[a]['mean'] for a in areas]
    sems = [results[a]['sem'] for a in areas]
    
    plotter.fig.add_trace(go.Bar(
        x=display_labels,
        y=means,
        error_y=dict(type='data', array=sems, visible=True),
        marker_color="#9400D3",
        marker_line=dict(width=1, color="black")
    ))
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    filename = "f003_surprise_index.html"
    filepath = os.path.join(output_dir, filename)
    plotter.fig.write_html(filepath, include_plotlyjs="cdn")
    log.progress(f"Saved {filename}")
