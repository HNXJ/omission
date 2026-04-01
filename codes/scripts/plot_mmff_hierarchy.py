
import numpy as np
import plotly.graph_objects as go
import json
import os

AREA_ORDER = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
CONDITIONS = {
    'RRRR': {'color': 'rgb(139, 69, 19)', 'name': 'Standard (RRRR)'},
    'RXRR': {'color': 'rgb(255, 0, 0)', 'name': 'Omit p2 (RXRR)'},
    'RRXR': {'color': 'rgb(0, 0, 255)', 'name': 'Omit p3 (RRXR)'},
    'RRRX': {'color': 'rgb(0, 128, 0)', 'name': 'Omit p4 (RRRX)'}
}

def plot_mmff_results():
    if not os.path.exists('checkpoints/area_mmff_traces.json'):
        print("Waiting for MMFF traces...")
        return

    with open('checkpoints/area_mmff_traces.json', 'r') as f:
        data = json.load(f)

    # Bins match extraction: np.arange(0, 6000-100, 5)
    time_bins = np.arange(0, 6000 - 100, 5)
    # Relative to p1 onset at 1000ms
    rel_time = time_bins - 1000
    
    # Baseline window: -500 to 0ms (bins 100 to 200 in time_bins)
    base_mask = (rel_time >= -500) & (rel_time <= 0)

    # Event definitions
    EVENTS = {
        "fx": (0, 1000, 'rgba(128,128,128,0.08)'),
        "p1": (1000, 1531, 'rgba(128,128,128,0.12)'),
        "d1": (1531, 2031, 'rgba(128,128,128,0.08)'),
        "p2": (2031, 2562, 'rgba(255,0,0,0.12)'),   # Red for RXRR
        "d2": (2562, 3062, 'rgba(128,128,128,0.08)'),
        "p3": (3062, 3593, 'rgba(0,0,255,0.12)'),   # Blue for RRXR
        "d3": (3593, 4093, 'rgba(128,128,128,0.08)'),
        "p4": (4093, 4624, 'rgba(0,128,0,0.12)'),   # Green for RRRX
        "d4": (4624, 5124, 'rgba(128,128,128,0.08)')
    }

    os.makedirs('figures/final_reports', exist_ok=True)

    # 1. Individual Area Line Plots
    for area in AREA_ORDER:
        if area not in data: continue
        fig = go.Figure()
        
        # Add Event Shades and Labels
        for name, (start, end, color) in EVENTS.items():
            fig.add_vrect(x0=start-1000, x1=end-1000, fillcolor=color, line_width=0, 
                          annotation_text=name, annotation_position="top left")

        for cond, cfg in CONDITIONS.items():
            trace = np.array(data[area][cond])
            if np.all(np.isnan(trace)): continue
            
            # Baselining to 0 during -500-0ms
            baseline = np.nanmean(trace[base_mask])
            trace_aligned = trace - baseline
            
            fig.add_trace(go.Scatter(x=rel_time, y=trace_aligned, mode='lines', 
                                     line=dict(color=cfg['color']), name=cfg['name']))

        fig.update_layout(title=f"Mean-Matched Fano Factor (Churchland 2010): {area}",
                          xaxis_title="Time (ms)", yaxis_title="ΔFano Factor (Baselined)",
                          xaxis_range=[-750, 4124], template="plotly_white")
        fig.write_html(f"figures/final_reports/FIG_03_MMFF_Traces_{area}.html")

    # 2. Hierarchy Bar Plot (Omission Window)
    # Average ΔFano during omission p2, p3, p4
    omission_vals = []
    for area in AREA_ORDER:
        vals = []
        # Omit p2 (RXRR) window: 1031-1562 rel time
        v_p2 = np.nanmean(np.array(data[area]['RXRR'])[(rel_time >= 1031) & (rel_time <= 1562)])
        # Omit p3 (RRXR) window: 2062-2593 rel time
        v_p3 = np.nanmean(np.array(data[area]['RRXR'])[(rel_time >= 2062) & (rel_time <= 2593)])
        # Omit p4 (RRRX) window: 3093-3624 rel time
        v_p4 = np.nanmean(np.array(data[area]['RRRX'])[(rel_time >= 3093) & (rel_time <= 3624)])
        
        avg_om = np.nanmean([v_p2, v_p3, v_p4])
        omission_vals.append(avg_om)

    fig_bar = go.Figure(data=[go.Bar(x=AREA_ORDER, y=omission_vals, marker_color='indianred')])
    fig_bar.update_layout(title="Variability Quenching Hierarchy (MMFF) during Omission",
                          xaxis_title="Brain Area", yaxis_title="ΔFano Factor",
                          template="plotly_white")
    fig_bar.write_html("figures/final_reports/FIG_04A_MMFF_Hierarchy.html")

    print("Saved MMFF-based Figure 3 and 4A to figures/final_reports/")

if __name__ == '__main__':
    plot_mmff_results()
