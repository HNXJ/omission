
import numpy as np
import pandas as pd
import scipy.io as sio
import os
import glob
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Time windows relative to p1 onset (in ms)
TIME_WINDOWS = {
    'fx': (-500, 0),
    'p1': (0, 531),
    'd1': (531, 1031),
    'p2': (1031, 1562),
    'd2': (1562, 2062),
    'p3': (2062, 2593),
    'd3': (2593, 3093),
    'p4': (3093, 3624),
    'd4': (3624, 4124),
}

CONDITION_MAP = {
    1: 'AAAB', 2: 'AAAB', 3: 'AXAB', 4: 'AAXB', 5: 'AAAX',
    6: 'BBBA', 7: 'BBBA', 8: 'BXBA', 9: 'BBXA', 10: 'BBBX',
    **{i: 'RRRR' for i in range(11, 27)},
    **{i: 'RXRR' for i in range(27, 35)},
    35: 'RRXR', 37: 'RRXR', 39: 'RRXR', 41: 'RRXR',
    36: 'RRRX', 38: 'RRRX', 40: 'RRRX', 42: 'RRRX',
    **{i: 'RRRX' for i in range(43, 51)},
}

def get_condition_name(trial):
    return CONDITION_MAP.get(trial.Condition, f"Unknown_{trial.Condition}")

def calculate_variance(mat_path):
    """Calculates eye-x and eye-y variance for different time windows."""
    try:
        mat = sio.loadmat(mat_path, struct_as_record=False, squeeze_me=True)
        bhvUni = mat['bhvUni']
        
        variances = []
        
        for trial in bhvUni:
            if trial.TrialError != 0:
                continue

            codes = trial.BehavioralCodes.CodeNumbers
            times = trial.BehavioralCodes.CodeTimes
            p1_idx = np.where(codes == 101)[0]
            if len(p1_idx) == 0:
                continue
            p1_time = times[p1_idx[0]]
            
            eye_data = trial.AnalogData.Eye
            
            for window_name, (start_ms, end_ms) in TIME_WINDOWS.items():
                start_sample = int(p1_time + start_ms)
                end_sample = int(p1_time + end_ms)
                
                if end_sample > len(eye_data):
                    continue
                    
                eye_window = eye_data[start_sample:end_sample]
                
                var_x = np.var(eye_window[:, 0])
                var_y = np.var(eye_window[:, 1])
                
                variances.append({
                    'session': os.path.basename(mat_path).split('_')[0],
                    'condition': get_condition_name(trial),
                    'window': window_name,
                    'var_x': var_x,
                    'var_y': var_y,
                    'var_total': var_x + var_y
                })
                
        return pd.DataFrame(variances)
        
    except Exception as e:
        print(f"Error processing {mat_path}: {e}")
        return pd.DataFrame()

def main():
    bhv_dir = r'D:\Analysis\Omission\local-workspace\data\behavioral'
    output_dir = r'D:\Analysis\Omission\local-workspace\figures\part02'
    os.makedirs(output_dir, exist_ok=True)
    
    all_variances = []
    for mat_file in glob.glob(os.path.join(bhv_dir, "*.mat")):
        all_variances.append(calculate_variance(mat_file))
        
    df = pd.concat(all_variances, ignore_index=True)
    
    # --- Generate Plots ---
    # 1. Bar plot of average variance by time window
    avg_variance = df.groupby('window')[['var_x', 'var_y', 'var_total']].mean().reindex(TIME_WINDOWS.keys())
    
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=avg_variance.index, y=avg_variance['var_x'], name='Var(X)', marker_color='red'))
    fig1.add_trace(go.Bar(x=avg_variance.index, y=avg_variance['var_y'], name='Var(Y)', marker_color='blue'))
    fig1.add_trace(go.Bar(x=avg_variance.index, y=avg_variance['var_total'], name='Var(Total)', marker_color='green'))
    fig1.update_layout(
        title='Average Eye Variance by Time Window',
        xaxis_title='Time Window',
        yaxis_title='Variance (DVA^2)',
        barmode='group',
        template='plotly_white'
    )
    fig1.write_html(os.path.join(output_dir, 'avg_variance_by_window.html'))
    
    # 2. Session-by-session variance plot
    session_variance = df.groupby(['session', 'condition', 'window'])[['var_x', 'var_y', 'var_total']].mean().reset_index()
    conditions = sorted(session_variance['condition'].unique())
    
    fig2 = make_subplots(
        rows=len(conditions), 
        cols=1, 
        subplot_titles=conditions,
        shared_xaxes=True,
        vertical_spacing=0.02
    )
    
    sessions = sorted(session_variance['session'].unique())
    colors = ['red', 'blue', 'green', 'yellow', 'brown', 'pink', 'gray', 'purple', 'cyan', 'darkblue', 'darkred', 'darkgreen', 'darkgoldenrod', 'black']

    for i, cond in enumerate(conditions):
        cond_df = session_variance[session_variance['condition'] == cond]
        for j, session in enumerate(sessions):
            session_df = cond_df[cond_df['session'] == session]
            if not session_df.empty:
                show_legend = (i == 0)
                color = colors[j % len(colors)]
                fig2.add_trace(go.Scatter(x=session_df['window'], y=session_df['var_x'], mode='lines+markers', line=dict(color=color, dash='dot'), name=f'{session}-x', legendgroup=session, showlegend=show_legend), row=i+1, col=1)
                fig2.add_trace(go.Scatter(x=session_df['window'], y=session_df['var_y'], mode='lines+markers', line=dict(color=color, dash='dash'), name=f'{session}-y', legendgroup=session, showlegend=show_legend), row=i+1, col=1)
                fig2.add_trace(go.Scatter(x=session_df['window'], y=session_df['var_total'], mode='lines+markers', line=dict(color=color), name=f'{session}-total', legendgroup=session, showlegend=show_legend), row=i+1, col=1)

    fig2.update_layout(
        title='Session-by-Session Eye Variance by Condition',
        height=200 * len(conditions),
        template='plotly_white'
    )
    fig2.write_html(os.path.join(output_dir, 'session_variance_by_condition.html'))
    
    print("Analysis complete. Plots saved to:", output_dir)

if __name__ == '__main__':
    main()
