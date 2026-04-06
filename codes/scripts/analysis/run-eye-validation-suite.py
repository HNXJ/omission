
import scipy.io
import numpy as np
import os
import glob
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Constants
BHV_DIR = r'behavioral\omission_bhv\data'
NWB_DATA_DIR = r'data'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\eye_validation'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Stimulus timing
STIM_DURATION = 531
TOTAL_DURATION = 5248
TIME_VEC = np.arange(TOTAL_DURATION)

STIM_ON_CODES = [101, 103, 105, 107]
FIX_ON_CODE = 10 # Assuming 10 is fixation onset

def get_stim_sequence(trial):
    attrs = trial.TaskObject.Attribute
    stim_names = []
    for attr in attrs[1:]: # Skip fix
        if isinstance(attr, np.ndarray) and len(attr) > 1:
            nm = str(attr[1])
            if 'A.avi' in nm: stim_names.append('A')
            elif 'B.avi' in nm: stim_names.append('B')
            elif 'R.avi' in nm: stim_names.append('R')
            else: stim_names.append('O')
        else: stim_names.append('O')
    return "".join(stim_names)

def get_ylim_window(traces_list, buffer=0.1):
    """Calculates y-limits based on data between 1000ms and 4000ms."""
    if not traces_list: return None
    # Ensure we don't exceed trace length
    all_vals = np.concatenate([t[1000:min(len(t), 4000)] for t in traces_list])
    if len(all_vals) == 0: return None
    vmin, vmax = np.min(all_vals), np.max(all_vals)
    vrange = vmax - vmin if vmax > vmin else 1.0
    return [vmin - buffer * vrange, vmax + buffer * vrange]

def process_session_validation(fpath):
    session_id = os.path.basename(fpath).split('_')[0]
    print(f"Validating Session {session_id}...")
    
    try:
        data = scipy.io.loadmat(fpath, struct_as_record=False, squeeze_me=True)
        bhv_array = data['bhvUni']
    except: return

    session_data = []
    
    for t_idx, trial in enumerate(bhv_array):
        if trial.TrialError != 0: continue
        
        codes = trial.BehavioralCodes.CodeNumbers
        times = trial.BehavioralCodes.CodeTimes
        
        # Align to Fixation Onset (Code 10)
        idx_fix = np.where(codes == FIX_ON_CODE)[0]
        if len(idx_fix) == 0: continue
        t_start = int(times[idx_fix[0]])
        
        eye_data = trial.AnalogData.Eye # (nSamples, 2)
        if t_start + TOTAL_DURATION > len(eye_data): continue
        
        full_trace = eye_data[t_start : t_start + TOTAL_DURATION]
        cond_str = get_stim_sequence(trial)
        
        session_data.append({
            'trial_idx': t_idx,
            'cond': cond_str,
            'trace': full_trace # (5248, 2)
        })

    if not session_data: return
    
    # 1. Plot Full Trial Traces (Per Condition)
    fig_full = make_subplots(rows=2, cols=1, subplot_titles=["X Position (DVA)", "Y Position (DVA)"], vertical_spacing=0.1)
    
    all_mx, all_my = [], []
    
    for cond_target in ['AAAB', 'BBBA', 'RRRR']:
        subset = [d['trace'] for d in session_data if d['cond'] == cond_target]
        if not subset: continue
        
        stack = np.stack(subset)
        mx, my = np.mean(stack[:, :, 0], axis=0), np.mean(stack[:, :, 1], axis=0)
        all_mx.append(mx); all_my.append(my)
        
        fig_full.add_trace(go.Scatter(x=TIME_VEC, y=mx, name=f"{cond_target} (X)", line=dict(width=2)), row=1, col=1)
        fig_full.add_trace(go.Scatter(x=TIME_VEC, y=my, name=f"{cond_target} (Y)", line=dict(width=2)), row=2, col=1)

    # Calculate Y-Lims
    xlim = get_ylim_window(all_mx)
    ylim = get_ylim_window(all_my)
    if xlim: fig_full.update_yaxes(range=xlim, row=1, col=1)
    if ylim: fig_full.update_yaxes(range=ylim, row=2, col=1)

    # Annotate stimulus periods
    periods = [1000, 1531, 2062, 2593, 3124, 3655, 4186, 4717, 5248]
    for p in periods:
        fig_full.add_vline(x=p, line_dash="dash", line_color="gray", row='all', col=1)

    fig_full.update_layout(title=f"Full Trial Eye Trajectories - Session {session_id}", template="plotly_white", height=800)
    fig_full.write_html(os.path.join(OUTPUT_DIR, f"FIG_FullTrial_{session_id}.html"))

    # 2. Compare BHV (.mat) vs NWB (.npy)
    npy_file = os.path.join(NWB_DATA_DIR, f"ses{session_id}-behavioral-AAAB.npy")
    if os.path.exists(npy_file):
        try:
            nwb_traces = np.load(npy_file) # (nTrials, nCh, nTime)
            bhv_aaab = [d['trace'] for d in session_data if d['cond'] == 'AAAB']
            
            if len(bhv_aaab) > 0:
                fig_comp = make_subplots(rows=2, cols=1, subplot_titles=["X: BHV vs NWB", "Y: BHV vs NWB"])
                bhv_sample = bhv_aaab[0]
                nwb_sample_x = np.nan_to_num(nwb_traces[0, 1, :])
                nwb_sample_y = np.nan_to_num(nwb_traces[0, 2, :])
                
                # Z-Score for comparison (Shape match)
                def zscore(v): return (v - np.mean(v)) / np.std(v) if np.std(v) > 0 else v
                
                fig_comp.add_trace(go.Scatter(x=TIME_VEC, y=zscore(bhv_sample[:, 0]), name="BHV (Z-Scored) X", line=dict(color='blue')), row=1, col=1)
                fig_comp.add_trace(go.Scatter(x=np.arange(len(nwb_sample_x)), y=zscore(nwb_sample_x), name="NWB (Z-Scored) X", line=dict(color='red', dash='dot')), row=1, col=1)
                
                fig_comp.add_trace(go.Scatter(x=TIME_VEC, y=zscore(bhv_sample[:, 1]), name="BHV (Z-Scored) Y", line=dict(color='green')), row=2, col=1)
                fig_comp.add_trace(go.Scatter(x=np.arange(len(nwb_sample_y)), y=zscore(nwb_sample_y), name="NWB (Z-Scored) Y", line=dict(color='orange', dash='dot')), row=2, col=1)
                
                # Note on units
                fig_comp.add_annotation(text="Note: Signals are Z-scored to allow shape comparison across differing units (BHV: DVA, NWB: Raw Volts).",
                                        xref="paper", yref="paper", x=0.5, y=-0.2, showarrow=False)
                
                fig_comp.update_layout(title=f"BHV vs NWB Calibration Check - Session {session_id}", template="plotly_white")
                fig_comp.write_html(os.path.join(OUTPUT_DIR, f"FIG_Comparison_{session_id}.html"))
                print(f"  Comparison saved for {session_id}")
        except Exception as e:
            print(f"  Error comparing {session_id}: {e}")

def run_eye_validation_suite():
    files = glob.glob(os.path.join(BHV_DIR, "*.mat"))
    for f in files:
        process_session_validation(f)

if __name__ == '__main__':
    run_eye_validation_suite()
