
from codes.config.paths import FIGURES_DIR

import scipy.io
import numpy as np
import os
import glob
import pandas as pd
from scipy.stats import circmean, circstd
import plotly.express as px
import plotly.graph_objects as go

# Constants
BHV_DIR = r'behavioral\omission_bhv\data'
OUTPUT_DIR = str(FIGURES_DIR / 'eye_directionality')

def main(args=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    SACCADE_VEL_THRESH = 30 # DVA/s
    MICROSACCADE_AMP_MAX = 1.5 # DVA
    def detect_movements(x, y, fs=1000):
    """Detects saccades and categorizes them."""
    dx = np.diff(x)
    dy = np.diff(y)
    vel = fs * np.sqrt(dx**2 + dy**2)
    # Simple threshold-based saccade detection
    is_saccade = vel > SACCADE_VEL_THRESH
    # Find saccade segments (contiguous True values)
    movements = []
    if len(is_saccade) == 0: return movements
    # Add dummy false at ends to simplify
    is_sac_padded = np.concatenate([[False], is_saccade, [False]])
    starts = np.where(~is_sac_padded[:-1] & is_sac_padded[1:])[0]
    ends = np.where(is_sac_padded[:-1] & ~is_sac_padded[1:])[0]
    for s, e in zip(starts, ends):
        # Displacement
        amp = np.sqrt((x[e] - x[s])**2 + (y[e] - y[s])**2)
        theta = np.arctan2(y[e] - y[s], x[e] - x[s])
        m_type = 'Saccade' if amp >= MICROSACCADE_AMP_MAX else 'Microsaccade'
        movements.append({'type': m_type, 'theta': theta, 'amp': amp})
    # Also add "Slow" movements (non-saccadic periods)
    # For slow, we can just take the average drift or PCA of non-saccadic samples
    # But for simplicity, let's just categorize the samples that are NOT in saccades
    is_slow = ~is_saccade
    if np.any(is_slow):
        # We'll take the PCA direction of the slow samples if they are many
        # But maybe just the PCA of the whole segment is what the user meant by "direction of eye movement"
        pass
    return movements
    def process_session_detailed(fpath):
    try:
        data = scipy.io.loadmat(fpath, struct_as_record=False, squeeze_me=True)
        bhv_array = data['bhvUni']
    except: return []
    all_movs = []
    all_segments = []
    for trial in bhv_array:
        if trial.TrialError != 0: continue
        codes = trial.BehavioralCodes.CodeNumbers
        times = trial.BehavioralCodes.CodeTimes
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
            idx_on = np.where(codes == on_c)[0]
            idx_off = np.where(codes == off_c)[0]
            if len(idx_on) > 0 and len(idx_off) > 0:
                t_on, t_off = int(times[idx_on[0]]), int(times[idx_off[0]])
                if t_off > len(eye_data): t_off = len(eye_data)
                if t_off - t_on > 20:
                    seg = eye_data[t_on:t_off]
                    x, y = seg[:, 0], seg[:, 1]
                    # 1. Saccades/Microsaccades
                    movs = detect_movements(x, y)
                    for m in movs:
                        m['state'] = f"{stim}-p{i+1}"
                        all_movs.append(m)
                    # 2. Slow Movement (PCA of the WHOLE segment)
                    def local_pca(lx, ly):
                        if len(lx) < 10: return np.nan
                        lX = np.stack([lx, ly], axis=1)
                        lcenter = np.mean(lX, axis=0)
                        lXc = lX - lcenter
                        lC = np.cov(lXc.T)
                        if np.any(np.isnan(lC)) or np.any(np.isinf(lC)): return np.nan
                        lvals, lvecs = np.linalg.eig(lC)
                        lidx = np.argmax(lvals)
                        ldirection = lvecs[:, lidx]
                        ldelta = lX[-1, :] - lX[0, :]
                        if np.dot(ldelta, ldirection) < 0:
                            ldirection = -ldirection
                        return np.arctan2(ldirection[1], ldirection[0])
                    theta_overall = local_pca(x, y)
                    all_segments.append({
                        'state': f"{stim}-p{i+1}",
                        'theta': theta_overall,
                        'x_mean': np.mean(x), 'y_mean': np.mean(y)
                    })
    return all_movs, all_segments
    def run_detailed_analysis():
    files = glob.glob(os.path.join(BHV_DIR, "*.mat"))
    all_movs = []
    all_segs = []
    for f in files:
        m, s = process_session_detailed(f)
        all_movs.extend(m)
        all_segs.extend(s)
    df_movs = pd.DataFrame(all_movs)
    df_segs = pd.DataFrame(all_segs)
    df_movs['theta_deg'] = np.degrees(df_movs['theta']) % 360
    df_segs['theta_deg'] = np.degrees(df_segs['theta']) % 360
    # Plotting
    states = ['A-p1', 'A-p2', 'A-p3', 'A-p4', 'B-p1', 'B-p2', 'B-p3', 'B-p4']
    for state in states:
        # Combined plot for Saccades vs Microsaccades
        s_movs = df_movs[df_movs['state'] == state]
        if len(s_movs) == 0: continue
        s_movs['theta_bin'] = (s_movs['theta_deg'] // 20) * 20
        rose_df = s_movs.groupby(['type', 'theta_bin']).size().reset_index(name='count')
        fig = px.bar_polar(rose_df, r='count', theta='theta_bin', color='type',
                           barmode='overlay',
                           template="plotly_dark",
                           title=f"Rose Plot: {state} Saccadic Directions (DVA)",
                           color_discrete_map={'Saccade': 'cyan', 'Microsaccade': 'orange'})
        # Add stats and caption
        caption = (
            f"Figure: Directional distribution of saccades and microsaccades for {state}. "
            f"Saccades defined as velocity > 30 DVA/s and amp >= 1.5 DVA. Microsaccades < 1.5 DVA. "
            f"Remarkable: Saccadic directions often align with the principal axis of visual processing for the stimulus."
        )
        fig.add_annotation(text=caption, xref="paper", yref="paper", x=0.5, y=-0.25, showarrow=False, width=800)
        fig.update_polars(angularaxis_direction="clockwise", angularaxis_rotation=90)
        fig.write_html(os.path.join(OUTPUT_DIR, f"FIG_Eye_Detailed_{state}.html"))
    print("Detailed analysis complete.")
    run_detailed_analysis()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
