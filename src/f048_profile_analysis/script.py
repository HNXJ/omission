import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from pathlib import Path
from src.analysis.profile_search import ProfileSearcher, get_band_power
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def plot_psth_exemplar(loader, unit_id, family, om_conds, ctrl_conds, onset_ms, output_path):
    """Plots Omission vs Control PSTH for a single unit."""
    print(f"""[action] Plotting PSTH exemplar for {unit_id} ({family})...""")
    
    # Time axis (ms relative to p1 onset)
    # Load full 4s stim block
    time = np.linspace(-1000, 3000, 4000) # Assuming 4s total in these npy files
    
    fig = go.Figure()
    
    # 1. Load Omission Trace
    om_traces = []
    for cond in om_conds:
        spk = loader.load_unit_spikes(unit_id, condition=cond)
        if spk is not None:
            # Average across trials
            om_traces.append(np.mean(spk, axis=0) * 1000)
    
    if om_traces:
        avg_om = np.mean(om_traces, axis=0)
        fig.add_trace(go.Scatter(x=time, y=avg_om, name='Omission Trial', line=dict(color='red')))
        
    # 2. Load Control Trace
    ctrl_traces = []
    for cond in ctrl_conds:
        spk = loader.load_unit_spikes(unit_id, condition=cond)
        if spk is not None:
            ctrl_traces.append(np.mean(spk, axis=0) * 1000)
            
    if ctrl_traces:
        avg_ctrl = np.mean(ctrl_traces, axis=0)
        fig.add_trace(go.Scatter(x=time, y=avg_ctrl, name='Matched Control', line=dict(color='black', dash='dash')))

    # Layout
    fig.add_vline(x=onset_ms, line_width=2, line_dash="dash", line_color="green", annotation_text="Omission Onset")
    fig.update_layout(
        title=f"Unit Omission Response: {unit_id} ({family})",
        xaxis_title="Time (ms from p1 onset)",
        yaxis_title="Firing Rate (Hz)",
        template="plotly_white"
    )
    fig.write_html(str(output_path))

def run_f048():
    """
    Standard runner for Figure 48: Omission-Grounded Profile Analysis.
    """
    print(f"""[action] Initializing Figure 48: Omission Profiles...""")
    loader = DataLoader()
    searcher = ProfileSearcher(loader=loader)
    
    # 1. SEARCH BRANCHES
    print(f"""[action] Searching SPK omission profiles...""")
    spk_df = searcher.search_omission_profiles(mode="spk")
    
    print(f"""[action] Searching LFP omission profiles...""")
    lfp_df = searcher.search_omission_profiles(mode="lfp")
    
    # 2. DESCRIPTIVE AUXILIARY (Repetition Scaling)
    print(f"""[action] Running auxiliary repetition scaling search...""")
    rep_df = searcher.search_repetition_profiles(mode="spk")
    
    # 3. OUTPUT GENERATION
    output_dir = loader.get_output_dir("f048_profile_analysis")
    
    # Save Raw Results
    spk_df.to_csv(output_dir / "omission_profiles_spk.csv", index=False)
    lfp_df.to_csv(output_dir / "omission_profiles_lfp.csv", index=False)
    rep_df.to_csv(output_dir / "aux_repetition_scaling.csv", index=False)
    
    # 4. SUMMARY QA TABLE
    print(f"""[action] Generating QA Summary Table...""")
    qa_rows = []
    for family in ['p2', 'p3', 'p4']:
        f_spk = spk_df[spk_df['family'] == family]
        f_lfp = lfp_df[lfp_df['family'] == family]
        qa_rows.append({
            'Family': family,
            'Total Units': len(f_spk),
            'Om-Positive Units': f_spk['is_omission_positive'].sum(),
            'LFP Gamma Suppression': (f_lfp[f_lfp['band']=='Gamma']['ratio'] < 0.8).sum()
        })
    qa_df = pd.DataFrame(qa_rows)
    qa_df.to_csv(output_dir / "qa_summary_table.csv", index=False)
    print(qa_df)

    # 5. EXEMPLAR PLOTS
    print(f"""[action] Identifying top omission-positive SPK units...""")
    if not spk_df.empty:
        # Find top overall omission responder
        top_unit = spk_df.sort_values('effect_size', ascending=False).iloc[0]
        uid = top_unit['id']
        fam = top_unit['family']
        cfg = ProfileSearcher.OMISSION_FAMILIES[fam]
        
        plot_psth_exemplar(
            loader, uid, fam, 
            cfg['omission'], cfg['control'], cfg['onset'],
            output_dir / f"exemplar_psth_{uid}.html"
        )

    # 6. LFP SUMMARY FIGURE
    print(f"""[action] Generating LFP Omission Ratio Summary...""")
    fig_lfp = go.Figure()
    for band in ['Theta', 'Alpha', 'Beta', 'Gamma']:
        b_data = lfp_df[lfp_df['band'] == band]
        if b_data.empty: continue
        fig_lfp.add_trace(go.Box(y=b_data['ratio'], name=band))
    
    fig_lfp.update_layout(
        title="Omission/Control Power Ratio by LFP Band",
        yaxis_title="Ratio (Om/Ctrl)",
        template="plotly_white"
    )
    fig_lfp.write_html(str(output_dir / "index.html")) # Main dashboard landing for f048

    print(f"""[action] Figure 48 generation complete.""")

if __name__ == "__main__":
    run_f048()
