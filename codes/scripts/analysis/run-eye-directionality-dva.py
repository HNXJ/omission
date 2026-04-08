
from codes.config.paths import FIGURES_DIR, BEHAVIORAL_DIR

import scipy.io
import numpy as np
import os
import glob
import pandas as pd
from scipy.stats import circmean, circstd
import plotly.express as px
import plotly.graph_objects as go
from concurrent.futures import ProcessPoolExecutor

# Constants
BHV_DIR = BEHAVIORAL_DIR / 'omission_bhv/data'
OUTPUT_DIR = FIGURES_DIR / 'eye_directionality'
# Stimulus timing codes
CODE_P1_ON = 101; CODE_P1_OFF = 102
CODE_P2_ON = 103; CODE_P2_OFF = 104
CODE_P3_ON = 105; CODE_P3_OFF = 106
CODE_P4_ON = 107; CODE_P4_OFF = 108
# Velocity Threshold for movement categorization (DVA/s)
VEL_THRESH = 30 

def get_pca_direction(x, y):
    """Calculates the principal direction of movement using PCA."""
    if len(x) < 10: return np.nan
    X = np.stack([x, y], axis=1)
    center = np.mean(X, axis=0)
    Xc = X - center
    C = np.cov(Xc.T)
    if np.any(np.isnan(C)) or np.any(np.isinf(C)): return np.nan
    vals, vecs = np.linalg.eig(C)
    idx = np.argmax(vals)
    direction = vecs[:, idx]
    delta = X[-1, :] - X[0, :]
    if np.dot(delta, direction) < 0:
        direction = -direction
    return np.arctan2(direction[1], direction[0])

def process_session(fpath):
    print(f"Processing {os.path.basename(fpath)}...")
    try:
        data = scipy.io.loadmat(fpath, struct_as_record=False, squeeze_me=True)
        bhv_array = data['bhvUni']
    except Exception as e:
        print(f"Error loading {fpath}: {e}")
        return []
    session_results = []
    for t_idx, trial in enumerate(bhv_array):
        # 1. Check for success
        if trial.TrialError != 0: continue
        # 2. Get codes and times
        codes = trial.BehavioralCodes.CodeNumbers
        times = trial.BehavioralCodes.CodeTimes
        # 3. Get stimulus sequence from TaskObject
        # In this task, TO 1 is fix, TO 2 is P1, TO 3 is P2, etc.
        attrs = trial.TaskObject.Attribute
        stim_names = []
        for attr in attrs[1:]: # Skip 'fix'
            if isinstance(attr, np.ndarray) and len(attr) > 1:
                nm = str(attr[1])
                if 'A.avi' in nm: stim_names.append('A')
                elif 'B.avi' in nm: stim_names.append('B')
                else: stim_names.append('O') # Omission or R
            else:
                stim_names.append('O')
        # 4. Extract Eye Data
        eye_data = trial.AnalogData.Eye # (nSamples, 2)
        # Sample rate is 1kHz, so times are in ms
        # Analyze p1-p4
        on_codes = [101, 103, 105, 107]
        off_codes = [102, 104, 106, 108]
        for i, (on_c, off_c) in enumerate(zip(on_codes, off_codes)):
            if i >= len(stim_names): break
            stim = stim_names[i]
            if stim not in ['A', 'B']: continue
            # Find times
            idx_on = np.where(codes == on_c)[0]
            idx_off = np.where(codes == off_c)[0]
            if len(idx_on) > 0 and len(idx_off) > 0:
                t_on = int(times[idx_on[0]])
                t_off = int(times[idx_off[0]])
                # Clip to eye data length
                if t_on < 0: t_on = 0
                if t_off > len(eye_data): t_off = len(eye_data)
                if t_off - t_on > 10:
                    seg = eye_data[t_on:t_off]
                    x, y = seg[:, 0], seg[:, 1]
                    # Overall PCA Theta
                    theta = get_pca_direction(x, y)
                    # Categorize movements by velocity
                    dx = np.diff(x)
                    dy = np.diff(y)
                    vel = 1000 * np.sqrt(dx**2 + dy**2) # DVA/s
                    # Store data
                    session_results.append({
                        'session': os.path.basename(fpath)[:6],
                        'state': f"{stim}-p{i+1}",
                        'stim': stim,
                        'pos': i+1,
                        'theta': theta,
                        'x_mean': np.mean(x),
                        'y_mean': np.mean(y),
                        'x_std': np.std(x),
                        'y_std': np.std(y),
                        'mean_vel': np.mean(vel)
                    })
    return session_results

def run_eye_directionality_analysis():
    files = glob.glob(os.path.join(BHV_DIR, "*.mat"))
    all_results = []
    # Using loop for simplicity and to avoid pickling errors with mat_struct
    for f in files:
        res = process_session(f)
        all_results.extend(res)
    df = pd.DataFrame(all_results)
    df = df.dropna(subset=['theta'])
    df['theta_deg'] = np.degrees(df['theta']) % 360
    # Calculate Stats per State
    stats = []
    states = ['A-p1', 'A-p2', 'A-p3', 'A-p4', 'B-p1', 'B-p2', 'B-p3', 'B-p4']
    for state in states:
        sdf = df[df['state'] == state]
        if len(sdf) == 0: continue
        # Circular mean/std
        m_theta = np.degrees(circmean(np.radians(sdf['theta_deg']))) % 360
        s_theta = np.degrees(circstd(np.radians(sdf['theta_deg'])))
        stats.append({
            'State': state,
            'Count': len(sdf),
            'Mean_X': sdf['x_mean'].mean(),
            'Std_X': sdf['x_mean'].std(),
            'Mean_Y': sdf['y_mean'].mean(),
            'Std_Y': sdf['y_mean'].std(),
            'Mean_Theta': m_theta,
            'Std_Theta': s_theta
        })
        # Rose Plot for this state
        sdf_copy = sdf.copy()
        sdf_copy['theta_bin'] = (sdf_copy['theta_deg'] // 15) * 15
        rose_df = sdf_copy.groupby('theta_bin').size().reset_index(name='count')
        fig = px.bar_polar(rose_df, r='count', theta='theta_bin',
                           template="plotly_dark",
                           title=f"Rose Plot: {state} Directionality (PCA Principal Axis)",
                           color_discrete_sequence=['cyan' if 'A' in state else 'magenta'])
        fig.update_polars(angularaxis_direction="clockwise", angularaxis_rotation=90)
        # Add caption
        caption = (
            f"Figure: Eye movement directionality for {state}. "
            f"Method: PCA-based principal axis extraction on DVA-calibrated eye coordinates ({len(sdf)} trials). "
            f"Results: Circular Mean = {m_theta:.1f}°, Circular Std = {s_theta:.1f}°. "
            f"Position: X = {sdf['x_mean'].mean():.2f} ± {sdf['x_mean'].std():.2f}, Y = {sdf['y_mean'].mean():.2f} ± {sdf['y_mean'].std():.2f} DVA."
        )
        fig.add_annotation(text=caption, xref="paper", yref="paper", x=0.5, y=-0.2, showarrow=False, width=600)
        fig.write_html(os.path.join(OUTPUT_DIR, f"FIG_Eye_Dir_{state}.html"))
    stats_df = pd.DataFrame(stats)
    stats_df.to_csv(os.path.join(OUTPUT_DIR, "eye_directionality_stats.csv"), index=False)
    print("Analysis complete. Statistics saved to eye_directionality_stats.csv.")
    # Summary Plot: Mean Position with Std Bars
    fig_pos = px.scatter(stats_df, x='Mean_X', y='Mean_Y', color='State',
                         error_x='Std_X', error_y='Std_Y',
                         title="Average Eye Position ± Std across States (DVA)",
                         template="plotly_white")
    fig_pos.add_annotation(text="Figure: Average gaze position and variability across A/B stimulus positions (p1-p4). Calibrated to Degrees of Visual Angle (DVA).",
                           xref="paper", yref="paper", x=0.5, y=-0.15, showarrow=False)
    fig_pos.write_html(os.path.join(OUTPUT_DIR, "FIG_Eye_Position_Summary.html"))

def main(args=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    run_eye_directionality_analysis()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
