# f039 — Spike-Field Coherence Visualization (Madelane Golden Dark)
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log


# Madelane Golden Dark palette
GOLD = "#CFB87C"
PURPLE = "#9400D3"
AREA_COLORS = {
    "V1":  "#CFB87C",
    "V4":  "#FF6B6B",
    "FEF": "#4ECDC4",
    "PFC": "#9400D3",
    "MT":  "#45B7D1",
    "V2":  "#96CEB4",
}


def plot_ppc_band_comparison(results_df, output_dir: str):
    """
    Plots PPC baseline vs omission across frequency bands, per area pair.
    
    Input:
        results_df — DataFrame with columns: area_src, area_tgt, condition,
                     band, ppc_baseline_mean, ppc_baseline_sem,
                     ppc_omission_mean, ppc_omission_sem, n_pairs.
        output_dir — str, path for HTML output.
    
    Output:
        Interactive HTML figure saved to output_dir.
    """
    print(f"""[action] Generating PPC band comparison figure""")
    
    bands = ["Theta", "Alpha", "Beta", "Low Gamma", "High Gamma"]
    conditions = results_df['condition'].unique()
    
    plotter = OmissionPlotter(
        title="Figure f039: Spike-Field Coherence (PPC)",
        x_label="Frequency Band",
        y_label="PPC",
        subtitle="Pairwise Phase Consistency: Baseline vs Omission across Frequency Bands",
        y_unit="a.u."
    )
    
    for cond in conditions:
        cdf = results_df[results_df['condition'] == cond]
        
        # Baseline trace
        base_means = []
        base_sems = []
        omit_means = []
        omit_sems = []
        band_labels = []
        
        for band in bands:
            bdf = cdf[cdf['band'] == band]
            if len(bdf) > 0:
                base_means.append(bdf['ppc_baseline_mean'].values[0])
                base_sems.append(bdf['ppc_baseline_sem'].values[0])
                omit_means.append(bdf['ppc_omission_mean'].values[0])
                omit_sems.append(bdf['ppc_omission_sem'].values[0])
                band_labels.append(band)
        
        if not band_labels:
            print(f"""[warning] No data for condition {cond}""")
            continue
        
        base_means = np.array(base_means)
        base_sems = np.array(base_sems)
        omit_means = np.array(omit_means)
        omit_sems = np.array(omit_sems)
        
        # Baseline trace with SEM shading
        plotter.add_shaded_error_bar(
            x=band_labels, mean=base_means, error_upper=base_sems,
            name=f"{cond} Baseline", color=GOLD
        )
        
        # Omission trace with SEM shading
        plotter.add_shaded_error_bar(
            x=band_labels, mean=omit_means, error_upper=omit_sems,
            name=f"{cond} Omission", color=PURPLE
        )
    
    plotter.add_yline(0, "No Phase-Locking", color="gray", dash="dot")
    plotter.save(output_dir, "f039_spike_field_coherence")
    print(f"""[action] PPC band comparison figure saved""")


def plot_ppc_per_area(results_df, output_dir: str):
    """
    Plots per-area PPC spectra: one subplot per area, showing baseline vs omission.
    
    Input:  results_df — aggregated PPC results.
    Output: HTML figure saved.
    """
    print(f"""[action] Generating per-area PPC figure""")
    
    areas = results_df['area_src'].unique()
    bands = ["Theta", "Alpha", "Beta", "Low Gamma", "High Gamma"]
    
    n_areas = len(areas)
    fig = make_subplots(
        rows=1, cols=n_areas,
        subplot_titles=[f"{a}" for a in areas],
        shared_yaxes=True
    )
    
    for i, area in enumerate(areas):
        adf = results_df[results_df['area_src'] == area]
        color = AREA_COLORS.get(area, "#888888")
        
        base_vals = []
        omit_vals = []
        
        for band in bands:
            bdf = adf[adf['band'] == band]
            if len(bdf) > 0:
                base_vals.append(bdf['ppc_baseline_mean'].mean())
                omit_vals.append(bdf['ppc_omission_mean'].mean())
            else:
                base_vals.append(np.nan)
                omit_vals.append(np.nan)
        
        # Baseline
        fig.add_trace(go.Scatter(
            x=bands, y=base_vals, name=f"{area} Baseline",
            line=dict(color=color, width=2, dash="dash"),
            legendgroup=area, showlegend=True
        ), row=1, col=i+1)
        
        # Omission
        fig.add_trace(go.Scatter(
            x=bands, y=omit_vals, name=f"{area} Omission",
            line=dict(color=color, width=3),
            legendgroup=area, showlegend=True
        ), row=1, col=i+1)
    
    fig.update_layout(
        title=dict(
            text="<b>Figure f039: Per-Area Spike-Field Coherence</b><br>"
                 "<sup>Dashed=Baseline, Solid=Omission</sup>",
            x=0.5, xanchor='center', font=dict(size=16)
        ),
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        xaxis_title="Frequency Band",
        yaxis_title="PPC",
        margin=dict(l=80, r=60, t=120, b=80),
        modebar_add=['toImage'],
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.2,
            xanchor="center", x=0.5,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#000000", borderwidth=1
        )
    )
    
    from pathlib import Path
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(out / "f039_ppc_per_area.html"), include_plotlyjs="cdn")
    print(f"""[action] Per-area PPC figure saved""")
    log.progress(f"Saved f039_ppc_per_area.html")
