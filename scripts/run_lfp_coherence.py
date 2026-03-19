
import numpy as np
import pandas as pd
import os
from scipy.signal import coherence
import plotly.graph_objects as go

# Parameters
DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
CHECKPOINT_DIR = r'D:\Analysis\Omission\local-workspace\checkpoints'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\final_reports\lfp'
os.makedirs(OUTPUT_DIR, exist_ok=True)

SESSIONS = ['230630', '230816', '230830']
FS = 1000.0
OMIT_ONSET = 4124
WIN_SIZE = 500

def run_lfp_coherence():
    vflip_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'vflip2_mapping_v3.csv'))
    results = []
    
    for sid in SESSIONS:
        print(f"LFP Coherence: Session {sid}")
        session_vflip = vflip_df[vflip_df['session_id'] == int(sid)]
        
        probes = session_vflip['probe_id'].unique()
        if len(probes) < 2: continue
        
        # Select one rep channel per probe
        probe_channels = {}
        for p_id in probes:
            crossover_vals = session_vflip[session_vflip['probe_id'] == p_id]['crossover'].values
            if len(crossover_vals) > 0 and not np.isnan(crossover_vals[0]):
                probe_channels[p_id] = int(crossover_vals[0])
            else:
                probe_channels[p_id] = 64 # Default mid-channel
            
        # Pairwise combinations
        for i in range(len(probes)):
            for j in range(i + 1, len(probes)):
                p1, p2 = probes[i], probes[j]
                area1 = session_vflip[session_vflip['probe_id'] == p1]['area'].values[0]
                area2 = session_vflip[session_vflip['probe_id'] == p2]['area'].values[0]
                
                for cond in ['AAAB', 'AAAX']:
                    f1 = os.path.join(DATA_DIR, f'ses{sid}-probe{p1}-lfp-{cond}.npy')
                    f2 = os.path.join(DATA_DIR, f'ses{sid}-probe{p2}-lfp-{cond}.npy')
                    
                    if os.path.exists(f1) and os.path.exists(f2):
                        lfp1 = np.load(f1, mmap_mode='r')
                        lfp2 = np.load(f2, mmap_mode='r')
                        
                        ch1, ch2 = probe_channels[p1], probe_channels[p2]
                        
                        # (trials, ch, time)
                        sig1 = lfp1[:, ch1, OMIT_ONSET : OMIT_ONSET + WIN_SIZE]
                        sig2 = lfp2[:, ch2, OMIT_ONSET : OMIT_ONSET + WIN_SIZE]
                        
                        all_coh = []
                        for t in range(min(50, sig1.shape[0])):
                            f_vec, Cxy = coherence(sig1[t, :], sig2[t, :], fs=FS, nperseg=256)
                            all_coh.append(Cxy)
                        
                        avg_coh = np.mean(all_coh, axis=0)
                        
                        # Extract Gamma Coherence (35-80Hz)
                        gamma_mask = (f_vec >= 35) & (f_vec <= 80)
                        gamma_coh = np.mean(avg_coh[gamma_mask])
                        
                        results.append({
                            'session': sid, 'pair': f"{area1}-{area2}", 'condition': cond, 
                            'gamma_coherence': gamma_coh
                        })
    
    res_df = pd.DataFrame(results)
    res_df.to_csv(os.path.join(CHECKPOINT_DIR, 'lfp_coherence_results.csv'), index=False)
    
    # Plotting
    fig = px.bar(res_df, x='pair', y='gamma_coherence', color='condition', barmode='group',
                 title="Figure 11: Inter-Area Gamma Coherence (Omission vs. Standard)")
    fig.write_html(os.path.join(OUTPUT_DIR, "FIG_11_Coherence_Results.html"))

if __name__ == '__main__':
    run_lfp_coherence()
