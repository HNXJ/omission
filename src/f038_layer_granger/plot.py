# f038
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def plot_layer_granger_contrast(results_df, output_dir):
    """
    Plots the contrast between FF and FB flow across Stimulus vs Omission.
    """
    plotter = OmissionPlotter(
        title="Layer-wise Directed Information Flow",
        subtitle="V1 <-> PFC Cortical Feedback Reversal",
        template="plotly_white"
    )
    
    # Custom Madelane Golden Dark theme injection
    # Gold: #CFB87C, Violet: #9400D3
    
    # Stimulus Window
    stim_data = results_df[results_df['window'] == 'Stimulus']
    omission_data = results_df[results_df['window'] == 'Omission']
    
    # Add FF traces (V1 -> PFC)
    plotter.add_trace(go.Bar(
        x=['Stimulus', 'Omission'],
        y=[stim_data['ff_flow'].mean(), omission_data['ff_flow'].mean()],
        name='Feedforward (V1 Sup -> PFC)',
        marker_color='#CFB87C'
    ), name='FF Flow')
    
    # Add FB traces (PFC -> V1)
    plotter.add_trace(go.Bar(
        x=['Stimulus', 'Omission'],
        y=[stim_data['fb_flow'].mean(), omission_data['fb_flow'].mean()],
        name='Feedback (PFC Deep -> V1)',
        marker_color='#9400D3'
    ), name='FB Flow')
    
    plotter.set_axes("Temporal Window", "Category", "Granger F-Statistic", "a.u.")
    
    plotter.fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        xaxis=dict(gridcolor="#D3D3D3", linecolor="#000000"),
        yaxis=dict(gridcolor="#D3D3D3", linecolor="#000000"),
        barmode='group'
    )
    
    plotter.save(output_dir, "f038_granger_flow_reversal")
    log.info(f"[f038] Exported flow reversal plot to {output_dir}")
