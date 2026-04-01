import numpy as np
import pandas as pd
import scipy.io as sio
import os
import glob
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Condition mapping
CONDITION_MAP = {
    1: 'AAAB', 2: 'AAAB', 3: 'AXAB', 4: 'AAXB', 5: 'AAAX',
    6: 'BBBA', 7: 'BBBA', 8: 'BXBA', 9: 'BBXA', 10: 'BBBX',
    **{i: 'RRRR' for i in range(11, 27)},
    **{i: 'RXRR' for i in range(27, 35)},
    35: 'RRXR', 37: 'RRXR', 39: 'RRXR', 41: 'RRXR',
    36: 'RRRX', 38: 'RRRX', 40: 'RRRX', 42: 'RRRX',
    **{i: 'RRRX' for i in range(43, 51)},
}

def identify_condition_from_number(condition_number):
    return CONDITION_MAP.get(condition_number, f"Unknown_Cond_{condition_number}")

def pixels_to_dva(pixels, screen_width_cm=120, screen_distance_cm=108, screen_resolution_px=1920):
    """Converts pixel values to degrees of visual angle."""
    pixels_per_cm = screen_resolution_px / screen_width_cm
    cm = pixels / pixels_per_cm
    dva = np.rad2deg(np.arctan(cm / screen_distance_cm))
    return dva

def parse_full_trial_eye_data(mat_path):
    """Parses .mat BHV file for full trial eye DVA, all conditions."""
    try:
        mat = sio.loadmat(mat_path, struct_as_record=False, squeeze_me=True)
        bhvUni = mat['bhvUni']
        results = {}
        
        for i, trial in enumerate(bhvUni):
            if trial.TrialError != 0:
                continue
            
            cond_name = identify_condition_from_number(trial.Condition)
            codes = trial.BehavioralCodes.CodeNumbers
            times = trial.BehavioralCodes.CodeTimes
            
            # Find fixation start (code 9) and trial end
            fx_on_idx = np.where(codes == 9)[0]
            if len(fx_on_idx) == 0:
                continue
            
            start_time = int(times[fx_on_idx[0]])
            end_time = int(trial.AnalogData.Eye.shape[0]) # Take the whole trial length

            eye_trace_pixels = trial.AnalogData.Eye[start_time:end_time, :]
            eye_trace_dva = pixels_to_dva(eye_trace_pixels)
            
            if cond_name not in results:
                results[cond_name] = []
            results[cond_name].append(eye_trace_dva)
        
        return results
    except Exception as e:
        print(f"Error parsing {mat_path}: {e}")
        return None

def generate_fig02():
    bhv_dir = r'D:\Analysis\Omission\local-workspace\data\behavioral'
    output_dir = r'D:\Analysis\Omission\local-workspace\figures\oglo\fig_02_EYE_DVA_ALLSESSIONS'
    os.makedirs(output_dir, exist_ok=True)
    
    bhv_paths = glob.glob(os.path.join(bhv_dir, "*bhv2.mat"))

    for mat_path in bhv_paths:
        session_id = os.path.basename(mat_path).split('_')[0]
        eye_data_by_condition = parse_full_trial_eye_data(mat_path)

        if not eye_data_by_condition:
            continue

        for cond_name, trials in eye_data_by_condition.items():
            # Pad trials to the same length for averaging
            max_len = max([len(t) for t in trials])
            if max_len == 0:
                continue
            padded_trials = [np.pad(t, ((0, max_len - len(t)), (0, 0)), 'constant', constant_values=np.nan) for t in trials]
            
            trials_arr = np.array(padded_trials)
            
            # Check data range
            if np.nanmax(np.abs(trials_arr)) > 10:
                print(f"WARNING: Session {session_id}, Cond {cond_name} has large eye data values (max: {np.nanmax(np.abs(trials_arr)):.2f} DVA).")

            mean_trace = np.nanmean(trials_arr, axis=0)
            sem_trace = np.nanstd(trials_arr, axis=0) / np.sqrt(trials_arr.shape[0])

            time_axis = np.arange(mean_trace.shape[0]) - 500

            fig = go.Figure()

            # Plot X trace
            fig.add_trace(go.Scatter(x=time_axis, y=mean_trace[:, 0] + sem_trace[:, 0], line_width=0, showlegend=False, name="X SEM Upper"))
            fig.add_trace(go.Scatter(x=time_axis, y=mean_trace[:, 0] - sem_trace[:, 0], fill='tonexty', fillcolor='rgba(255, 0, 0, 0.2)', line_width=0, showlegend=False, name="X SEM Lower"))
            fig.add_trace(go.Scatter(x=time_axis, y=mean_trace[:, 0], name='Average X Position', line=dict(color='red')))

            # Plot Y trace
            fig.add_trace(go.Scatter(x=time_axis, y=mean_trace[:, 1] + sem_trace[:, 1], line_width=0, showlegend=False, name="Y SEM Upper"))
            fig.add_trace(go.Scatter(x=time_axis, y=mean_trace[:, 1] - sem_trace[:, 1], fill='tonexty', fillcolor='rgba(0, 0, 255, 0.2)', line_width=0, showlegend=False, name="Y SEM Lower"))
            fig.add_trace(go.Scatter(x=time_axis, y=mean_trace[:, 1], name='Average Y Position', line=dict(color='blue')))
            
            # Add epoch rectangles
            epoch_times = {
                'fx': (-500, 0), 'p1': (0, 531), 'd1': (531, 1031),
                'p2': (1031, 1562), 'd2': (1562, 2062), 'p3': (2062, 2593),
                'd3': (2593, 3093), 'p4': (3093, 3624), 'd4': (3624, 4124)
            }
            colors = ['rgba(0, 255, 0, 0.2)', 'rgba(0, 0, 255, 0.2)']
            for i, (name, (start, end)) in enumerate(epoch_times.items()):
                fig.add_vrect(x0=start, x1=end, fillcolor=colors[i % 2], layer="below", line_width=0, annotation_text=name)

            # Add omission patch
            if 'X' in cond_name:
                omit_pos = cond_name.find('X')
                if omit_pos != -1:
                    p_start = epoch_times[f'p{omit_pos+1}'][0]
                    p_end = epoch_times[f'p{omit_pos+1}'][1]
                    fig.add_vrect(x0=p_start, x1=p_end, fillcolor="rgba(255, 0, 255, 0.2)", layer="below", line_width=0, annotation_text="omission")

            stats_text = f"Analyzed {len(trials)} correct trials. Mean eye position is calculated across trials. Shaded area represents SEM."
            fig.update_layout(
                title=f"Trial-Averaged Eye Position (DVA)<br>Session: {session_id} | Condition: {cond_name}",
                xaxis_title="Time relative to first presentation (ms)",
                yaxis_title="Eye Position (Degrees of Visual Angle)",
                template="plotly_white",
                legend_title="Traces",
                annotations=[dict(x=0.5, y=-0.25, showarrow=False, text=stats_text, xref="paper", yref="paper")]
            )
			
			# Save files
            base_filename = f"{session_id}_{cond_name}_full_eyexy"
            fig.write_html(os.path.join(output_dir, f"{base_filename}.html"))
            fig.write_image(os.path.join(output_dir, f"{base_filename}.svg"))
            print(f"  -> Saved {base_filename} for session {session_id}")
			
if __name__ == '__main__':
    generate_fig02()
