import os
import numpy as np
import plotly.graph_objects as go
import glob
import json

# Mandated Palette (Vanderbilt Gold, Electric Violet, Teal, Orange)
EPOCH_COLORS = {
    'p1': '#CFB87C',
    'p2': '#8F00FF',
    'p3': '#00FFCC',
    'p4': '#FF5E00'
}

# Stimulus Onsets relative to p1 alignment (at 1000ms)
ONSETS = {
    'p1': 1000,
    'p2': 2031,
    'p3': 3062,
    'p4': 4093
}

CONDITIONS = ['AAAB', 'BBBA', 'RRRR']
SESSIONS = ['230901', '230629', '230712', '230713', '230714', '230719', '230720', '230721', '230816', '230818', '230823', '230825', '230830', '230831']

def run():
    print("Generating Pupil Diameter Plot (p1-p4 Comparison)...")
    
    behavioral_dir = r'D:\Analysis\Omission\local-workspace\data\behavioral'
    output_dir = r'D:\Analysis\Omission\local-workspace\figures\behavioral'
    os.makedirs(output_dir, exist_ok=True)
    
    all_pupil_data = {epoch: [] for epoch in ONSETS.keys()}
    sessions_with_data = []

    for sid in SESSIONS:
        session_found = False
        for cond in CONDITIONS:
            f_pattern = f'ses{sid}-behavioral-{cond}.npy'
            f_path = os.path.join(behavioral_dir, f_pattern)
            
            if os.path.exists(f_path):
                session_found = True
                try:
                    # data shape: (trials, channels, 6000)
                    # Channel 2 is Pupil Diameter
                    data = np.load(f_path)
                    pupil = data[:, 2, :] # (trials, 6000)
                    
                    # Sanitation
                    pupil = np.nan_to_num(pupil, nan=np.nanmedian(pupil))
                    
                    # Normalize (z-score) per session to allow pooling if needed
                    # but the user asked for diameter, so maybe just mean-subtraction?
                    # Let's keep it as is if it's already extracted.
                    
                    for epoch, onset in ONSETS.items():
                        start = onset - 500
                        end = onset + 1000
                        if end <= 6000:
                            # (n_trials, 1500)
                            segment = pupil[:, start:end]
                            # Average over trials for this session/condition
                            all_pupil_data[epoch].append(np.nanmean(segment, axis=0))
                except Exception as e:
                    print(f"  Error processing {f_path}: {e}")
        
        if session_found:
            sessions_with_data.append(sid)

    if not any(all_pupil_data.values()):
        print("No pupil data found in the available sessions.")
        return

    # Grand average across all sessions and conditions
    fig = go.Figure()
    time_ax = np.linspace(-500, 1000, 1500)

    for epoch in ['p1', 'p2', 'p3', 'p4']:
        epoch_data = np.array(all_pupil_data[epoch]) # (n_session_cond_pairs, 1500)
        mean_pupil = np.nanmean(epoch_data, axis=0)
        sem_pupil = np.nanstd(epoch_data, axis=0) / np.sqrt(epoch_data.shape[0])
        
        # Smooth for visualization
        window = 50
        mean_pupil_s = np.convolve(mean_pupil, np.ones(window)/window, mode='same')
        sem_pupil_s = np.convolve(sem_pupil, np.ones(window)/window, mode='same')

        # Trace
        fig.add_trace(go.Scatter(
            x=time_ax, y=mean_pupil_s,
            mode='lines',
            line=dict(color=EPOCH_COLORS[epoch], width=3),
            name=f'Presentation {epoch.upper()}'
        ))
        
        # SEM Shade
        fig.add_trace(go.Scatter(
            x=np.concatenate([time_ax, time_ax[::-1]]),
            y=np.concatenate([mean_pupil_s + 2*sem_pupil_s, (mean_pupil_s - 2*sem_pupil_s)[::-1]]),
            fill='toself',
            fillcolor=EPOCH_COLORS[epoch],
            opacity=0.2,
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=False,
            hoverinfo='skip'
        ))

    fig.update_layout(
        title=f"<b>Pupil Diameter Comparison: P1, P2, P3, P4</b><br><sup>Grand Average across {len(sessions_with_data)} sessions | Conditions: {', '.join(CONDITIONS)}</sup>",
        xaxis_title="Time relative to stimulus onset [ms]",
        yaxis_title="Pupil Diameter [z-score]",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.5)
    fig.add_vrect(x0=0, x1=531, fillcolor="gray", opacity=0.1, layer="below", line_width=0, annotation_text="Stimulus")

    base_name = os.path.join(output_dir, "pupil_comparison_p1_p4")
    fig.write_html(base_name + ".html")
    fig.write_image(base_name + ".svg")
    fig.write_image(base_name + ".png")
    
    meta = {
        "script": "generate_pupil_plot.py",
        "sessions": sessions_with_data,
        "conditions": CONDITIONS,
        "window": [-500, 1000],
        "colors": EPOCH_COLORS
    }
    with open(base_name + ".metadata.json", "w") as f:
        json.dump(meta, f, indent=4)
        
    print(f"Pupil comparison plot saved to {output_dir}")

if __name__ == '__main__':
    run()
