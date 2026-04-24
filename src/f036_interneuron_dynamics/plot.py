# beta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

def plot_interneuron_dynamics(results, output_dir="output"):
    """
    Plots FS vs RS dynamics across the hierarchy.
    """
    areas = list(results['metadata']['counts'].keys())
    fig = make_subplots(
        rows=1, cols=len(areas), 
        subplot_titles=[f"Area: {a}" for a in areas],
        shared_yaxes=True
    )
    
    colors = {'FS': '#9400D3', 'RS': '#CFB87C'} # Dark Purple / Golden
    
    for i, area in enumerate(areas):
        for u_type in ['FS', 'RS']:
            data = results.get(u_type, {}).get(area)
            if data is None:
                continue
            
            avg = data['avg']
            sem = data['sem']
            t = np.arange(len(avg))
            
            # Main trace
            fig.add_trace(
                go.Scatter(
                    x=t, y=avg, 
                    name=f"{u_type} ({results['metadata']['counts'][area][u_type]})",
                    line=dict(color=colors[u_type], width=2.5),
                    showlegend=(i==0)
                ),
                row=1, col=i+1
            )
            
            # SEM Shading
            fig.add_trace(
                go.Scatter(
                    x=np.concatenate([t, t[::-1]]),
                    y=np.concatenate([avg + sem, (avg - sem)[::-1]]),
                    fill='toself',
                    fillcolor=colors[u_type],
                    opacity=0.2,
                    line=dict(color='rgba(255,255,255,0)'),
                    hoverinfo="skip",
                    showlegend=False
                ),
                row=1, col=i+1
            )
        
        # Add stim markers
        for stim_t in [1000, 2031, 3062, 4093]:
            fig.add_vline(x=stim_t, line=dict(color="rgba(0,0,0,0.3)", dash="dash", width=1), row=1, col=i+1)

    fig.update_layout(
        title="Putative Interneuron (FS) vs Pyramidal (RS) Dynamics",
        template="plotly_white",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Outfit, sans-serif", color="#333"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=100, b=50, l=50, r=50),
        modebar_add=['toImage']
    )
    
    fig.update_xaxes(title_text="Time (ms)", gridcolor="#eee", linecolor="black")
    fig.update_yaxes(title_text="Firing Rate (Hz)", gridcolor="#eee", linecolor="black")
    
    out_path = os.path.join(output_dir, "f036_interneuron_dynamics.html")
    fig.write_html(out_path)
    print(f"[action] Saved interneuron dynamics plot to {out_path}")
