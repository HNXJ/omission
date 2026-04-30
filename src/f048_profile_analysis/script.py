import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from pathlib import Path
from src.analysis.profile_search import ProfileSearcher
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def plot_repetition_exemplar(loader, unit_id, family, cond, onset_ms, p1_val, p3_val, output_path):
    """Plots validated repetition exemplar with highlighted windows."""
    print(f"""[action] Plotting Repetition Exemplar for {unit_id} ({family})...""")
    time = np.linspace(-1000, 3000, 4000)
    
    spk = loader.load_unit_spikes(unit_id, condition=cond)
    if spk is None: return
    trace = np.mean(spk, axis=0) * 1000
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time, y=trace, name=cond, line=dict(color='royalblue')))
    
    # Highlight p1 and p3 windows
    fig.add_vrect(x0=0, x1=515, fillcolor="rgba(0,255,0,0.1)", layer="below", line_width=0, annotation_text="p1")
    fig.add_vrect(x0=2062, x1=2577, fillcolor="rgba(255,0,0,0.1)", layer="below", line_width=0, annotation_text="p3")
    
    fig.update_layout(
        title=f"Repetition Profile: {unit_id} ({family}) | p1={p1_val:.1f}Hz, p3={p3_val:.1f}Hz, Ratio={p3_val/p1_val if p1_val>0 else 0:.2f}",
        xaxis_title="Time (ms from p1 onset)",
        yaxis_title="Firing Rate (Hz)",
        template="plotly_white"
    )
    fig.write_html(str(output_path))

def run_f048():
    """
    Standard runner for Figure 48: Repetition QA & Omission Profiles.
    """
    print(f"""[action] Initializing Figure 48 QA Cycle...""")
    loader = DataLoader()
    searcher = ProfileSearcher(loader=loader)
    
    # 1. SEARCH
    spk_df = searcher.search_omission_profiles(mode="spk")
    rep_spk_df = searcher.search_repetition_profiles(mode="spk")
    
    output_dir = loader.get_output_dir("f048_profile_analysis")
    
    # 2. AUDIT TABLE (Compact anchor)
    print(f"""[action] Building Repetition Audit Table...""")
    audit_rows = []
    for (fam, area), group in rep_spk_df.groupby(['family', 'area']):
        audit_rows.append({
            'family': fam, 'area': area, 'modality': 'spk',
            'total_n': len(group),
            'gt_1': group['gt_1'].sum(),
            'gt_1p5': group['gt_1p5'].sum(),
            'gt_2': group['gt_2'].sum(),
            'lt_1': group['lt_1'].sum(),
            'lt_0p67': group['lt_0p67'].sum(),
            'lt_0p5': group['lt_0p5'].sum(),
            'median_ratio': group['p3_over_p1'].median(),
            'median_diff': group['p3_minus_p1'].median()
        })
    audit_df = pd.DataFrame(audit_rows)
    audit_df.to_csv(output_dir / "repetition_audit_table.csv", index=False)

    # 3. DELAY SCALING SUMMARY
    print(f"""[action] Generating Delay Scaling Summary...""")
    delay_rows = []
    for cond in ["AXAB", "BXBA", "RXRR"]:
        f_df = rep_spk_df[rep_spk_df['family'] == cond]
        delay_rows.append({
            'Family': cond,
            'n(d3>d1)': f_df['d_gt_1'].sum(),
            'n(d3>2*d1)': f_df['d_gt_2'].sum(),
            'n(d3<0.5*d1)': f_df['d_lt_0p5'].sum()
        })
    pd.DataFrame(delay_rows).to_csv(output_dir / "delay_scaling_summary.csv", index=False)

    # 4. EXAMPLES (Validated by Activity Guard)
    print(f"""[action] Exporting validated repetition exemplars...""")
    for fam in ["AXAB", "BXBA", "RXRR"]:
        fam_df = rep_spk_df[rep_spk_df['family'] == fam]
        # Top Facilitators
        tops = fam_df.sort_values('p3_over_p1', ascending=False).head(2)
        # Top Suppressors
        bottoms = fam_df.sort_values('p3_over_p1', ascending=True).head(2)
        
        for i, row in enumerate(pd.concat([tops, bottoms]).iterrows()):
            r = row[1]
            cat = "facilitator" if i < 2 else "suppressor"
            plot_repetition_exemplar(
                loader, r['id'], fam, fam, 0, r['p1_value'], r['p3_value'],
                output_dir / f"repetition_exemplar_{fam}_{cat}_{r['id']}.html"
            )

    print(f"""[action] Figure 48 generation complete.""")

if __name__ == "__main__":
    run_f048()
