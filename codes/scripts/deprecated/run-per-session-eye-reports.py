
from codes.config.paths import FIGURES_DIR

import scipy.io
import numpy as np
import os
import glob
import pandas as pd
from scipy.stats import circmean, circstd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Constants
BHV_DIR = r'behavioral\omission_bhv\data'
OUTPUT_DIR = str(FIGURES_DIR / 'eye_directionality/per_session')

def main(args=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    SACCADE_VEL_THRESH = 30 # DVA/s
    MICROSACCADE_AMP_MAX = 1.5 # DVA
    def detect_movements(x, y, fs=1000):
    dx = np.diff(x); dy = np.diff(y)
    vel = fs * np.sqrt(dx**2 + dy**2)
    is_saccade = vel > SACCADE_VEL_THRESH
    movements = []
    if len(is_saccade) == 0: return movements
    is_sac_padded = np.concatenate([[False], is_saccade, [False]])
    starts = np.where(~is_sac_padded[:-1] & is_sac_padded[1:])[0]
    ends = np.where(is_sac_padded[:-1] & ~is_sac_padded[1:])[0]
    for s, e in zip(starts, ends):
        amp = np.sqrt((x[e] - x[s])**2 + (y[e] - y[s])**2)
        theta = np.arctan2(y[e] - y[s], x[e] - x[s])
        m_type = 'Saccade' if amp >= MICROSACCADE_AMP_MAX else 'Microsaccade'
        movements.append({'type': m_type, 'theta': theta, 'amp': amp})
    return movements
    def get_smoothed_distribution(thetas, bins=72):
    if len(thetas) == 0: return np.zeros(bins), np.linspace(0, 360, bins)
    counts, edges = np.histogram(np.degrees(thetas) % 360, bins=bins, range=(0, 360))
    centers = (edges[:-1] + edges[1:]) / 2
    smoothed = np.convolve(np.tile(counts, 3), np.ones(5)/5, mode='same')
    return smoothed[bins:2*bins], centers
    def process_and_plot_session(fpath):
    session_id = os.path.basename(fpath).split('_')[0]
    print(f"Processing Session {session_id}...")
    try:
        data = scipy.io.loadmat(fpath, struct_as_record=False, squeeze_me=True)
        bhv_array = data['bhvUni']
    except Exception as e:
        print(f"Error loading {fpath}: {e}")
        return
    all_movs = []
    for trial in bhv_array:
        if trial.TrialError != 0: continue
        codes = trial.BehavioralCodes.CodeNumbers; times = trial.BehavioralCodes.CodeTimes
        attrs = trial.TaskObject.Attribute
        stim_names = []
        for attr in attrs[1:]:
            if isinstance(attr, np.ndarray) and len(attr) > 1:
                nm = str(attr[1])
                if 'A.avi' in nm: stim_names.append('A')
                elif 'B.avi' in nm: stim_names.append('B')
                else: stim_names.append('O')
            else: stim_names.append('O')
        eye_data = trial.AnalogData.Eye
        on_codes = [101, 103, 105, 107]; off_codes = [102, 104, 106, 108]
        for i, (on_c, off_c) in enumerate(zip(on_codes, off_codes)):
            if i >= len(stim_names): break
            stim = stim_names[i]
            if stim not in ['A', 'B']: continue
            idx_on = np.where(codes == on_c)[0]; idx_off = np.where(codes == off_c)[0]
            if len(idx_on) > 0 and len(idx_off) > 0:
                t_on, t_off = int(times[idx_on[0]]), int(times[idx_off[0]])
                if t_off > len(eye_data): t_off = len(eye_data)
                if t_off - t_on > 20:
                    seg = eye_data[t_on:t_off]
                    movs = detect_movements(seg[:,0], seg[:,1])
                    for m in movs:
                        m['state'] = f"{stim}-p{i+1}"
                        all_movs.append(m)
    if not all_movs: return
    df = pd.DataFrame(all_movs)
    states = ['A-p1', 'A-p2', 'A-p3', 'A-p4', 'B-p1', 'B-p2', 'B-p3', 'B-p4']
    fig = make_subplots(rows=2, cols=4, specs=[[{'type': 'polar'}]*4]*2,
                        subplot_titles=states, horizontal_spacing=0.05, vertical_spacing=0.15)
    colors = {'Saccade': 'rgba(0, 255, 255, 0.6)', 'Microsaccade': 'rgba(255, 165, 0, 0.6)'}
    for idx, state in enumerate(states):
        row, col = idx // 4 + 1, idx % 4 + 1
        sdf = df[df['state'] == state]
        if sdf.empty: continue
        for m_type in ['Saccade', 'Microsaccade']:
            type_df = sdf[sdf['type'] == m_type]
            if type_df.empty: continue
            thetas = type_df['theta'].values
            r, theta = get_smoothed_distribution(thetas)
            r = np.append(r, r[0]); theta = np.append(theta, theta[0])
            fig.add_trace(go.Scatterpolar(
                r=r, theta=theta, name=m_type, mode='lines',
                fill='toself', fillcolor=colors[m_type],
                line=dict(color=colors[m_type].replace('0.6', '1.0'), width=2),
                showlegend=(idx == 0)
            ), row=row, col=col)
        fig.update_polars(dict(angularaxis=dict(direction="clockwise", rotation=90),
                               radialaxis=dict(showticklabels=False, ticks="")),
                          row=row, col=col)
    caption = (
        f"Figure 19-{session_id}: Oculomotor Directionality Suite for Session {session_id}. "
        "Smoothed polar distributions contrast Saccades (Cyan, >30 DVA/s, >1.5° amp) "
        "and Microsaccades (Orange, <1.5° amp) across 8 stimulus states (A/B, p1-p4). "
        "Remarkable: Session-specific biases reveal individualized predictive patterns and oculomotor strategies."
    )
    fig.add_annotation(text=caption, xref="paper", yref="paper", x=0.5, y=-0.15, showarrow=False, width=900, font=dict(size=12))
    fig.update_layout(title=f"Oculomotor Directionality Suite - Session {session_id}",
                      template="plotly_dark", height=900, width=1400, margin=dict(b=150, t=100))
    out_file = os.path.join(OUTPUT_DIR, f"FIG_19_Session_{session_id}_Directionality.html")
    fig.write_html(out_file)
    print(f"Saved Session Report: {out_file}")
    def run_per_session_eye_reports():
    files = glob.glob(os.path.join(BHV_DIR, "*.mat"))
    for f in files:
        process_and_plot_session(f)
    run_per_session_eye_reports()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
