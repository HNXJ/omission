import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from pathlib import Path
from src.analysis.profile_search import ProfileSearcher
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def run_f048():
    """
    Standard runner for Figure 48: Profile Analysis.
    """
    print(f"""[action] Initializing Figure 48: Profile Analysis...""")
    loader = DataLoader()
    searcher = ProfileSearcher(loader=loader)
    
    # 1. SEARCH
    print(f"""[action] Searching neurons for repetition profiles...""")
    neuron_df = searcher.search_neurons()
    print(f"""[action] Searching LFP bands for repetition profiles...""")
    lfp_df = searcher.search_lfp_bands()
    
    combined_df = pd.concat([neuron_df, lfp_df])
    
    # 2. POPULATION VISUALIZATION (Histogram of Ratios)
    print(f"""[action] Generating population statistics figures...""")
    fig_pop = make_subplots(rows=1, cols=2, subplot_titles=("Stimulus (x/y)", "Delay (z/w)"))
    
    for area in loader.CANONICAL_AREAS:
        area_data = neuron_df[neuron_df['area'] == area]
        if area_data.empty: continue
        
        # Stimulus Ratio
        fig_pop.add_trace(go.Box(
            y=area_data['ratio_xy'],
            name=area,
            marker_color='royalblue',
            showlegend=False
        ), row=1, col=1)
        
        # Delay Ratio
        fig_pop.add_trace(go.Box(
            y=area_data['ratio_zw'],
            name=area,
            marker_color='indianred',
            showlegend=False
        ), row=1, col=2)
    
    fig_pop.update_layout(
        title="Distribution of Repetition Ratios across Areas (Stimulus vs Delay)",
        template="plotly_white",
        yaxis=dict(range=[0, 5]),
        yaxis2=dict(range=[0, 5])
    )
    
    # 3. SCATTER COMPARISON (x/y vs z/w)
    print(f"""[action] Generating scatter comparison...""")
    fig_scatter = go.Figure()
    for area in loader.CANONICAL_AREAS:
        area_data = neuron_df[neuron_df['area'] == area]
        if area_data.empty: continue
        fig_scatter.add_trace(go.Scatter(
            x=area_data['ratio_xy'],
            y=area_data['ratio_zw'],
            mode='markers',
            name=area,
            text=area_data['id'],
            marker=dict(size=6, opacity=0.6)
        ))
    
    fig_scatter.update_layout(
        title="Repetition Scaling: Stimulus (x/y) vs Delay (z/w)",
        xaxis_title="Stimulus Ratio (p3/p1)",
        yaxis_title="Delay Ratio (d3/d1)",
        template="plotly_white",
        xaxis=dict(range=[0, 3]),
        yaxis=dict(range=[0, 3])
    )
    fig_scatter.add_shape(type="line", x0=0, y0=0, x1=3, y1=3, line=dict(dash="dash", color="black"))
    
    # 4. SAMPLE IDENTIFICATION
    print(f"""[action] Identifying extreme units for trace plotting...""")
    top_suppressor = neuron_df.nsmallest(1, 'ratio_xy').iloc[0]
    top_facilitator = neuron_df.nlargest(1, 'ratio_xy').iloc[0]
    
    # Create output directory
    output_dir = loader.get_output_dir("f048_profile_analysis")
    
    # Save statistics figure
    fig_pop.write_html(str(output_dir / "index.html"))
    fig_scatter.write_html(str(output_dir / "scatter_comparison.html"))
    
    # Save CSVs for the requested filters
    filters = {
        "x_gt_y": neuron_df[neuron_df['x'] > neuron_df['y']],
        "x_gt_1.5y": neuron_df[neuron_df['x'] > 1.5 * neuron_df['y']],
        "x_gt_2.0y": neuron_df[neuron_df['x'] > 2.0 * neuron_df['y']],
        "x_lt_y": neuron_df[neuron_df['x'] < neuron_df['y']],
        "x_lt_0.5y": neuron_df[neuron_df['x'] < 0.5 * neuron_df['y']]
    }
    
    for name, f_df in filters.items():
        f_df.to_csv(output_dir / f"profile_{name}.csv", index=False)
        print(f"""[action] Saved {len(f_df)} units to {name}.csv""")

    print(f"""[action] Figure 48 generation complete.""")

if __name__ == "__main__":
    run_f048()
