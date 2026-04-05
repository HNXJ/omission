# Figure 06 Description: LFP Band Power Summary

## Introduction to the LFP Band Power Summary Figure

Figure 06, titled "LFP Band Power Summary," is a pivotal visualization within the "GAMMA PLAN" for LFP-centric omission analysis. Its primary goal is to present the temporal dynamics of power within predefined, physiologically relevant LFP frequency bands (e.g., Delta, Theta, Alpha, Beta, Gamma) across different brain areas. This figure, distinct from the full TFR heatmap, offers a more direct and quantitative view of band-limited power changes, making it ideal for comparing specific oscillatory activities over time and across different cortical regions. It directly addresses questions about the engagement of various oscillatory mechanisms in sensory processing, predictive coding, and the response to unexpected events like omissions.

From a neuroscientific perspective, summarizing LFP power by discrete frequency bands provides a simplified yet powerful representation of brain activity. Each band is often associated with distinct neural computations and cognitive states. For instance, Beta oscillations (13-30 Hz) are frequently implicated in maintaining current cognitive states, motor control, and predictive coordination, while Gamma oscillations (>30 Hz) are linked to active processing, attention, and sensory binding. By plotting the mean and statistical error (SEM) of these band powers, Figure 06 allows for robust quantitative comparisons and identification of significant modulations.

## Data Representation and Preprocessing

The data underpinning Figure 06 originates from `global_processed_data['lfp_band_power']`. This structured dictionary stores processed band power statistics for each session, area, condition, and presentation key. Specifically, for each `session_id`, `area`, `condition`, `band_name`, and `pres_key`, it contains:
1.  `'mean'`: A NumPy array representing the mean band power time series (in dB), averaged across trials.
2.  `'sem'`: A NumPy array representing the standard error of the mean for the band power time series.
3.  `'n_trials'`: The number of trials used for the averaging.
4.  `'time_series'`: The full time series of the mean band power for plotting.

The preprocessing steps that generate this data are crucial for its accuracy and interpretability:

*   **LFP Epoching, Bipolar Referencing, Baseline Normalization**: These initial steps are identical to those for TFR (Figure 05). Raw LFP is epoched, bipolar-referenced within areas, and baseline-normalized to produce signals ready for spectral analysis.
*   **Trial-Level TFR and Band Power Computation**: Unlike the full TFR for Figure 05, the data for Figure 06 is derived from computing TFR and then extracting band-limited power for *each individual trial*. This is critical because calculating the Standard Error of the Mean (SEM) requires a distribution of values (i.e., trial-to-trial variability) at each time point. The `_compute_trial_tfr_and_band_power` helper function within `run-lfp-analysis-pipeline.py` is specifically designed for this purpose.
*   **Band Definition**: Power is averaged within predefined frequency ranges for each band (e.g., Beta=(13,30) Hz, Gamma=(30,80) Hz), as specified by the `BANDS` dictionary in `lfp_constants.py`.
*   **Mean and SEM Calculation**: For each band, area, and condition, the mean and SEM of the trial-level band power are calculated across all trials for the entire time course. This ensures a robust measure of central tendency and variability.
*   **Handling NaNs**: The code explicitly handles NaN values, particularly when calculating SEM for areas with insufficient trials or when filtering data.

## Visual Elements - Part by Part Description

Figure 06 is a multi-subplot figure, organized to display the temporal evolution of various LFP frequency bands. It provides a direct comparison of oscillatory activity across different brain regions and is strictly compliant with the "GAMMA PLAN" aesthetic mandates.

### Structure and Layout:
The figure employs `plotly.subplots.make_subplots` to arrange plots vertically. Each row represents a distinct frequency band (e.g., Delta, Theta, Alpha, Beta, Gamma). The subplots share a common x-axis (time), facilitating direct temporal comparison across bands. `vertical_spacing` is optimized to ensure clear separation and readability. Each subplot row is titled with the name of the band (e.g., "Beta Band Power"). The `height` of the figure dynamically adjusts to accommodate the number of bands being plotted.

### Main Traces (Mean Band Power):
*   **Appearance**: Each brain area's mean band power is plotted as a solid line (`mode='lines'`). The line color (`line=dict(color=color, width=2)`) is assigned based on a predefined `area_colors` dictionary (e.g., `V1` in Gold, `V4` in Violet, `FEF` in Teal). These colors adhere to the project's palette mandates (`GOLD`, `VIOLET`, `TEAL` from `lfp_constants.py`).
*   **Representation**: These lines depict the trial-averaged, baseline-normalized power (in dB) within a specific frequency band for a given brain area, showing how this activity evolves over the course of an experimental trial.

### Error Bands (±SEM):
*   **Appearance**: Surrounding each mean band power line is a shaded region (`fill='toself'`). The `fillcolor` is a semi-transparent version of the area's main color (e.g., `color.replace(')', ', 0.2)').replace('rgb', 'rgba')`). This transparency (0.2 opacity) allows multiple error bands to be overlaid without excessive clutter, and for underlying event markers to be visible.
*   **Representation**: This shaded area represents the `±1 SEM` (unless a different `sem_multiplier` is applied for figure generation, but for band power summaries, ±1 SEM is typical for showing variability). It indicates the variability of the mean band power estimate across trials. It provides a measure of statistical confidence, showing the range within which the true population mean is likely to fall.

### Event Markers (Vertical Dashed Lines):
*   **Appearance**: Thin, gray dashed vertical lines (`line_width=1, line_dash="dash", line_color=GRAY`) are overlaid on each subplot. Each line is accompanied by a small annotation (`annotation_text=pres_key, annotation_position="top left", annotation_font_size=10, annotation_font_color=GRAY`) placed at the top left.
*   **Representation**: These lines mark critical temporal points in the experimental sequence (e.g., `fx` for fixation, `p1` for primary stimulus onset). As defined in `TIMING_MS` from `lfp_constants.py`, they provide essential temporal context, allowing the viewer to precisely align observed power changes with experimental events.

### Axes:
*   **X-axis (Time [ms])**: The horizontal axis represents time in milliseconds. It is shared across all subplots, ensuring consistent temporal alignment. The x-axis title is clearly labeled "Time (ms)" at the bottom of the figure.
*   **Y-axis (Normalized Power)**: The vertical axis represents the normalized band power, typically in decibels (dB). Each subplot has its own y-axis, titled "Normalized Power". The range is automatically scaled by Plotly to fit the data, ensuring optimal visualization of power changes for each band.

### Titles and Labels:
*   **Main Title**: The figure boasts a prominent main title: `<b>Band Power Summary: Session {session_id}</b>`. This title provides immediate context regarding the session being analyzed.
*   **Subplot Titles**: Each row/subplot is clearly titled (e.g., "Delta Band Power", "Beta Band Power"), indicating the specific frequency band being displayed.
*   **Legend**: A comprehensive legend is displayed, typically at the top of the figure. It indicates which color corresponds to which brain area (e.g., "V1 Mean", "V4 Mean"). The legend is designed to appear only once for the first subplot to avoid redundancy, enhancing clarity.
*   **Aesthetic Mandates**: The figure rigidly adheres to the "GAMMA PLAN" aesthetic mandates, including the `"plotly_white"` template, "Arial" font, and specified black text color. `plot_bgcolor` and `paper_bgcolor` are explicitly set to `WHITE`.

## Scientific Interpretation (Eye Model Perspective)

From the perspective of an "eye model" or an experienced neuroscientist, Figure 06 is an invaluable tool for dissecting the temporal interplay of different oscillatory rhythms across brain regions in response to the task.

### Expected Patterns:
1.  **Baseline Stability**: Similar to firing rates, baseline power (prior to `fx` and `p1`) in each band should ideally be stable. Deviations could indicate issues or a non-stationary baseline.
2.  **Sensory-Evoked Responses**:
    *   **Gamma (30-80+ Hz)**: An increase in gamma power, often sharp and transient, is expected in visual areas (V1, V4) immediately following `p1` (sensory stimulus onset). This is associated with local processing of sensory information.
    *   **Beta (13-30 Hz)**: Often, a *decrease* in beta power (desynchronization) is seen during active processing (e.g., during stimulus presentation), followed by a "rebound" (increase) after stimulus offset or during periods of expectation or motor preparation. Beta is strongly linked to sensorimotor processing and maintaining the current state.
    *   **Alpha (8-12 Hz)**: Decreases in alpha power (desynchronization) are typically associated with increased cortical excitability and attention, especially in visual areas when visual stimuli are present or expected.
    *   **Theta (4-8 Hz)**: Theta power might increase during memory tasks, spatial navigation, or periods of high cognitive load. Its role in purely visual tasks might be more subtle or related to attentional shifts.
3.  **Omission-Specific Modulations**: The response to an omitted stimulus is a key focus. In the pink-shaded omission window:
    *   **Prediction Error**: We might observe a transient gamma burst (similar to a sensory response but without physical input) reflecting a "prediction error" signal, as the brain detects a mismatch between predicted and actual sensory input.
    *   **Beta Rebound/Increase**: A prominent beta power increase during the omission period could signify a top-down signal reflecting the maintenance of an internal model or an inhibitory process to suppress incorrect predictions. This is a common finding in predictive coding frameworks.
    *   **Alpha/Theta**: Modulations in alpha or theta during omission could reflect increased attentional engagement or memory retrieval processes trying to resolve the unexpected event.
4.  **Area-Specific Dynamics**: Power changes are highly dependent on the brain area. Early visual areas (V1, V2) might show strong, short-latency sensory-evoked responses. Higher-order areas (MT, PFC, FEF) might exhibit more complex, longer-latency, or sustained modulations, reflecting their role in higher cognitive functions and integration.
5.  **Hierarchical Processing**: Differences in the latency or magnitude of band power changes across a hierarchy of areas (e.g., V1 to PFC) can reveal insights into feedforward and feedback processing.

### Anomaly Detection and Interesting Observations:
*   **No Expected Modulation**: The absence of a strong gamma response in visual cortex to `p1` or an omission could indicate functional impairment or an artifactual issue.
*   **Excessive Noise**: Jittery or highly variable mean traces (large SEM) might point to insufficient trials, highly variable neural responses, or noise in the data.
*   **Persistent High Power (Artifacts)**: Flat, high-power lines across all bands could indicate saturated signals or persistent noise.
*   **Unexpected Latency**: Band power changes that are uncharacteristically early or late could indicate altered processing speed.
*   **Inverse Relationships**: Observing a decrease in one band (e.g., alpha) concurrent with an increase in another (e.g., gamma) is a common and informative finding, suggesting a shift in neural processing modes.

### Cross-Figure Insights:
Figure 06's findings are critically informed by and inform other figures:
*   Strong gamma band power increases in Figure 06, especially around `p1` or during omission, should correlate with increases in population firing rates (Figure 03) in the same area.
*   Persistent beta power in Figure 06 during certain periods might align with a decrease in firing rate (Figure 03), indicative of inhibitory control.
*   The TFR heatmap (Figure 05) provides the broadband context from which these specific band power plots are derived. Figure 06 offers a more focused, quantitative summary of key bands from Figure 05.

## Adherence to Mandates and Best Practices

Figure 06 strictly adheres to the "GAMMA PLAN" mandates:
*   **Plotly Only**: Uses `plotly.graph_objects` for all plotting elements.
*   **HTML/SVG Output**: Generated in both interactive HTML and static SVG formats.
*   **White Background**: `plotly_white` template ensures a clean, white background.
*   **Error Representation**: Clearly displays `±SEM` as a shaded region (with 0.2 opacity).
*   **Time Axis**: X-axis in milliseconds with event lines.
*   **Palette**: Uses `GOLD`, `VIOLET`, `TEAL`, `PINK`, `GRAY`, and `BLACK` for area-specific lines, omission patches, event lines, and text, respectively, as mandated.
*   **Naming Convention**: Adheres to `ALL_band_summary_[session_id]`.
*   **Scientific Rigor**: The use of trial-level data for SEM calculation, clear labeling, and adherence to color codes reflects robust scientific plotting.

## Potential Improvements/Future Steps

*   **Statistical Overlays**: Incorporating statistical significance indicators (e.g., from cluster permutation testing) directly on the plots would greatly enhance their interpretive power, highlighting where changes are statistically robust.
*   **Merging Omission Conditions**: The current implementation plots for a single condition (e.g., 'RRRR'). A future step is to refine Figure 06 to merge relevant omission conditions for direct comparison (e.g., `RXRR` vs. `RRRR` to show omission effect) in a multi-session aggregated context.
*   **Area Ranking**: Implementing an area ranking system based on the magnitude or latency of responses could help organize the subplots in a scientifically meaningful order, rather than just alphabetical.
*   **Dynamic Y-Axis Range**: While auto-scaling works, sometimes a fixed or adaptive but consistent y-axis range across subplots of the same band (e.g., all Beta plots) can improve comparability.
*   **Interactive Controls**: For HTML output, adding interactive controls for selecting specific bands or areas could enhance exploratory data analysis.

In conclusion, Figure 06 provides a highly informative summary of LFP band power dynamics, meticulously designed to meet the rigorous scientific and aesthetic standards of the "GAMMA PLAN." It is a vital tool for understanding the oscillatory underpinnings of neural processing during complex tasks.
