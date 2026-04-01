
import numpy as np
import pandas as pd
import scipy.io as sio
import os
import glob
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Aesthetic preferences
COLORS = ['red', 'blue', 'green', 'yellow', 'brown', 'pink', 'gray', 'purple', 'cyan', 'darkblue', 'darkred', 'darkgreen', 'darkgoldenrod', 'black']
BAND_COLORS = {'Theta': 'purple', 'Alpha': 'orange', 'Beta': 'red', 'Gamma': 'blue'}
TEMPLATE = 'plotly_white'

# Task Timing (Relative to P1 Onset at Sample 1000)
OMISSION_CONFIGS = {
    'p2': {'start': 531, 'end': 2062},
    'p3': {'start': 1562, 'end': 3093},
    'p4': {'start': 2593, 'end': 4124}
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

def identify_condition_from_number(condition_number):
    """Maps a condition number to its string name."""
    return CONDITION_MAP.get(condition_number, f"Unknown_Cond_{condition_number}")

def parse_bhv_eye_data(mat_path):
    """Direct parsing of .mat BHV file for eye DVA with condition grouping."""
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
            p1_idx = np.where(codes == 101)[0]
            if len(p1_idx) == 0:
                continue
            p1_time = times[p1_idx[0]]
            
            eye = trial.AnalogData.Eye
            
            # For EYE_DVA, we want the full trial
            start_ms = int(p1_time - 500)
            end_ms = int(p1_time + 4124)

            if end_ms < len(eye):
                win = eye[start_ms:end_ms, :]
                if cond_name not in results: results[cond_name] = []
                results[cond_name].append(win)
                    
        return results
    except Exception as e:
        print(f"Error parsing {mat_path}: {e}")
        return None

def add_time_markers(fig):
    time_markers = {
        'fx': -500, 'p1': 0, 'd1': 531, 'p2': 1031, 'd2': 1562,
        'p3': 2062, 'd3': 2593, 'p4': 3093, 'd4': 3624
    }
    for name, time in time_markers.items():
        fig.add_vline(x=time, line_dash="dash", line_color="black", annotation_text=name, annotation_position="top")

def add_omission_shade(fig, cond_name):
    omission_windows = {
        'p2': (1031, 1562),
        'p3': (2062, 2593),
        'p4': (3093, 3624)
    }
    
    omission_level = None
    if 'X' in cond_name:
        x_pos = -1
        try:
            x_pos = cond_name.index('X')
        except ValueError:
            pass
            
        if x_pos == 1:
            omission_level = 'p2'
        elif x_pos == 2:
            omission_level = 'p3'
        elif x_pos == 3:
            omission_level = 'p4'

    if omission_level:
        start, end = omission_windows[omission_level]
        fig.add_vrect(x0=start, x1=end, fillcolor="pink", opacity=0.5, layer="below")

def generate_fig_02(base_dir):
    """Generates EYE_DVA figures for all sessions."""
    output_dir = os.path.join(base_dir, 'fig_02_EYE_DVA_ALLSESSIONS')
    os.makedirs(output_dir, exist_ok=True)
    
    bhv_dir = r'D:\Analysis\Omission\local-workspace\data\behavioral'
    bhv_paths = glob.glob(os.path.join(bhv_dir, "*.mat"))
    
    all_sessions_data = {}

    for bhv_path in bhv_paths:
        sid = os.path.basename(bhv_path).split('_')[0]
        print(f"--- Processing Session: {sid} for Fig 02 ---")
        eye_data = parse_bhv_eye_data(bhv_path)
        if eye_data:
            for cond_name, group in eye_data.items():
                if cond_name not in all_sessions_data:
                    all_sessions_data[cond_name] = []
                all_sessions_data[cond_name].extend(group)

    for cond_name, group in all_sessions_data.items():
        print(f"  - Condition {cond_name}: {len(group)} trials across all sessions")
        group_arr = np.array(group)
        mu = np.mean(group_arr, axis=0)
        sem = np.std(group_arr, axis=0) / np.sqrt(len(group))
        var = np.mean(np.var(group_arr, axis=1), axis=0)
        time = np.arange(mu.shape[0]) - 500 # Centered on p1 onset

        fig = go.Figure()
        # X
        fig.add_trace(go.Scatter(x=time, y=mu[:, 0] + sem[:, 0], line_width=0, showlegend=False))
        fig.add_trace(go.Scatter(x=time, y=mu[:, 0] - sem[:, 0], fill='tonexty', fillcolor='red', opacity=0.5, line_width=0, showlegend=False))
        fig.add_trace(go.Scatter(x=time, y=mu[:, 0], name='Avg X', line=dict(color='red', width=3)))
        # Y
        fig.add_trace(go.Scatter(x=time, y=mu[:, 1] + sem[:, 1], line_width=0, showlegend=False))
        fig.add_trace(go.Scatter(x=time, y=mu[:, 1] - sem[:, 1], fill='tonexty', fillcolor='blue', opacity=0.5, line_width=0, showlegend=False))
        fig.add_trace(go.Scatter(x=time, y=mu[:, 1], name='Avg Y', line=dict(color='blue', width=3)))

        add_time_markers(fig)
        add_omission_shade(fig, cond_name)

        caption = f"Statistics (All Sessions):<br>Var(X): {var[0]:.4f}, Var(Y): {var[1]:.4f}<br>Mean(X): {np.mean(mu[:,0]):.4f}, Mean(Y): {np.mean(mu[:,1]):.4f}"
        fig.update_layout(
            title=f"Eye DVA: {cond_name} (All Sessions)", 
            template=TEMPLATE,
            xaxis_range=[-500, 4000],
            annotations=[
                go.layout.Annotation(
                    text=caption,
                    align='left',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=-0.1
                )
            ]
        )
        
        base_filename = f"{cond_name}_full_eyexy"
        fig.write_html(os.path.join(output_dir, f"{base_filename}.html"))
        fig.write_image(os.path.join(output_dir, f"{base_filename}.svg"))
        print(f"    -> Saved {base_filename}.html and .svg")

def generate_fig_03(base_dir):
    """Generates single unit spiking average per area figures."""
    output_dir = os.path.join(base_dir, 'fig_03_SPK_Firing_ALLSESSIONS')
    os.makedirs(output_dir, exist_ok=True)
    
    unit_info_path = r'D:\Analysis\Omission\local-workspace\data\checkpoints\enhanced_neuron_categories.csv'
    unit_info = pd.read_csv(unit_info_path)
    
    data_dir = r'D:\Analysis\Omission\local-workspace\data'
    
    conditions = list(np.unique(list(CONDITION_MAP.values())))
    
    for cond in conditions:
        print(f"--- Processing Condition: {cond} for Fig 03 ---")
        
        area_spikes = {}
        
        # Find all spike files for this condition
        spike_files = glob.glob(os.path.join(data_dir, f"ses*-units-*-spk-{cond}.npy"))
        
        for spike_file in spike_files:
            try:
                sid = os.path.basename(spike_file).split('-')[0].replace('ses', '')
                probe_id = int(os.path.basename(spike_file).split('-')[2].replace('probe', ''))
                
                spikes = np.load(spike_file)
                
                session_units = unit_info[(unit_info['session'] == int(sid)) & (unit_info['probe'] == probe_id)]
                
                for _, row in session_units.iterrows():
                    unit_idx = int(row['unit_idx'])
                    area = row['area']
                    
                    if area not in area_spikes:
                        area_spikes[area] = []
                    
                    # Assuming the order of units in the npy file matches the unit_idx
                    if unit_idx < spikes.shape[1]:
                         # (trials, time)
                        unit_spikes = spikes[:, unit_idx, :]
                        # average across trials
                        avg_unit_spikes = np.mean(unit_spikes, axis=0)
                        area_spikes[area].append(avg_unit_spikes)

            except Exception as e:
                print(f"Error processing {spike_file}: {e}")

        # Now, for each area, calculate the average firing rate
        fig = go.Figure()
        
        for area, spikes_list in area_spikes.items():
            if spikes_list:
                # average across units
                avg_area_spikes = np.mean(np.array(spikes_list), axis=0)
                time = np.arange(len(avg_area_spikes)) - 1000 # Centered on p1 onset
                
                # Convert to firing rate (spikes/sec) - assuming spike counts are in 1ms bins
                firing_rate = avg_area_spikes * 1000
                
                fig.add_trace(go.Scatter(x=time, y=firing_rate, name=area))

        add_time_markers(fig)
        add_omission_shade(fig, cond)

        caption = f"Average single unit spiking per area for condition {cond}."
        fig.update_layout(
            title=f"Spiking Rate: {cond} (All Sessions)",
            template=TEMPLATE,
            xaxis_title="Time (ms)",
            xaxis_range=[-1000, 4000],
            yaxis_title="Firing Rate (spikes/s)",
            yaxis_type="log",
            yaxis_range=[np.log10(0.1), np.log10(100.0)],
            annotations=[
                go.layout.Annotation(
                    text=caption,
                    align='left',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=-0.1
                )
            ]
        )
        
        base_filename = f"{cond}_full_spiking_avg_per_area"
        fig.write_html(os.path.join(output_dir, f"{base_filename}.html"))
        fig.write_image(os.path.join(output_dir, f"{base_filename}.svg"))
        print(f"    -> Saved {base_filename}.html and .svg")

def generate_fig_04(base_dir):
    """Generates rule-based classification figures of single units."""
    from scipy.stats import ttest_ind # Import ttest_ind here
    
    output_dir = os.path.join(base_dir, 'fig_04_SPK_rule_based_classification_ALLSESSIONS')
    os.makedirs(output_dir, exist_ok=True)

    unit_info_path = r'D:\Analysis\Omission\local-workspace\data\checkpoints\enhanced_neuron_categories.csv'
    unit_info = pd.read_csv(unit_info_path)
    data_dir = r'D:\Analysis\Omission\local-workspace\data'

    # Define time windows based on event markers (in ms, relative to data start at -1000ms from p1)
    epochs = {
        'p1': (1000, 1531),
        'd1': (1531, 2031),
        'd2': (2031, 2562),
        'p2_omission': (2031, 2562), # for AXAB, BXBA, RXRR
        'p3_omission': (2562, 3093), # for AAXB, BBXA, RRXR
        'p4_omission': (3093, 3624), # for AAAX, BBBX, RRRX
    }
    
    PRE_OMISSION_WINDOW_DUR = 200 # ms
    
    # Generate pre-omission windows dynamically
    pre_omission_epochs = {}
    for om_event, (om_start, om_end) in epochs.items():
        if 'omission' in om_event:
            pre_om_start = om_start - PRE_OMISSION_WINDOW_DUR
            pre_om_end = om_start
            pre_omission_epochs[f'pre_{om_event}'] = (pre_om_start, pre_om_end)

    omission_conditions = {
        'p2_omission': ['AXAB', 'BXBA', 'RXRR'],
        'p3_omission': ['AAXB', 'BBXA', 'RRXR'],
        'p4_omission': ['AAAX', 'BBBX', 'RRRX']
    }

    # 1. Load all spike data and classify all neurons
    print("--- Classifying neurons based on firing rate rules (Fig 04) ---")
    
    all_spike_data = {} # { (sid, probe, unit_idx): {cond: spikes} }
    
    spike_files = glob.glob(os.path.join(data_dir, "ses*-units-*-spk-*.npy"))

    for spike_file in spike_files:
        try:
            parts = os.path.basename(spike_file).split('-')
            sid = parts[0].replace('ses', '')
            probe_id = int(parts[2].replace('probe', ''))
            cond = parts[4].replace('.npy', '')
            
            spikes = np.load(spike_file) # (trials, units, time)

            session_units = unit_info[(unit_info['session'] == int(sid)) & (unit_info['probe'] == probe_id)]

            for _, row in session_units.iterrows():
                unit_idx = int(row['unit_idx'])
                if unit_idx < spikes.shape[1]:
                    key = (sid, probe_id, unit_idx)
                    if key not in all_spike_data:
                        all_spike_data[key] = {}
                    # average across trials -> (time)
                    all_spike_data[key][cond] = spikes[:, unit_idx, :] # Keep trial dimension for t-test
        except Exception as e:
            print(f"Error loading {spike_file}: {e}")
            
    # 2. Perform classification
    neuron_classifications = {} # { (sid, probe, unit_idx): 'class' }

    for unit_key, cond_spikes in all_spike_data.items():
        
        # Default classification is Null
        classification = 'Null'
        
        # Check for low firing rate first
        if 'RRRR' in cond_spikes:
            # entire trial average firing rate, converted to spikes/sec
            # Use mean across trials and time
            avg_rate_s = np.mean(cond_spikes['RRRR']) * 1000
            if avg_rate_s < 1:
                neuron_classifications[unit_key] = 'Null'
                continue # Skip to next neuron

        # Stimulus response (use a non-omission condition like RRRR)
        p1_rates_trials = []
        d1_rates_trials = []
        d2_rates_trials = []
        
        if 'RRRR' in cond_spikes:
            # Calculate mean rate per trial for comparison
            p1_rates_trials = np.mean(cond_spikes['RRRR'][:, epochs['p1'][0]:epochs['p1'][1]], axis=1)
            d1_rates_trials = np.mean(cond_spikes['RRRR'][:, epochs['d1'][0]:epochs['d1'][1]], axis=1)
            d2_rates_trials = np.mean(cond_spikes['RRRR'][:, epochs['d2'][0]:epochs['d2'][1]], axis=1)

        stim_pos = (np.mean(p1_rates_trials) > np.mean(d1_rates_trials)) or (np.mean(p1_rates_trials) > np.mean(d2_rates_trials))
        stim_neg = (np.mean(p1_rates_trials) < np.mean(d1_rates_trials)) or (np.mean(p1_rates_trials) < np.mean(d2_rates_trials))

        # Omission response
        om_pos = False
        om_neg = False
        
        p1d1_avg_rate_mean = (np.mean(p1_rates_trials) + np.mean(d1_rates_trials)) / 2

        for om_epoch_name, om_conds in omission_conditions.items():
            for cond in om_conds:
                if cond in cond_spikes:
                    # Omission vs p1-d1 average comparison
                    om_rates_trials = np.mean(cond_spikes[cond][:, epochs[om_epoch_name][0]:epochs[om_epoch_name][1]], axis=1)
                    if np.mean(om_rates_trials) > p1d1_avg_rate_mean:
                        om_pos = True
                    if np.mean(om_rates_trials) < p1d1_avg_rate_mean:
                        om_neg = True

                    # Statistical test for peak/dip during omission relative to pre-omission baseline
                    pre_om_start, pre_om_end = pre_omission_epochs[f'pre_{om_epoch_name}']
                    
                    pre_om_rates_trials = np.mean(cond_spikes[cond][:, pre_om_start:pre_om_end], axis=1)
                    
                    # Ensure enough data points for t-test
                    if len(pre_om_rates_trials) > 1 and len(om_rates_trials) > 1:
                        stat, pval = ttest_ind(om_rates_trials, pre_om_rates_trials)
                        
                        if pval < 0.05:
                            if np.mean(om_rates_trials) > np.mean(pre_om_rates_trials):
                                om_pos = True
                            elif np.mean(om_rates_trials) < np.mean(pre_om_rates_trials):
                                om_neg = True

        # Assign a single class based on priority
        if stim_pos:
            classification = 'Stimulus Positive'
        elif stim_neg:
            classification = 'Stimulus Negative'
        elif om_pos:
            classification = 'Omission Positive'
        elif om_neg:
            classification = 'Omission Negative'
        
        neuron_classifications[unit_key] = classification


    # 3. Aggregate spikes by class and plot
    conditions_to_plot = list(np.unique(list(CONDITION_MAP.values())))
    
    for cond in conditions_to_plot:
        
        classified_spikes = {
            'Stimulus Positive': [], 'Stimulus Negative': [],
            'Omission Positive': [], 'Omission Negative': [], 'Null': []
        }

        for unit_key, spikes_by_cond in all_spike_data.items():
            if cond in spikes_by_cond:
                classification = neuron_classifications.get(unit_key, 'Null')
                
                # Use the trial-averaged data for plotting
                avg_spikes_for_plotting = np.mean(spikes_by_cond[cond], axis=0)
                classified_spikes[classification].append(avg_spikes_for_plotting)

        fig = go.Figure()
        
        for classification, spike_list in classified_spikes.items():
            if spike_list:
                avg_spikes = np.mean(np.array(spike_list), axis=0)
                firing_rate = avg_spikes * 1000 # to spikes/sec
                time = np.arange(len(firing_rate)) - 1000

                fig.add_trace(go.Scatter(x=time, y=firing_rate, name=f'{classification} ({len(spike_list)} units)'))

        add_time_markers(fig)
        add_omission_shade(fig, cond)
        
        fig.update_layout(
            title=f"Rule-based Neuron Classes for Condition: {cond}",
            xaxis_title="Time (ms)",
            xaxis_range=[-1000, 4000],
            yaxis_title="Firing Rate (spikes/s)",
            yaxis_type="log",
            yaxis_range=[np.log10(0.1), np.log10(100.0)],
            template=TEMPLATE
        )
        
        base_filename = f"{cond}_rule_based_classification"
        fig.write_html(os.path.join(output_dir, f"{base_filename}.html"))
        fig.write_image(os.path.join(output_dir, f"{base_filename}.svg"))
        print(f"    -> Saved {base_filename}.html and .svg for condition {cond}")




def generate_fig_05(base_dir):
    """Generates LFP power trace figures for omission conditions."""
    import h5py
    output_dir = os.path.join(base_dir, 'fig_05_LFP_dB_EXT_ALLSESSIONS')
    os.makedirs(output_dir, exist_ok=True)

    lfp_dir = r'D:\Analysis\Omission\local-workspace\data'
    lfp_files = glob.glob(os.path.join(lfp_dir, "lfp_by_area_ses-*.h5"))

    omission_groups = {
        'p2': ('d1-p2-d2', ['AXAB', 'BXBA', 'RXRR']),
        'p3': ('d2-p3-d3', ['AAXB', 'BBXA', 'RRXR']),
        'p4': ('d3-p4-d4', ['AAAX', 'BBBX', 'RRRX'])
    }
    
    time_windows = {
        'd1-p2-d2': (531, 2062),
        'd2-p3-d3': (1562, 3093),
        'd3-p4-d4': (2593, 4124)
    }

    for p_level, (win_name, conditions) in omission_groups.items():
        print(f"--- Processing Omission Level: {p_level} for Fig 05 ---")
        
        area_data = {}

        for lfp_file in lfp_files:
            try:
                with h5py.File(lfp_file, 'r') as f:
                    for area_key in f.keys():
                        areas = area_key.split(',')
                        for area in areas:
                            area = area.strip()
                            if area not in area_data:
                                area_data[area] = {cond: [] for cond in conditions}
                            
                            for cond in conditions:
                                if cond in f[area_key]:
                                    data = f[f'{area_key}/{cond}'][:]
                                    area_data[area][cond].append(data)
            except Exception as e:
                print(f"Error reading {lfp_file}: {e}")

        for area, cond_data in area_data.items():
            
            fig = make_subplots(rows=len(conditions), cols=1, subplot_titles=conditions)
            
            for i, (cond, data_list) in enumerate(cond_data.items()):
                if data_list:
                    # Reshape 2D arrays to 3D
                    reshaped_data_list = []
                    for arr in data_list:
                        if arr.ndim == 2:
                            reshaped_data_list.append(arr[np.newaxis, :, :])
                        else:
                            reshaped_data_list.append(arr)

                    # Pad arrays to the same length
                    max_len = max(arr.shape[1] for arr in reshaped_data_list)
                    padded_data_list = []
                    for arr in reshaped_data_list:
                        pad_width = max_len - arr.shape[1]
                        padded_arr = np.pad(arr, ((0, 0), (0, pad_width), (0, 0)), 'constant')
                        padded_data_list.append(padded_arr)

                    # (sessions, trials, time, freq)
                    all_data = np.vstack(padded_data_list)
                    
                    # (trials, time, freq)
                    avg_data = np.mean(all_data, axis=0)
                    
                    start, end = time_windows[win_name]
                    
                    # (time, freq)
                    power_trace = avg_data[start:end, :]
                    
                    time = np.arange(power_trace.shape[0])
                    freqs = np.arange(power_trace.shape[1])
                    
                    fig.add_trace(go.Heatmap(z=power_trace.T, x=time, y=freqs, coloraxis = "coloraxis"), row=i+1, col=1)
                    add_omission_shade(fig, cond)


            if fig.data:
                fig.update_layout(
                    title_text=f"LFP Power Trace for Area {area} ({p_level})",
                    template=TEMPLATE,
                )
                fig.update_layout(coloraxis = {'colorscale':'Viridis'})


                base_filename = f"{area}_{p_level}_{win_name}_lfp_power_traces"
                fig.write_html(os.path.join(output_dir, f"{base_filename}.html"))
                fig.write_image(os.path.join(output_dir, f"{base_filename}.svg"))
                print(f"    -> Saved {base_filename}.html and .svg")


def generate_fig_06(base_dir):
    """Generates LFP power trace figures for averaged omission conditions."""
    import h5py
    output_dir = os.path.join(base_dir, 'fig_06_LFP_dB_EXT_ALLSESSIONS')
    os.makedirs(output_dir, exist_ok=True)

    lfp_dir = r'D:\Analysis\Omission\local-workspace\data'
    lfp_files = glob.glob(os.path.join(lfp_dir, "lfp_by_area_ses-*.h5"))

    omission_groups = {
        'p2': ['AXAB', 'BXBA', 'RXRR'],
        'p3': ['AAXB', 'BBXA', 'RRXR'],
    }
    
    bands = {
        'theta': (4, 8),
        'alpha': (8, 12),
        'beta': (12, 30),
        'gamma': (30, 80)
    }

    print(f"--- Processing Averaged Omissions for Fig 06 ---")
    
    area_data = {}

    for lfp_file in lfp_files:
        try:
            with h5py.File(lfp_file, 'r') as f:
                for area_key in f.keys():
                    areas = area_key.split(',')
                    for area in areas:
                        area = area.strip()
                        if area not in area_data:
                            area_data[area] = {level: [] for level in omission_groups.keys()}
                        
                        for level, conditions in omission_groups.items():
                            for cond in conditions:
                                if cond in f[area_key]:
                                    data = f[f'{area_key}/{cond}'][:]
                                    area_data[area][level].append(data)
        except Exception as e:
            print(f"Error reading {lfp_file}: {e}")
            
    for band_name, (band_start, band_end) in bands.items():
        print(f"  - Processing band: {band_name}")
        
        fig_traces = make_subplots(rows=1, cols=1)
        fig_sorted = make_subplots(rows=1, cols=1)
        
        power_changes = {}

        for area, level_data in area_data.items():
            
            p2_data = level_data.get('p2', [])
            p3_data = level_data.get('p3', [])

            if p2_data and p3_data:
                
                all_p2_data = [d[np.newaxis, :, :] if d.ndim == 2 else d for d in p2_data]
                all_p3_data = [d[np.newaxis, :, :] if d.ndim == 2 else d for d in p3_data]

                max_len_p2 = max(arr.shape[1] for arr in all_p2_data)
                padded_p2 = [np.pad(arr, ((0, 0), (0, max_len_p2 - arr.shape[1]), (0, 0)), 'constant') for arr in all_p2_data]

                max_len_p3 = max(arr.shape[1] for arr in all_p3_data)
                padded_p3 = [np.pad(arr, ((0, 0), (0, max_len_p3 - arr.shape[1]), (0, 0)), 'constant') for arr in all_p3_data]

                avg_p2 = np.mean(np.vstack(padded_p2), axis=0)
                avg_p3 = np.mean(np.vstack(padded_p3), axis=0)

                # Assuming freqs are the same for both
                avg_omission = (avg_p2[:min(len(avg_p2), len(avg_p3))] + avg_p3[:min(len(avg_p2), len(avg_p3))]) / 2
                
                band_power = np.mean(avg_omission[:, band_start:band_end], axis=1)
                
                time = np.arange(len(band_power))
                
                sem = np.std(avg_omission[:, band_start:band_end], axis=1) / np.sqrt(avg_omission.shape[0])

                fig_traces.add_trace(go.Scatter(x=time, y=band_power, name=area))
                fig_traces.add_trace(go.Scatter(x=time, y=band_power + 2 * sem, line_width=0, showlegend=False))
                fig_traces.add_trace(go.Scatter(x=time, y=band_power - 2 * sem, fill='tonexty', line_width=0, showlegend=False))

                baseline_power = np.mean(band_power[:100])
                power_change = np.mean(band_power[100:]) - baseline_power
                power_changes[area] = power_change

        sorted_areas = sorted(power_changes.keys(), key=lambda k: power_changes[k], reverse=True)
        sorted_power_changes = [power_changes[area] for area in sorted_areas]
        
        fig_sorted.add_trace(go.Bar(x=sorted_areas, y=sorted_power_changes))

        fig_traces.update_layout(title=f"LFP Power Trace ({band_name}, p2/p3 avg)", template=TEMPLATE)
        fig_sorted.update_layout(title=f"Sorted Power Change ({band_name}, p2/p3 avg)", template=TEMPLATE)

        fig_traces.write_html(os.path.join(output_dir, f"p2_p3_avg_{band_name}_lfp_power_traces.html"))
        fig_traces.write_image(os.path.join(output_dir, f"p2_p3_avg_{band_name}_lfp_power_traces.svg"))
        
        fig_sorted.write_html(os.path.join(output_dir, f"p2_p3_avg_{band_name}_sorted_area_power.html"))
        fig_sorted.write_image(os.path.join(output_dir, f"p2_p3_avg_{band_name}_sorted_area_power.svg"))

def main():
    base_output_dir = r'D:\Analysis\Omission\local-workspace\figures\oglo'
    generate_fig_02(base_output_dir)
    generate_fig_03(base_output_dir)
    generate_fig_04(base_output_dir)
    generate_fig_05(base_output_dir)
    generate_fig_06(base_output_dir)

if __name__ == '__main__':
    main()
