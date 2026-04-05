# Figure 05 Description: LFP Time-Frequency Representation (TFR)

## Introduction to the LFP Time-Frequency Representation Figure

Figure 05, representing the LFP Time-Frequency Representation (TFR), is a crucial visualization within the "GAMMA PLAN" for LFP-centric omission analysis. Its primary function is to depict how the power of different frequency bands within the Local Field Potential (LFP) signal changes over time, relative to various experimental events. This figure serves to illustrate the oscillatory dynamics of local neuronal populations, providing insights into sensory processing, attention, and predictive coding, particularly in the context of visual stimulus presentation and omission.

From a neuroscientific standpoint, LFP oscillations in different frequency bands are believed to reflect distinct underlying neural processes. For instance, lower frequencies (delta, theta, alpha) are often associated with states of arousal, attention, or memory, while higher frequencies (beta, gamma) are frequently linked to active information processing, sensory binding, and cognitive computations. TFR analysis allows for a precise examination of when and at what frequencies these oscillatory power changes occur, offering a dynamic view of brain states and processing.

## Data Representation and Preprocessing

The data underpinning Figure 05 originates from `global_processed_data['lfp_tfr']`. This structured dictionary stores the processed Time-Frequency Representations for each session, area, and condition. Specifically, for each `session_id`, `area`, and `condition`, it contains:
1.  `'full_tfr'`: A 2D NumPy array representing the TFR, where one dimension is frequency and the other is time. These values are typically normalized power in decibels (dB).
2.  `'freqs'`: A 1D NumPy array listing the frequencies corresponding to the TFR data.
3.  `'times'`: A 1D NumPy array listing the time points (in milliseconds) corresponding to the TFR data.

The preprocessing steps leading to this TFR data are critical:

*   **LFP Epoching**: Raw LFP signals are first epoched around event onsets, providing trial-aligned segments of LFP.
*   **Bipolar Referencing**: To enhance spatial specificity and reduce common-mode noise, bipolar referencing is applied within each brain area. This involves subtracting the LFP of adjacent channels.
*   **Baseline Normalization**: The epoched LFP is then typically baseline-normalized, often by converting power values to decibels (dB) relative to a pre-stimulus baseline period. This allows for the comparison of power changes relative to a stable resting state.
*   **Time-Frequency Transform**: A time-frequency transform (e.g., using wavelets or short-time Fourier transform via Welch's method as in `scipy.signal.spectrogram`) is applied to the epoched LFP data. This decomposes the signal into its constituent frequencies over time.
*   **Averaging**: The TFRs from individual trials are then averaged (after appropriate normalization) to obtain the trial-averaged `full_tfr` for a given condition, smoothing out trial-to-trial variability and highlighting consistent event-related power modulations.

## Visual Elements - Part by Part Description

Figure 05 is presented as a heatmap, which is an ideal visualization for 2D data like TFRs where two continuous variables (time and frequency) influence a third (power). Each figure displays the TFR for a single combination of session, area, and condition, strictly adhering to the "GAMMA PLAN" aesthetic mandates.

### Structure and Layout:
The figure consists of a single heatmap plot per generated file. This focused display allows for detailed examination of the time-frequency dynamics within a specific context.

### Main Data Representation (Heatmap):
*   **Appearance**: The core of the figure is a color-coded grid (`plotly.graph_objects.Heatmap`). The colors represent the power (in dB) of LFP oscillations across a range of frequencies (y-axis) and over time (x-axis). The `colorscale='Jet'` (or another appropriate colormap) maps power values to a gradient of colors.
*   **Color Scale (`zmin`, `zmax`)**: The `zmin` and `zmax` parameters (e.g., `-3` and `3` dB) define the range of power values represented by the color scale. Keeping this range consistent across figures is crucial for meaningful comparisons, indicating, for example, a ±3 dB change from baseline.
*   **Colorbar**: A vertical colorbar to the right of the heatmap (`colorbar=dict(title="Power (dB)", thickness=20)`) provides a legend for the color mapping, clearly indicating what each color represents in terms of power in decibels.
*   **Representation**: This heatmap visually identifies specific frequency bands that increase or decrease in power at particular times relative to experimental events. For example, a bright yellow region in the gamma band after stimulus onset would indicate a strong increase in gamma power, suggesting active processing.

### Omission Patches (Vertical Rectangles):
*   **Appearance**: For conditions involving an omission (e.g., `RXRR`, `RRXR`, `RRRX`), a translucent pink vertical rectangle (`fillcolor=PINK, opacity=0.3, layer="below", line_width=0`) is drawn across the duration of the omitted stimulus. The opacity of 0.3 allows the underlying TFR data to still be discernible, while clearly marking the temporal window of interest.
*   **Representation**: This patch highlights the temporal window during which an expected stimulus was withheld. It draws the viewer's attention to this critical period, where "omission responses" (changes in TFR not driven by external sensory input) are expected to occur, often reflecting predictive processing.

### Event Markers (Vertical Dashed Lines):
*   **Appearance**: Thin, gray dashed vertical lines (`line_width=1, line_dash="dash", line_color=GRAY`) are overlaid on the heatmap. Each line is accompanied by a small annotation (`annotation_text=pres_key, annotation_position="top left", annotation_font_size=10, annotation_font_color=GRAY`).
*   **Representation**: These lines mark critical time points in the experimental trial sequence, such as the onset of fixation (`fx`), the primary stimulus (`p1`), and subsequent presentation or delay periods (`d1`, `d2`, etc.), as defined in `TIMING_MS`. They serve as vital temporal anchors, allowing for precise alignment and interpretation of oscillatory power changes relative to external events.

### Axes:
*   **X-axis (Time [ms])**: The horizontal axis represents time in milliseconds. Its range is dynamically set from `times.min()` to `times.max()`, ensuring the entire analyzed time window is visible. The x-axis title is clearly labeled "Time (ms)".
*   **Y-axis (Frequency [Hz])**: The vertical axis represents frequency in Hertz. Its range is dynamically set from `freqs.min()` to `freqs.max()`, covering the entire frequency spectrum analyzed. The y-axis title is clearly labeled "Frequency (Hz)".

### Titles and Labels:
*   **Main Title**: The figure has a prominent main title: `<b>TFR: Session {session_id}, Area {area}, Condition {condition}</b>`. This title provides essential context (the type of analysis, session ID, brain area, and experimental condition). The use of bold (`<b>`) enhances readability.
*   **Template**: The plotting template is set to `"plotly_white"`, ensuring a clean, white background for all elements.
*   **Font**: The font is specified as "Arial", size 12, with black color for all text elements, maintaining consistency across all figures in the "GAMMA PLAN".
*   **Backgrounds**: `plot_bgcolor` and `paper_bgcolor` are explicitly set to `WHITE`.

## Scientific Interpretation (Eye Model Perspective)

From the perspective of an "eye model" or a neuroscientist analyzing these TFRs, Figure 05 provides a wealth of information about local circuit activity.

### Expected Patterns:
1.  **Baseline Activity**: Before `p1` onset, the TFR should ideally show relatively stable power across frequencies, reflecting baseline brain activity. Any consistent deviations from zero dB (if baseline normalized) would indicate issues with baseline selection or normalization.
2.  **Sensory Evoked Oscillations**: Following the `p1` stimulus onset, a typical response in visual areas is an increase in gamma band power (e.g., 30-80 Hz, or even higher, depending on the area and species). This gamma increase is often accompanied by a decrease in lower frequency power (e.g., alpha/beta desynchronization). These patterns reflect active sensory processing and cortical engagement.
3.  **Sustained vs. Transient Responses**: Some power changes might be transient (e.g., a brief burst of gamma at stimulus onset), while others might be sustained throughout a stimulus presentation or delay period (e.g., sustained beta power during anticipation).
4.  **Omission-Related Modulations**: In omission conditions, the TFR is particularly informative. At the time an expected stimulus is omitted, an "omission response" might be observed. This could manifest as:
    *   **Gamma Burst**: An increase in gamma power, reflecting a prediction error or the brain's "surprise" at the missing input.
    *   **Beta Rebound**: A transient increase in beta power (13-30 Hz), often associated with inhibition or maintaining the current sensory state, which might occur after a prediction is violated.
    *   **Alpha/Theta Modulation**: Changes in alpha or theta power, potentially reflecting shifts in attention or memory encoding related to the unexpected event.
5.  **Area-Specific Dynamics**: Different brain areas are expected to show distinct TFR patterns. Early visual areas (V1) might have robust, short-latency sensory-evoked gamma, while higher-order areas (PFC, FEF) might show more complex and prolonged modulations in various bands, especially during cognitive aspects of the task or during omission.

### Anomaly Detection and Interesting Observations:
*   **Lack of Expected Modulation**: If sensory-evoked gamma is absent in a visual area following `p1`, it could indicate a problem with the stimulus, data acquisition, or a suppressed neural state.
*   **Persistent High Power (Artifacts)**: Broad, high-power bands across all frequencies, especially at harmonics of the line noise (e.g., 60 Hz, 120 Hz in North America), would suggest electrical noise or artifacts.
*   **Unexpected Latency/Duration**: Power changes occurring too early or too late, or persisting abnormally long, warrant investigation into potential processing delays or prolonged neural engagement.
*   **Cross-Condition Differences**: Comparing TFRs between omission conditions and full-stimulus control conditions is critical. Significant differences at the time of omission would highlight the brain's response to prediction errors.

### Cross-Figure Insights:
TFR patterns in Figure 05 are expected to correlate with other modalities:
*   An increase in gamma power in Figure 05 might coincide with an increase in population firing rate (Figure 03) in the same area, strengthening the interpretation of active local processing.
*   Strong beta power increases in Figure 05, particularly during delay or post-omission periods, might reflect inhibitory processes that could manifest as decreased firing rates in Figure 03.
These inter-figure comparisons are essential for a multi-modal understanding of brain function.

## Adherence to Mandates and Best Practices

Figure 05 strictly adheres to the "GAMMA PLAN" mandates:
*   **Plotly Only**: Uses `plotly.graph_objects` for all plotting.
*   **HTML/SVG Output**: Saved in both interactive HTML and static SVG formats.
*   **White Background**: `plotly_white` template ensures a clean, white background.
*   **Time Axis**: X-axis in milliseconds with event lines.
*   **Palette**: Uses `PINK` and `GRAY` for specific markers as mandated, while the TFR color scale is chosen for effective data representation.
*   **Naming Convention**: Adheres to `[condition]_full_tfr_[area]_[session_id]`.
*   **Scientific Rigor**: Clear axis labels, colorbar, and event markers ensure the figure is scientifically informative.

## Potential Improvements/Future Steps

*   **Statistical Masking**: Overlapping the TFR with statistically significant clusters (e.g., from cluster permutation testing against a baseline or a control condition) would greatly enhance its scientific value by highlighting areas of genuine, non-random power change.
*   **Dynamic Z-Range**: While a consistent `zmin`/`zmax` is good for comparison, sometimes dynamically adjusting it based on the data's range (or a robust percentile) could reveal subtle modulations, especially for conditions with weaker responses.
*   **Area-Specific Frequency Bands**: Tailoring the displayed frequency range or highlighting specific bands relevant to a particular brain area could make the figures even more informative.
*   **Multi-Session Averages**: Aggregating TFRs across multiple sessions for grand averages would improve the signal-to-noise ratio and provide more generalizable insights.

In summary, Figure 05 provides a powerful and detailed view of the oscillatory landscape of the LFP, enabling dynamic analysis of neural activity in response to complex experimental paradigms like visual omission. It is carefully constructed to meet both scientific requirements and aesthetic mandates of the "GAMMA PLAN."
