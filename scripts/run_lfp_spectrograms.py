
import numpy as np
import pandas as pd
import os
from scipy.signal import spectrogram
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Parameters
DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
CHECKPOINT_DIR = r'D:\Analysis\Omission\local-workspace\checkpoints'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\final_reports\lfp'
os.makedirs(OUTPUT_DIR, exist_ok=True)

SESSIONS = ['230630', '230816', '230830']
FS = 1000.0
CONDITIONS = ['AAAB', 'AAAX'] # Standard vs Omission
AREA_ORDER = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']

def plot_spectrogram_suite():
    vflip_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'vflip2_mapping_v3.csv'))
    
    for sid in SESSIONS:
        print(f"LFP Spectrograms: Session {sid}")
        session_vflip = vflip_df[vflip_df['session_id'] == int(sid)]
        
        for p_id in session_vflip['probe_id'].unique():
            area = session_vflip[session_vflip['probe_id'] == p_id]['area'].values[0]
            crossover = session_vflip[session_vflip['probe_id'] == p_id]['crossover'].values[0]
            
            # Select representative channels (Superficial and Deep)
            ch_sup = int(crossover - 10) if crossover > 10 else 10
            ch_deep = int(crossover + 10) if crossover < 118 else 118
            
            fig = make_subplots(rows=2, cols=2, 
                                subplot_titles=(f"Sup ({ch_sup}) - AAAB", f"Sup ({ch_sup}) - AAAX",
                                               f"Deep ({ch_deep}) - AAAB", f"Deep ({ch_deep}) - AAAX"),
                                vertical_spacing=0.1, horizontal_spacing=0.1)
            
            for col_idx, cond in enumerate(CONDITIONS):
                f = os.path.join(DATA_DIR, f'ses{sid}-probe{p_id}-lfp-{cond}.npy')
                if not os.path.exists(f): continue
                
                lfp = np.load(f, mmap_mode='r') # (trials, 128, time)
                
                for row_idx, ch in enumerate([ch_sup, ch_deep]):
                    # Trial-averaged spectrogram
                    # Shape: (trials, 128, time)
                    trial_specs = []
                    for t_idx in range(min(20, lfp.shape[0])): # Average first 20 trials for speed
                        f_vec, t_vec, Sxx = spectrogram(lfp[t_idx, ch, :], fs=FS, nperseg=256, noverlap=200)
                        trial_specs.append(Sxx)
                    
                    avg_spec = np.mean(trial_specs, axis=0)
                    log_spec = 10 * np.log10(avg_spec + 1e-12)
                    
                    fig.add_trace(go.Heatmap(
                        z=log_spec, x=t_vec, y=f_vec,
                        coloraxis="coloraxis",
                        zmin=-40, zmax=0
                    ), row=row_idx+1, col=col_idx+1)
            
            fig.update_layout(title=f"LFP Spectrogram - Session {sid} - Probe {p_id} ({area})",
                              xaxis_title="Time (s)", yaxis_title="Frequency (Hz)",
                              coloraxis=dict(colorscale='Viridis'), height=1000, template="plotly_white")
            fig.update_yaxes(range=[0, 100]) # Focus on 0-100Hz
            
            fig.write_html(os.path.join(OUTPUT_DIR, f"FIG_09_Spectrogram_{sid}_P{p_id}_{area.replace(',', '_')}.html"))

if __name__ == '__main__':
    plot_spectrogram_suite()
