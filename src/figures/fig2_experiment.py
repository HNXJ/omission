# core
import numpy as np
import plotly.graph_objects as go
from src.core.plotting import OmissionPlotter
from src.core.logger import log

def generate_figure_2(output_dir: str = "D:/drive/outputs/oglo-8figs/f002"):
    """
    Generates Figure 2: Experimental Design & Recording Summary.
    Shows the task timeline (A-B-R vs X-fx-d) and a synthetic CSD map demonstrating layer assignments.
    """
    log.progress(f"""[action] Generating Figure 2: Experimental Design in {output_dir}...""")
    
    # Part A: Task Timeline
    plotter_timeline = OmissionPlotter(
        title="Figure 2A: Task Timeline (A-B-R vs X-fx-d)",
        subtitle="Illustration of Omission pure prediction windows."
    )
    plotter_timeline.set_axes(x_label="Time", x_unit="ms", y_label="Condition", y_unit="Type")
    
    # Add synthetic timeline rectangles to show sequences
    times = [0, 531, 1031, 1562, 2062, 2593, 3093, 3624, 4124]
    labels = ["p1", "d1", "p2", "d2", "p3", "d3", "p4", "d4"]
    
    for i in range(len(times)-1):
        plotter_timeline.add_xline(times[i], f"{labels[i]} start", color="gray", dash="dot")
        
    plotter_timeline.add_trace(
        go.Scatter(x=[250, 1250, 2250, 3250], y=[1, 1, 1, 1], mode="markers+text",
                   marker=dict(size=20, color="#CFB87C"), text=["A", "A", "A", "B"], name="AAAB"),
        name="AAAB"
    )
    plotter_timeline.add_trace(
        go.Scatter(x=[250, 1250, 2250, 3250], y=[2, 2, 2, 2], mode="markers+text",
                   marker=dict(size=20, color="#9400D3"), text=["A", "X", "A", "B"], name="AXAB (Omission 2)"),
        name="AXAB"
    )
    plotter_timeline.fig.update_yaxes(tickvals=[1, 2], ticktext=["Standard (AAAB)", "Omission (AXAB)"])
    plotter_timeline.save(output_dir, "fig2A_task_timeline")
    
    # Part B: CSD Layer Assignment Map (Synthetic)
    plotter_csd = OmissionPlotter(
        title="Figure 2B: Current Source Density (CSD)",
        subtitle="FLIP/vFLIP spectral layer anchoring (Mendoza-Halliday 2024)"
    )
    plotter_csd.set_axes(x_label="Time from Stimulus", x_unit="ms", y_label="Cortical Depth", y_unit="µm")
    
    # Generate synthetic CSD pattern
    t = np.linspace(-100, 400, 200)
    depths = np.linspace(0, 2000, 128)
    T, D = np.meshgrid(t, depths)
    # create a sink/source dipole pattern
    csd = np.sin(2 * np.pi * 5 * T / 1000) * np.exp(-((D - 800)**2) / 50000) - \
          np.sin(2 * np.pi * 5 * T / 1000) * np.exp(-((D - 1200)**2) / 50000)
          
    csd_trace = go.Heatmap(z=csd, x=t, y=depths, colorscale="RdBu_r", zmid=0)
    plotter_csd.add_trace(csd_trace, name="CSD")
    
    # Add L2/3 and L5/6 layer boundaries
    plotter_csd.add_yline(y_val=800, name="L4/Superficial Border", color="black")
    plotter_csd.add_yline(y_val=1200, name="L4/Deep Border", color="black")
    plotter_csd.save(output_dir, "fig2B_csd_map")
    
    log.progress(f"""[action] Figure 2 generation complete.""")

if __name__ == "__main__":
    generate_figure_2()