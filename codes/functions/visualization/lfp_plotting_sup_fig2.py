"""
lfp_plotting_sup_fig2.py: Plotting functions for Supplemental Figure 2.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from codes.functions.visualization.lfp_plotting_utils import add_mean_sem_trace, set_global_layout

def plot_panel_a(panel_a_data: pd.DataFrame, output_dir: Path):
    """
    Plots Panel A: Correlation Spectrum for each area.
    """
    areas = panel_a_data['area'].unique()
    if len(areas) == 0:
        print("No data for Panel A.")
        return
        
    fig = make_subplots(
        rows=1, cols=len(areas),
        subplot_titles=areas
    )

    for i, area in enumerate(areas):
        area_data = panel_a_data[panel_a_data['area'] == area]
        
        add_mean_sem_trace(
            fig,
            x=area_data['freqs'],
            y=area_data['mean'],
            sem=area_data['sem'],
            row=1, col=i + 1,
            color='black',
            name=f"{area} Corr"
        )
        fig.update_xaxes(title_text="Frequency (Hz)", row=1, col=i + 1)
        if i == 0:
            fig.update_yaxes(title_text="Spearman Correlation", row=1, col=i + 1)
        
    set_global_layout(fig, "MUA-LFP Power Correlation Spectrum")

    output_file = output_dir / "panel_a_correlation_spectrum"
    fig.write_html(f"{output_file}.html")
    fig.write_image(f"{output_file}.svg")
    fig.write_image(f"{output_file}.png")

    print(f"Panel A saved to {output_dir}")

def plot_panels_b_e(panels_b_e_data: pd.DataFrame, output_dir: Path):
    """
    Plots Panels B-E: Layer + Band Split Bar Plots for each area.
    """
    areas = panels_b_e_data.index.get_level_values('area').unique()
    if len(areas) == 0:
        print("No data for Panels B-E.")
        return
        
    fig = make_subplots(
        rows=1, cols=len(areas),
        subplot_titles=areas,
        shared_yaxes=True
    )

    bands = ['theta', 'alpha', 'beta', 'gamma']
    layer_colors = {'superficial': 'orange', 'deep': 'blue'}

    for i, area in enumerate(areas):
        area_data = panels_b_e_data.loc[area]
        
        for layer in ['superficial', 'deep']:
            if ('mean', layer) not in area_data.columns: continue
            
            means = area_data[('mean', layer)]
            sems = area_data[('sem', layer)]
            
            fig.add_trace(go.Bar(
                x=bands,
                y=means,
                error_y=dict(type='data', array=sems, visible=True),
                name=f"{area} {layer}",
                marker_color=layer_colors[layer]
            ), row=1, col=i + 1)
            
        fig.update_xaxes(title_text="Frequency Band", row=1, col=i + 1)
        if i == 0:
            fig.update_yaxes(title_text="Mean Spearman Correlation", row=1, col=i + 1)

    set_global_layout(fig, "MUA-LFP Correlation by Layer and Band")
    fig.update_layout(barmode='group')

    output_file = output_dir / "panels_b_e_layer_band_corr"
    fig.write_html(f"{output_file}.html")
    fig.write_image(f"{output_file}.svg")
    fig.write_image(f"{output_file}.png")

    print(f"Panels B-E saved to {output_dir}")

def plot_supplemental_figure_2(per_electrode_results: List[Dict[str, Any]], output_dir: Path):
    """
    Main function to generate and save Supplemental Figure 2.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # --- Data Aggregation ---
    # Convert list of dicts to a DataFrame for easier manipulation
    results_df = pd.DataFrame(per_electrode_results)
    
    if results_df.empty:
        print("No results to plot.")
        return

    # --- Panel A Aggregation ---
    # Explode the correlation spectrum and freqs to long format
    results_df_long = results_df.explode(['correlation_spectrum', 'freqs'])
    results_df_long['correlation_spectrum'] = pd.to_numeric(results_df_long['correlation_spectrum'])
    results_df_long['freqs'] = pd.to_numeric(results_df_long['freqs'])

    # Group by area and frequency to get mean and SEM
    panel_a_agg = results_df_long.groupby(['area', 'freqs'])['correlation_spectrum'].agg(['mean', 'sem']).reset_index()

    # --- Panels B-E Aggregation ---
    bands = {
        'theta': (2, 6),
        'alpha': (8, 14),
        'beta': (15, 30),
        'gamma': (40, 90)
    }
    
    # Assign band to each row
    def get_band(freq):
        for band_name, (low, high) in bands.items():
            if low <= freq <= high:
                return band_name
        return None
    results_df_long['band'] = results_df_long['freqs'].apply(get_band)
    
    # Drop rows without a band
    band_results = results_df_long.dropna(subset=['band'])
    
    # Average correlation within each band for each electrode
    electrode_band_agg = band_results.groupby(['session_id', 'electrode_id', 'area', 'layer', 'band'])['correlation_spectrum'].mean().reset_index()
    
    # Now group by area, layer, and band for plotting
    panels_b_e_agg = electrode_band_agg.groupby(['area', 'layer', 'band'])['correlation_spectrum'].agg(['mean', 'sem']).reset_index()

    # Pivot for easier access
    panels_b_e_pivot = panels_b_e_agg.pivot_table(
        index=['area', 'band'], 
        columns='layer', 
        values=['mean', 'sem']
    ).fillna(0)
    
    # TODO: Perform statistical tests between layers

    aggregated_results = {
        "panel_a": panel_a_agg,
        "panels_b_e": panels_b_e_pivot
    }
    
    # --- Plotting ---
    plot_panel_a(aggregated_results["panel_a"], output_dir)
    plot_panels_b_e(aggregated_results["panels_b_e"], output_dir)
    
    print(f"Supplemental Figure 2 saved in {output_dir}")
