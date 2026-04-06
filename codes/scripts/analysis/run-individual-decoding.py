
import numpy as np
import pandas as pd
import os
import glob
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, cross_val_score
import plotly.graph_objects as go

# Config
DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
CHECKPOINT_DIR = r'D:\Analysis\Omission\local-workspace\checkpoints'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\final_reports\decoding'
os.makedirs(OUTPUT_DIR, exist_ok=True)

SESSIONS = ['230630', '230816', '230830']
WINS = {'p2': (2062, 2593), 'p3': (3124, 3655), 'p4': (4186, 4717)}

def decode_single_units():
    units_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'neuron_categories.csv'))
    results = []
    
    for sid in SESSIONS:
        print(f"Decoding Individual Units: Session {sid}")
        session_units = units_df[units_df['session'] == int(sid)]
        
        # Test Case: p2-of-axab vs. p2-of-rxrr vs. p2-of-bxba (Multiclass)
        conds = ['AXAB', 'RXRR', 'BXBA']
        win = WINS['p2']
        
        for idx, row in session_units.iterrows():
            u_idx, p_id = row['unit_idx'], row['probe']
            f_paths = [os.path.join(DATA_DIR, f'ses{sid}-units-probe{p_id}-spk-{c}.npy') for c in conds]
            
            X_list, y_list = [], []
            if all(os.path.exists(f) for f in f_paths):
                for i, f in enumerate(f_paths):
                    # Load individual neuron's mean firing rate in window
                    data = np.mean(np.load(f, mmap_mode='r')[:, u_idx, win[0]:win[1]], axis=1).reshape(-1, 1)
                    X_list.append(data)
                    y_list.append(np.full(len(data), i))
                
                # Balanced Multiclass
                n_min = min(len(x) for x in X_list)
                if n_min > 5:
                    X_bal = np.vstack([x[:n_min] for x in X_list])
                    y_bal = np.concatenate([y[:n_min] for y in y_list])
                    
                    scores = cross_val_score(SVC(kernel='linear'), X_bal, y_bal, cv=3)
                    results.append({
                        'unit_id': f"{sid}_{p_id}_{u_idx}",
                        'area': row['area'],
                        'category': row['category'],
                        'accuracy': np.mean(scores)
                    })
                    
    pd.DataFrame(results).to_csv(os.path.join(OUTPUT_DIR, "individual_unit_decoding.csv"), index=False)

def decode_lfp_channels():
    results = []
    for sid in SESSIONS:
        print(f"Decoding LFP Channels: Session {sid}")
        # Identify probes with V1 and PFC
        probes = [0, 1, 2] # Most sessions have 3 probes
        conds = ['AXAB', 'RXRR', 'BXBA']
        win = WINS['p2']
        
        for p_id in probes:
            f_paths = [os.path.join(DATA_DIR, f'ses{sid}-probe{p_id}-lfp-{c}.npy') for c in conds]
            if all(os.path.exists(f) for f in f_paths):
                # Load LFP data (trials, 128, time)
                all_data = [np.load(f, mmap_mode='r')[:, :, win[0]:win[1]] for f in f_paths]
                
                for ch in range(128):
                    X_list, y_list = [], []
                    for i, d in enumerate(all_data):
                        feat = np.mean(d[:, ch, :], axis=1).reshape(-1, 1)
                        X_list.append(feat)
                        y_list.append(np.full(len(feat), i))
                    
                    n_min = min(len(x) for x in X_list)
                    if n_min > 5:
                        X_bal = np.vstack([x[:n_min] for x in X_list])
                        y_bal = np.concatenate([y[:n_min] for y in y_list])
                        scores = cross_val_score(SVC(kernel='linear'), X_bal, y_bal, cv=3)
                        results.append({'session': sid, 'probe': p_id, 'channel': ch, 'accuracy': np.mean(scores)})
                        
    pd.DataFrame(results).to_csv(os.path.join(OUTPUT_DIR, "individual_lfp_decoding.csv"), index=False)

if __name__ == '__main__':
    decode_single_units()
    decode_lfp_channels()
    print("Decoding complete. Results saved in figures/final_reports/decoding/")
