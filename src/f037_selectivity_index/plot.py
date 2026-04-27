# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter

def plot_selectivity_index(results: dict):
    """
    Plots Stimulus Selectivity Index across areas.
    """
    plotter = OmissionPlotter(
        title="Stimulus Selectivity Index (SSI) during Omission",
        x_label="Cortical Area",
        y_label="Selectivity Index",
        subtitle="Comparing predictable stim (p1) vs Omission (p2)",
        y_unit="norm"
    )
    
    areas = list(results.keys())
    means = [results[a]["ssi_mean"] for a in areas]
    sems = [results[a]["ssi_sem"] for a in areas]
    
    trace = go.Bar(
        x=areas,
        y=means,
        error_y=dict(type='data', array=sems, visible=True),
        marker_color='#CFB87C', # Madelane Golden
    )
    
    plotter.add_trace(trace, name="SSI")
    plotter.set_axes("Brain Area", "Unit", "SSI", "(R_pref - R_omission) / (R_pref + R_omission)")
    
    # Madelane Golden Dark Theme overrides
    plotter.fig.update_layout(
        template="plotly_white",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black')
    )
    
    plotter.fig.update_xaxes(showgrid=True, gridcolor='lightgray', linecolor='black')
    plotter.fig.update_yaxes(showgrid=True, gridcolor='lightgray', linecolor='black')
    
    return plotter
