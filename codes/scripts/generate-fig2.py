
import scipy.io
import numpy as np
import os
import glob
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Constants ---
BHV_DIR = 'data/behavioral'
OUTPUT_DIR = 'figures/oglo/fig_02_EYE_DVA_ALLSESSIONS'
os.makedirs(OUTPUT_DIR, exist_ok=True)

TRIAL_DURATION = 5248  # ms, from fixation onset to end of D4
FIXATION_ONSET_CODE = 10

# From TASK_DETAILS.md
OMISSION_WINDOWS = {
    'AXAB': (1031, 1031 + 531),
    'BXBA': (1031, 1031 + 531),
    'RXRR': (1031, 1031 + 531),
    'AAXB': (1562, 1562 + 531),
    'BBXA': (1562, 1562 + 531),
    'RRXR': (1562, 1562 + 531),
    'AAAX': (2093, 2093 + 531),
    'BBBX': (2093, 2093 + 531),
    'RRRX': (2093, 2093 + 531),
}

# From bhv_task_details.md
CONDITION_MAP = {
    1: 'AAAB', 2: 'AAAB',
    3: 'AXAB',
    4: 'AAXB',
    5: 'AAAX',
    6: 'BBBA', 7: 'BBBA',
    8: 'BXBA',
    9: 'BBXA',
    10: 'BBBX',
    11: 'RRRR', 12: 'RRRR', 13: 'RRRR', 14: 'RRRR', 15: 'RRRR', 16: 'RRRR',
    17: 'RRRR', 18: 'RRRR', 19: 'RRRR', 20: 'RRRR', 21: 'RRRR', 22: 'RRRR',
    23: 'RRRR', 24: 'RRRR', 25: 'RRRR', 26: 'RRRR',
    27: 'RXRR', 28: 'RXRR', 29: 'RXRR', 30: 'RXRR', 31: 'RXRR', 32: 'RXRR',
    33: 'RXRR', 34: 'RXRR',
    35: 'RRXR', 37: 'RRXR', 39: 'RRXR', 41: 'RRXR',
    36: 'RRRX', 38: 'RRRX', 40: 'RRRX', 42: 'RRRX', 43: 'RRRX', 44: 'RRRX',
    45: 'RRRX', 46: 'RRRX', 47: 'RRRX', 48: 'RRRX', 49: 'RRRX', 50: 'RRRX',
}

def extract_full_eye_traces():
    """Extracts full trial eye traces for all correct trials from all sessions."""
    files = glob.glob(os.path.join(BHV_DIR, "*.mat"))
    all_traces = []

    for fpath in files:
        session_id = os.path.basename(fpath).split('_')[0]
        print(f"Extracting traces from session: {session_id}...")
        try:
            data = scipy.io.loadmat(fpath, struct_as_record=False, squeeze_me=True)
            bhv_array = data['bhvUni']
        except Exception as e:
            print(f"  Could not load {fpath}: {e}")
            continue

        for trial in bhv_array:
            if trial.TrialError != 0:
                continue

            try:
                cond_num = trial.Condition
                cond_name = CONDITION_MAP.get(cond_num)
                if not cond_name:
                    continue

                codes = trial.BehavioralCodes.CodeNumbers
                times = trial.BehavioralCodes.CodeTimes
                eye_data = trial.AnalogData.Eye  # (nSamples, 2)

                fix_onset_idx = np.where(codes == FIXATION_ONSET_CODE)[0]
                if len(fix_onset_idx) > 0:
                    t_fix_on = int(times[fix_onset_idx[0]])
                    t_end = t_fix_on + TRIAL_DURATION

                    if t_end <= len(eye_data):
                        trace = eye_data[t_fix_on:t_end]
                        all_traces.append({
                            'session': session_id,
                            'condition': cond_name,
                            'trace_x': trace[:, 0],
                            'trace_y': trace[:, 1]
                        })
            except Exception as e:
                # print(f"  Skipping trial due to error: {e}")
                pass
                
    return pd.DataFrame(all_traces)

def plot_condition_traces(df):
    """Plots and saves figures for each condition."""
    if df.empty:
        print("No traces were extracted. Exiting.")
        return

    for condition_name, group in df.groupby('condition'):
        print(f"  Plotting condition: {condition_name}...")

        n_trials = len(group)
        if n_trials == 0:
            continue

        # Stack traces to compute mean and SEM
        x_stack = np.stack(group['trace_x'].values)
        y_stack = np.stack(group['trace_y'].values)

        mean_x, sem_x = np.mean(x_stack, axis=0), np.std(x_stack, axis=0) / np.sqrt(n_trials)
        mean_y, sem_y = np.mean(y_stack, axis=0), np.std(y_stack, axis=0) / np.sqrt(n_trials)
        
        time_vec = np.arange(TRIAL_DURATION)

        fig = go.Figure()

        # X Trace
        fig.add_trace(go.Scatter(
            x=time_vec, y=mean_x,
            name='Eye X', line=dict(color='blue'), legendgroup='x'
        ))
        fig.add_trace(go.Scatter(
            x=np.concatenate([time_vec, time_vec[::-1]]),
            y=np.concatenate([mean_x - sem_x, (mean_x + sem_x)[::-1]]),
            fill='toself', fillcolor='rgba(0,0,255,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip", showlegend=False, legendgroup='x'
        ))

        # Y Trace
        fig.add_trace(go.Scatter(
            x=time_vec, y=mean_y,
            name='Eye Y', line=dict(color='red'), legendgroup='y'
        ))
        fig.add_trace(go.Scatter(
            x=np.concatenate([time_vec, time_vec[::-1]]),
            y=np.concatenate([mean_y - sem_y, (mean_y + sem_y)[::-1]]),
            fill='toself', fillcolor='rgba(255,0,0,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip", showlegend=False, legendgroup='y'
        ))

        # Add omission patch
        if condition_name in OMISSION_WINDOWS:
            x0, x1 = OMISSION_WINDOWS[condition_name]
            fig.add_vrect(x0=x0, x1=x1, fillcolor="pink", opacity=0.3, layer="below", line_width=0)

        # Statistics for caption
        stats_caption = (
            f"<b>Statistics (N={n_trials} trials):</b><br>"
            f"Eye X (DVA): Mean(μ)={np.mean(mean_x):.3f}, Std(σ)={np.std(x_stack):.3f}<br>"
            f"Eye Y (DVA): Mean(μ)={np.mean(mean_y):.3f}, Std(σ)={np.std(y_stack):.3f}"
        )
        
        fig.update_layout(
            title=f'Eye Gaze (DVA) - Condition: {condition_name}',
            xaxis_title='Time from Fixation Onset (ms)',
            yaxis_title='Gaze Position (Degrees of Visual Angle)',
            template='plotly_white',
            height=600,
            width=1200,
            annotations=[
                dict(
                    text=stats_caption,
                    showarrow=False,
                    xref='paper', yref='paper',
                    x=0.5, y=-0.2,
                    align='center'
                )
            ],
            margin=dict(b=150)
        )

        # Save files
        base_filename = f"{condition_name}_full_eye_dva"
        html_path = os.path.join(OUTPUT_DIR, f"{base_filename}.html")
        svg_path = os.path.join(OUTPUT_DIR, f"{base_filename}.svg")

        fig.write_html(html_path)
        fig.write_image(svg_path)

    print("All conditions plotted.")


if __name__ == '__main__':
    print("Starting eye trace extraction...")
    all_traces_df = extract_full_eye_traces()
    print("Plotting traces for all conditions...")
    plot_condition_traces(all_traces_df)
    print("Figure 2 generation complete.")

