# Summary File 3: `run-lfp-analysis-pipeline.py` - Orchestration and Data Structure

## The Central Role of `run-lfp-analysis-pipeline.py`

The core of the "GAMMA PLAN" for LFP-centric omission analysis resides in the `run-lfp-analysis-pipeline.py` script. This script serves as the primary orchestrator, guiding the data through a multi-stage process that includes initial loading, preprocessing, laminar mapping, analysis of various modalities (LFP, spiking, MUA, behavioral), and finally, the generation of figures. Its design is modular, leveraging specialized functions from other modules like `lfp_io`, `lfp_events`, `lfp_preproc`, `lfp_laminar_mapping`, and `lfp_plotting_utils`. This modularity ensures maintainability, testability, and adherence to the project's architectural mandates.

## Design of the `global_processed_data` Structure

A critical component developed within `run-lfp-analysis-pipeline.py` is the `global_processed_data` dictionary. This nested dictionary serves as the central repository for all processed data across all sessions. Its design is meticulous, aiming to provide a highly organized and queryable structure that facilitates both within-session and cross-session analyses. The structure is designed to be queryable by `session_id`, `area`, `layer`, `condition`, `presentation_key`, and `modality`, enabling flexible data retrieval for various analyses and figure generations.

The top-level keys of `global_processed_data` correspond to different data modalities or types of information:

*   `lfp_tfr`: Stores Time-Frequency Representations (TFRs), primarily for the generation of Figure 05. It holds trial-averaged TFRs per session, area, and condition.
*   `lfp_band_power`: Stores aggregated band power statistics (mean, SEM, N) and the underlying time series data. This is crucial for Figure 06 and other band-specific analyses.
*   `spiking_firing_rate`: Stores processed spiking data, specifically the mean firing rate time series and their corresponding time bins per unit, area, layer, and condition, central to Figure 03.
*   `mua`: Stores Multi-Unit Activity (MUA) data, including epoched and averaged MUA across layers and conditions.
*   `behavioral_eye`: Stores eye-tracking behavioral data, such as averaged X/Y eye positions per condition and presentation window, for potential Figure 02 integration.
*   `session_metadata`: Stores essential metadata for each session, including `electrodes` (with laminar information), `units`, `omission_windows`, and `event_table`, providing a comprehensive context for each session's data.

This hierarchical structure is pivotal for managing the complexity of multi-modal neurophysiological data and for implementing the "GAMMA PLAN" requirements effectively.

## Step-by-Step Pipeline Orchestration within `run-lfp-analysis-pipeline.py`

The `run_lfp_pipeline` function iterates through each NWB (Neurodata Without Borders) file found in the specified `DATA_DIR`, processing each session sequentially. For each session, the following stages are executed:

### Stage 0: Initial Load & Validate

1.  **Session Loading**: `lfp_io.load_session(nwb_path)` is called to load the NWB file into a `session` dictionary, which is then augmented with the sampling frequency (`FS_LFP`).
2.  **Schema Validation (Step 1)**: `lfp_pipeline.validate_session_schema(session)` enforces data integrity, flagging any QC issues and ensuring that the NWB file conforms to expected standards. Sessions with missing LFP data are skipped.
3.  **Event Table Construction**: `lfp_events.build_event_table(session)` extracts experimental event timings and conditions, forming a DataFrame crucial for epoching.
4.  **Omission Window Definition (Step 2)**: `lfp_pipeline.build_omission_windows(event_table)` identifies and defines the precise timing of omission events based on the experimental design.

### New Stage: Laminar Mapping

This stage, detailed in Summary File 2, is integrated here to ensure that all LFP channels are assigned to cortical layers (`Superficial`, `L4`, `Deep`) before further analysis. This involves:

*   Iterating through each probe within the session.
*   Epoching LFP data for a robust condition (e.g., 'RRRR') to facilitate L4 crossover detection.
*   Calling `lfp_laminar_mapping.get_laminar_crossover` and `lfp_laminar_mapping.map_channels_to_layers` to update the `session["electrodes"]` DataFrame with layer information.

### Integration of Spiking Data (Units)

Spiking data from `session["units"]` is processed to extract firing rates. This involves:

1.  **Unit-Electrode Linkage**: Merging unit data with `session["electrodes"]` using `electrode_idx` or `peak_channel_id` to associate each unit with its brain area, probe, and crucially, its assigned cortical layer.
2.  **Firing Rate Calculation**: For each unit, and for each experimental condition:
    *   `_epoch_spike_times` is used to epoch and bin spike times relative to event onsets, converting them into trial-level binned spike counts.
    *   These binned counts are then converted into `firing_rate_per_trial` (Hz).
    *   The `mean_firing_rate_ts` (mean across trials) and corresponding `firing_rate_time_bins_ms` are calculated.
3.  **Storage in `global_processed_data`**: The `mean_firing_rate_ts` and `firing_rate_time_bins_ms` are stored in a nested structure: `global_processed_data['spiking_firing_rate'][session_id][unit_area][unit_layer][unit_id][cond]`.
4.  **Figure 03 Generation**: Crucially, after processing all spiking data for a session, `lfp_plotting_utils.create_population_firing_figure` is called for each condition, generating the population firing rate plots. This direct call ensures that figures are created as soon as the necessary data is available.

### Integration of Behavioral Data (Eye-tracking)

Eye-tracking data is loaded from session- and condition-specific NPY files (`ses<session_id>-behavioral-<CONDITION>.npy`) located in the `data/behavioral` directory. Mean X and Y eye positions are extracted for various presentation windows (`fx`, `p1`, `d1`, etc.) and stored in `global_processed_data['behavioral_eye']`.

### Integration of Multi-Unit Activity (MUA)

MUA is derived from the LFP signals:

1.  **Raw MUA Trace Computation**: For each LFP channel, `_compute_mua` applies bandpass filtering, rectification, and smoothing to the raw LFP to generate a 1D MUA trace.
2.  **Epoching and Aggregation**: These raw MUA traces are then epoched for each condition and averaged across channels within a specific area and layer.
3.  **Storage in `global_processed_data`**: The averaged MUA values for various presentation windows are stored in `global_processed_data['mua'][session_id][area][layer][cond][pres_key]`.

### Stage 1: Preprocessing & Epoching (LFP)

1.  **LFP QC (Step 3)**: `lfp_pipeline.run_lfp_qc` identifies and reports bad LFP channels (flat, noisy).
2.  **Bipolar Referencing**: `_apply_bipolar_ref_per_area` (a helper function within `run-lfp-analysis-pipeline.py`) groups LFP by area, sorts channels by depth, and applies bipolar referencing within each area, excluding bad channels.
3.  **Extract Matched Epochs (Step 4)**: `lfp_pipeline.extract_matched_epochs` segments the bipolar-referenced LFP into trial-aligned epochs based on the event table.
4.  **Normalize Epochs (Step 5)**: `lfp_pipeline.normalize_epochs` performs baseline normalization (dB) on the epoched LFP data.

### Stage 2: Time-Frequency Analysis (LFP)

1.  **Compute TFR per Condition (Step 6)**: `lfp_pipeline.compute_tfr_per_condition` computes the TFR for the normalized LFP data. The mean TFRs are stored in `global_processed_data['lfp_tfr']`.
2.  **Figure 05 Generation**: `lfp_plotting_utils.create_tfr_figure_per_condition` is called to generate TFR heatmap figures for each area and condition.
3.  **Compute Trial-Level Band Power**: `_compute_trial_tfr_and_band_power` (a new helper function) computes band power for each trial individually, enabling later calculation of SEM. These trial-level band powers are stored temporarily.
4.  **Populate `lfp_band_power`**: The trial-level band powers are then used to calculate mean, SEM, and N (number of trials) for each band, area, condition, and presentation window. This data, along with the averaged time series, is stored in `global_processed_data['lfp_band_power']`.
5.  **Figure 06 Generation**: `lfp_plotting_utils.create_band_summary_figure` is called to generate band power summary figures.

### Stage 3: Connectivity & Statistical Analysis (Placeholders)

This stage includes placeholders for future implementation of:
*   `compute_spectral_corr` (Step 8): Inter-area correlation matrices.
*   `compute_all_pairs_coherence` (Step 9): All-pairs coherence spectra.
*   `build_coherence_network_data` (Step 10): Adjacency matrices from coherence.
*   `compute_spectral_granger` (Step 11): Directional Granger causality.
*   `run_cluster_permutation` (Step 12): Cluster permutation statistics.
*   `aggregate_by_tier` (Step 13): Hierarchy tier aggregation.
*   `compute_post_omission_adapt` (Step 14): Post-omission adaptation analysis.

These steps often require multi-session aggregation, which is planned as a subsequent phase, and hence are currently represented by placeholder calls or dummy data generation.

### Stage 4: Output & Reproducibility (Step 15)

1.  **Write Analysis Manifest**: `lfp_pipeline.write_analysis_manifest` generates a JSON and CSV manifest summarizing analysis parameters and figure specifications, critical for reproducibility.
2.  **Save `global_processed_data`**: The entire `global_processed_data` dictionary, containing all processed information across all modalities for the current session, is serialized and saved as a `global_processed_data.pkl` file using `pickle`. This allows for efficient loading and further multi-session aggregation in subsequent analyses.

## Helper Functions within `run-lfp-analysis-pipeline.py`

Several helper functions were developed or refined directly within `run-lfp-analysis-pipeline.py` to support the pipeline's operations:

*   `_apply_bipolar_ref_per_area`: Groups raw LFP by area, sorts channels by depth, and applies bipolar referencing. This was a critical step in preprocessing to ensure clean signals for analysis.
*   `_epoch_lfp_data`: Extracts epoched LFP data for selected channels around specific event timings, used extensively for both laminar mapping and TFR/band power computations.
*   `_epoch_spike_times`: Extracts epoched and binned spike counts for single units, a foundational step for firing rate calculations. This function received a crucial fix to its time window filtering logic.
*   `_compute_mua`: Computes Multi-Unit Activity (MUA) from LFP by applying bandpass filtering, rectification, and smoothing, providing another important modality for analysis.
*   `_compute_trial_tfr_and_band_power`: This new helper function computes TFR and band power for each trial individually, which is essential for calculating accurate SEM and for later statistical analyses. It averages across channels within a trial before performing the time-frequency transform.

## Conclusion of Pipeline Orchestration and Data Structure

The `run-lfp-analysis-pipeline.py` script, with its meticulously designed `global_processed_data` structure and integration of numerous specialized helper functions, forms the backbone of the "GAMMA PLAN". It ensures that multi-modal neurophysiological data is processed, organized, and prepared for both immediate figure generation and future cross-session analyses. The modular approach taken here, coupled with robust data management, sets a strong foundation for deriving scientific insights from complex datasets. The next phase will delve deeper into the specific figure generation functions and their adherence to the project's aesthetic and scientific mandates.
