from codes.config.paths import DATA_DIR, FIGURES_DIR

import numpy as np
import os
import plotly.graph_objects as go
import plotly.io as pio
from run_behavioral_decoding_suite import analyze_session_eye, decode_identity_eye

# Madelane Golden Dark + Violet Theme
GOLD = '#CFB87C'
VIOLET = '#8F00FF'
BLACK = '#000000'
SLATE = '#708090'
WHITE = '#FFFFFF'

def plot_identity_decoding_plotly(scores, session_id):
    """Plots Behavioral Identity Decoding using Plotly."""
    time_bins = np.arange(len(scores)) * 100 - 1000 # -1000 to 5000ms
    
    fig = go.Figure()
    
    # Accuracy Trace
    fig.add_trace(go.Scatter(
        x=time_bins, 
        y=scores, 
        mode='lines',
        line=dict(color=GOLD, width=3),
        name='Identity A vs B'
    ))
    
    # Chance Level
    fig.add_trace(go.Scatter(
        x=time_bins, 
        y=[0.5]*len(time_bins), 
        mode='lines',
        line=dict(color=SLATE, dash='dash'),
        name='Chance (0.5)'
    ))
    
    # P1 Onset
    fig.add_vline(x=0, line_dash="dash", line_color=WHITE, annotation_text="P1 Onset")
    
    # Event Indicators (P2, P3, P4)
    for i in range(1, 5):
        fig.add_vline(x=i*531, line_dash="dot", line_color=SLATE, opacity=0.5)

    fig.update_layout(
        template='plotly_dark',
        title=f'Behavioral Identity Decoding (Eye/Pupil): Session {session_id}',
        xaxis_title='Time (ms)',
        yaxis_title='Decoding Accuracy',
        paper_bgcolor=BLACK,
        plot_bgcolor=BLACK,
        font_color=WHITE,
        yaxis_range=[0.3, 1.0] # Standard decoding range
    )
    
    html_path = os.path.join(str(FIGURES_DIR), f"FIG_Eye_Identity_Decoding_{session_id}.html")
    svg_path = os.path.join(str(FIGURES_DIR), f"FIG_Eye_Identity_Decoding_{session_id}.svg")
    
    fig.write_html(html_path)
    fig.write_image(svg_path)
    print(f"Saved Identity Decoding: {html_path}, {svg_path}")


def main(args=None):
    data_dir = DATA_DIR
    session_id = "230629"
    results = analyze_session_eye(data_dir, session_id)
    identity_scores = decode_identity_eye(results)
    if identity_scores is not None:
        plot_identity_decoding_plotly(identity_scores, session_id)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
