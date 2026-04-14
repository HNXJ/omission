import os
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

def save_canonical_fig(area, cond, window, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{area}-{cond}-{window}"
    
    # Dummy plot for verification
    fig = go.Figure(data=go.Scatter(x=np.arange(100), y=np.random.randn(100)))
    fig.update_layout(title=f"{area} | {cond} | {window}")
    
    # Save
    fig.write_html(out_dir / f"{filename}.html")
    fig.write_image(out_dir / f"{filename}.svg")
    fig.write_image(out_dir / f"{filename}.png")
    print(f"Saved: {out_dir / filename}")

# Test execution
save_canonical_fig("V1", "rxrr", "d1p2d2", "D:/drive/omission/outputs/oglo-figures/figure-6")
save_canonical_fig("PFC", "rrxr", "d2p3d3", "D:/drive/omission/outputs/oglo-figures/figure-6")
