# Figure 03 Description: Population Firing Rate

## Introduction to the Population Firing Rate Figure

Figure 03, "Population Firing Rate," is a cornerstone visualization within the "GAMMA PLAN" for LFP-centric omission analysis. Its primary purpose is to illustrate the average firing dynamics of neuronal populations across different cortical areas in response to specific experimental conditions, with a particular emphasis on events surrounding visual stimuli and their omissions. This figure directly addresses the scientific question of how the average spiking activity of neurons within defined brain regions modulates over time, providing insights into sensory processing, predictive coding, and adaptation mechanisms in the context of an omission paradigm.

From a neuroscientific perspective, population firing rates are a fundamental measure of neural activity. They represent the collective output of many neurons and are often correlated with behavioral states, sensory encoding, and cognitive processes. By visualizing these rates over time, particularly with robust error estimates, we can infer the temporal precision and reliability of neural responses. The figure is designed to facilitate comparisons across different conditions and brain areas, revealing both commonalities and distinctions in population-level coding.

## Data Representation and Preprocessing

The data underpinning Figure 03 originates from `global_processed_data['spiking_firing_rate']`. This is a meticulously structured nested dictionary designed to store the processed spiking activity for each neuron. Specifically, for each `session_id`, `area`, `layer`, `unit_id`, and `condition`, it contains two key components:
1.  `'firing_rate_ts'`: A NumPy array representing the mean firing rate time series (in Hz) for a single unit, averaged across all trials of a given condition.
2.  `'time_bins_ms'`: A NumPy array representing the corresponding time points (in milliseconds) for the `firing_rate_ts`.

Before being plotted, this data undergoes several crucial preprocessing steps:

*   **Binning and Trial Averaging**: Individual spike times for each unit are first epoched around event onsets and then binned into discrete time windows (e.g., 50ms bins). The counts within these bins are converted to firing rates (Hz). For each unit, these trial-level firing rates are then averaged across all trials belonging to a specific condition to yield a single `firing_rate_ts`. This averaging process helps to extract the stimulus-evoked or event-related response, reducing trial-to-trial variability.
*   **Population Aggregation**: For a given `area` and `condition`, the `create_population_firing_figure` function aggregates the `firing_rate_ts` from *all* units identified within that area (across all layers). This involves stacking these individual unit time series into a 2D array, where each row represents a unit and each column represents a time point.
*   **Mean and Standard Error of the Mean (SEM) Calculation**: From this aggregated population data, the mean firing rate (`mean_fr`) and the standard error of the mean (`sem_fr`) are computed across all units at each time point. This provides a robust estimate of the population's central tendency and the variability around it. The `sem_multiplier` (typically 2, for ±2 SEM) is applied to these values.
*   **Smoothing**: A `smooth_fr` helper function, implementing a simple moving average filter, is applied to both the `mean_fr` and `sem_fr`. This smoothing step is critical for reducing high-frequency noise and making the underlying trends in population activity more discernible. While the current implementation uses a simple moving average, critical feedback suggests a Gaussian kernel would be more biophysically appropriate to avoid phase shifts and 'blocky' artifacts.
*   **Non-negativity Constraint**: The lower bound of the SEM band is explicitly constrained to be non-negative. This is a biologically informed constraint, as neuronal firing rates cannot be below zero.

## Visual Elements - Part by Part Description

Figure 03 is a multi-subplot figure designed to present population firing rates in an organized and interpretable manner, strictly adhering to the "GAMMA PLAN" aesthetic mandates.

### Structure and Layout:
The figure utilizes `plotly.subplots.make_subplots` to arrange multiple plots vertically, one for each "active" brain area that contains recorded units for the specific `condition`. The subplots share a common x-axis (time), which is essential for comparing temporal dynamics across areas. `vertical_spacing` is set to a small value (0.03) to maximize vertical space efficiency while maintaining readability. Each subplot is clearly labeled with the name of the brain area it represents.

### Main Traces (Mean Firing Rate):
*   **Appearance**: A solid black line (`line=dict(color=BLACK, width=2)`) plots the `mean_fr_s` (smoothed mean firing rate) over time. Black is chosen for its strong contrast and professional appearance, consistent with the "GAMMA PLAN" palette.
*   **Representation**: This line represents the average spiking activity of the entire neuronal population within a given brain area, averaged across trials and smoothed, providing a clear trajectory of population response.

### Error Bands (±SEM):
*   **Appearance**: A light gray shaded region (`fillcolor='rgba(128,128,128,0.3)'`) surrounds the mean firing rate line. This region is generated by plotting `np.concatenate([upper_bound, lower_bound[::-1]])`, where `upper_bound` is `mean_fr_s + sem_multiplier * sem_fr_s` and `lower_bound` is `mean_fr_s - sem_multiplier * sem_fr_s` (with non-negativity enforced).
*   **Representation**: This shaded area indicates the variability or uncertainty of the mean firing rate estimate. By default, it represents ±2 SEM, providing a 95% confidence interval for the population mean, assuming a normal distribution. The transparency (0.3 opacity) allows the underlying grid lines or other visual elements to remain subtly visible.

### Event Markers (Vertical Dashed Lines):
*   **Appearance**: Thin, gray dashed vertical lines (`line_width=1, line_dash="dash", line_color=GRAY`) are overlaid on each subplot. Each line is accompanied by a small annotation (`annotation_text=pres_key, annotation_position="top left", annotation_font_size=10, annotation_font_color=GRAY`).
*   **Representation**: These lines mark critical time points in the experimental trial sequence, such as the onset of fixation (`fx`), the primary stimulus (`p1`), and subsequent presentation or delay periods (`d1`, `d2`, etc.), as defined in `TIMING_MS`. They serve as important temporal anchors, allowing for precise alignment and interpretation of the neural responses relative to external events.

### Omission Patches (Vertical Rectangles):
*   **Appearance**: For conditions involving an omission (e.g., `RXRR`, `RRXR`, `RRRX`), a translucent pink vertical rectangle (`fillcolor=PINK, opacity=0.2, layer="below", line_width=0`) is drawn across the duration of the omitted stimulus.
*   **Representation**: This patch visually highlights the specific temporal window during which an expected stimulus was withheld. It is critical for analyzing "omission responses"—neural activity that occurs not due to sensory input, but due to the *absence* of expected input, a key phenomenon in predictive coding research. Placing it `layer="below"` ensures it does not obscure the mean firing rate or SEM traces.

### Axes:
*   **X-axis (Time [ms])**: The horizontal axis represents time in milliseconds. Its range is set by the `window_ms` parameter (e.g., `[-500, 4000]`), ensuring a consistent temporal context across all plots. The x-axis title is clearly labeled "Time [ms]" at the bottom of the figure.
*   **Y-axis (Firing Rate [Hz])**: The vertical axis represents the firing rate in Hertz (spikes per second). Each subplot has its own y-axis, titled "Firing Rate [Hz]". The range of the y-axis is automatically scaled by Plotly to fit the data in each subplot, but it always starts from zero due to the non-negativity constraint.

### Titles and Labels:
*   **Main Title**: The figure has a prominent main title: `<b>Fig 03: Population Firing Rate (Session {session_id}, Condition {condition})</b><br><sup>N = {total_units_in_plot} units | Mean ± {sem_multiplier}SEM | Template: White</sup>`. This title provides essential context (figure number, session, condition), key statistical information (total number of units, SEM multiplier), and reiterates the plotting template. The use of bold (`<b>`) and superscript (`<sup>`) enhances readability.
*   **Subplot Titles**: Each subplot is titled with the `area` name (e.g., "V1", "PFC"), clearly indicating the brain region represented in that trace.
*   **Legend**: A legend is displayed at the top of the figure, indicating what the black line and gray shaded region represent (e.g., "Area Condition Mean", "Area Condition SEM"). This is shown only once for the first subplot to avoid redundancy.

## Scientific Interpretation (Eye Model Perspective)

From the perspective of an "eye model" or an experienced neuroscientist, Figure 03 offers a rich tapestry of information about neural population dynamics.

### Expected Patterns:
1.  **Baseline Activity**: Prior to the `fx` (fixation onset) and `p1` (primary stimulus onset) markers, we expect to see a relatively stable "baseline" firing rate. This reflects the spontaneous activity of the population in the absence of task-relevant stimuli.
2.  **Sensory Evoked Response**: Following the `p1` marker (onset of the primary visual stimulus), a rapid increase in firing rate is typically expected in visually responsive areas (e.g., V1, V2, V4). This represents the "onset response" or "sensory evoked response." The latency, peak amplitude, and duration of this response would be key observations.
3.  **Sustained Activity**: Depending on the stimulus and task, firing rates might remain elevated or show sustained modulation throughout the stimulus presentation period (`d1`, `d2`).
4.  **Omission Response**: This is a critical aspect for omission paradigms. In conditions where a predicted stimulus is *omitted* (e.g., `RXRR` when an 'X' is omitted), we often expect to see a transient change in firing rate around the time the stimulus *would have occurred*. This "omission response" can manifest as an increase or decrease in firing, reflecting a "prediction error" signal or the disinhibition of activity due to the absence of expected input. The latency and magnitude of this response, particularly its divergence from non-omission control conditions (like `RRRR`), are of high scientific interest.
5.  **Adaptation/Recovery**: After the omission or stimulus offset, the firing rates might return to baseline or show prolonged adaptation, indicating the dynamics of neural recovery or continued processing.
6.  **Area-Specific Differences**: Different brain areas are expected to exhibit distinct response profiles. Early visual areas (V1) might show strong, short-latency sensory responses, while higher-order areas (PFC, FEF) might exhibit more sustained activity, slower modulations, or more pronounced omission-related signals reflecting cognitive processing or expectation.

### Anomaly Detection and Interesting Observations:
*   **Lack of Response**: A population that fails to respond to an expected sensory event or omission might indicate a functional deficit, strong adaptation, or an area not involved in that particular processing stage.
*   **Unexpected Latency**: A response that occurs significantly earlier or later than expected could point to unusual processing pathways or altered temporal dynamics.
*   **Excessive Variability**: Broad SEM bands, especially during peak responses, could suggest high trial-to-trial variability, potentially indicative of fluctuating attention, task engagement, or heterogeneity within the neuronal population.
*   **Persistent Activity**: Sustained high or low firing rates beyond the expected stimulus duration could indicate working memory processes or prolonged top-down modulation.
*   **Artifacts**: Sudden, sharp, unphysiological deflections across many units in an area might suggest electrical artifacts. The smoothing helps to mitigate some noise, but gross artifacts would still be visible.

### Cross-Figure Insights:
Observations from Figure 03 would be critically cross-referenced with other figures. For instance:
*   An increase in population firing rate during an omission event in a specific area might coincide with a decrease in low-frequency LFP power (Figure 06) or a specific modulation in gamma band activity (Figure 05).
*   Strong sensory-evoked firing in V1 (Figure 03) would likely correspond to prominent TFR changes in the gamma band for V1 (Figure 05).
These cross-modal comparisons are vital for building a holistic understanding of the neural mechanisms underlying omission processing.

## Adherence to Mandates and Best Practices

Figure 03 strictly adheres to the "GAMMA PLAN" mandates:
*   **Plotly Only**: Uses `plotly.graph_objects` for all plotting.
*   **HTML/SVG Output**: Saved in both interactive HTML and static SVG formats.
*   **White Background**: `plotly_white` template ensures a clean, white background.
*   **Error Representation**: Clearly displays `±2 SEM` as a shaded region.
*   **Time Axis**: X-axis in milliseconds with event lines.
*   **Palette**: Uses `BLACK`, `PINK`, and `GRAY` as mandated.
*   **Naming Convention**: Adheres to `[condition]_population_firing_rate_[session_id]`.
*   **Scientific Rigor**: The plotting of population means and SEM, along with the non-negativity constraint, reflects good scientific plotting practices.

## Potential Improvements/Future Steps

*   **Gaussian Smoothing**: As noted in the critique, replacing the simple moving average with a Gaussian kernel for `smooth_fr` would be a significant biophysical improvement, reducing artificial phase shifts.
*   **Statistical Overlays**: Incorporating statistical significance markers (e.g., asterisks for p < 0.01) directly onto the plots, comparing specific conditions (e.g., omission vs. control), would enhance the scientific value. This would require integrating results from cluster permutation testing.
*   **Multi-Session Aggregation**: Currently, plots are generated per session. Future work involves aggregating data from multiple sessions to produce grand-averaged population firing rate figures, increasing statistical power and generalizability.
*   **Individual Unit Traces**: While this is a population figure, displaying a few representative single-unit firing rate traces as an overlay or in a supplementary figure could provide additional context.

In summary, Figure 03 provides a powerful and interpretable visualization of population-level neural dynamics, carefully constructed to meet both scientific requirements and aesthetic mandates of the "GAMMA PLAN."
