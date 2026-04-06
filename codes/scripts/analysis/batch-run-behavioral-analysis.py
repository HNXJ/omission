import numpy as np
import os
from pathlib import Path
from run_behavioral_decoding_suite import analyze_session_eye, decode_identity_eye
from run_behavioral_decoding_suite_plotly import plot_identity_decoding_plotly
from run_eye_consolidated_report_plotly import run_eye_consolidated_plotly

def run_all_behavioral_analyses(data_dir, exclude_session="230629"):
    """Runs Rose Plots, Trajectories, and Identity Decoding for all available sessions."""
    # Identify unique session IDs from behavioral .npy files
    files = [f for f in os.listdir(data_dir) if f.startswith('ses') and '-behavioral-' in f and f.endswith('.npy')]
    sessions = sorted(list(set([f.split('-')[0].replace('ses', '') for f in files])))
    
    print(f"Found {len(sessions)} sessions: {sessions}")
    
    for session_id in sessions:
        if session_id == exclude_session:
            print(f"Skipping excluded session: {session_id}")
            continue
            
        output_check = Path(__file__).parents[2] / "output" / f"FIG_Eye_Rose_Grid_{session_id}.html"
        if os.path.exists(output_check):
            print(f"Session {session_id} already processed. Skipping.")
            continue

        print(f"\n--- Processing Session: {session_id} ---")
        
        try:
            # 1. Identity Decoding (A vs B)
            print(f"Running Identity Decoding for {session_id}...")
            results = analyze_session_eye(data_dir, session_id)
            scores = decode_identity_eye(results)
            if scores is not None:
                plot_identity_decoding_plotly(scores, session_id)
            else:
                print(f"Warning: Identity decoding skipped for {session_id} (missing AAAB/BBBA).")
            
            # 2 & 3. Rose Plots and Temporal Trajectories
            print(f"Running Rose Plots and Temporal Trajectories for {session_id}...")
            run_eye_consolidated_plotly(data_dir, session_id)
            
        except Exception as e:
            print(f"Error processing session {session_id}: {e}")


def main(args=None):
    data_dir = Path(__file__).parents[2] / "data"
    run_all_behavioral_analyses(data_dir)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
