# Summary File 4: Figure Generation - TFR and Band Summary (Figures 05 & 06)

## The Role of `lfp_plotting_utils.py`

A critical aspect of the "GAMMA PLAN" is the generation of publication-quality figures that adhere to strict aesthetic and scientific mandates. To centralize and standardize this process, a new module, `lfp_plotting_utils.py`, was created. This module houses functions specifically designed to generate Plotly figures, ensuring consistency in visual style, color palettes, and data representation across all analyses. The design of this module is driven by the project's aesthetic mandates, which dictate everything from the choice of Plotly as the visualization library to specific color schemes, font types, and the inclusion of error bands (±SEM).

## `create_tfr_figure_per_condition` (Figure 05)

The `create_tfr_figure_per_condition` function is responsible for generating Time-Frequency Representation (TFR) heatmaps. These figures (corresponding to Figure 05 in the GAMMA PLAN) are crucial for visualizing how the power of different frequency bands changes over time relative to experimental events.

### Implementation Details:

*   **Input Data**: The function takes `session_id`, `area`, `condition`, the 2D `tfr_data` (power values across frequencies and time), `freqs` (frequency bins), `times` (time points), and `output_dir` as parameters.
*   **Heatmap Generation**: `plotly.graph_objects.Heatmap` is used to create the core visualization, mapping frequency and time to a colormap (e.g., 'Jet') that represents power in decibels (dB). The `zmin` and `zmax` parameters are typically set to provide a consistent dynamic range across figures.
*   **Omission Patches**: A key feature for omission paradigms is to visually mark the period of omission. The function includes logic to add `fig.add_vrect` (vertical rectangles) for omission periods. These patches are filled with a specific color (e.g., `PINK`) and transparency (`opacity=0.3`) to highlight the relevant experimental window without obscuring the TFR data.
*   **Event Timings**: Vertical lines (`fig.add_vline`) are added to mark crucial event timings (e.g., `fx`, `p1`, `d1`, `d2`) as defined in `TIMING_MS` from `lfp_constants.py`. These lines are styled with dashes and annotations to clearly indicate the onset of different experimental events.
*   **Layout and Styling**: The figure's layout is meticulously configured to adhere to the project's aesthetic mandates:
    *   **Title**: Dynamically generated, including `session_id`, `area`, and `condition`.
    *   **Axis Labels**: Clearly labeled as "Time (ms)" and "Frequency (Hz)".
    *   **Template**: Set to `"plotly_white"` for a clean, white background.
    *   **Font**: "Arial" font, size 12, color black for consistency.
    *   **Backgrounds**: `plot_bgcolor` and `paper_bgcolor` are set to `WHITE`.
*   **Output**: Figures are saved in both `.html` (for interactive viewing) and `.svg` (for publication-quality static images) formats to the specified `output_dir`. The filename follows the strict naming convention: `[condition]_full_tfr_[area]_[session_id]`.

### Integration into `run-lfp-analysis-pipeline.py`:

Within the `run-lfp-analysis-pipeline.py` script, after `lfp_pipeline.compute_tfr_per_condition` computes the mean TFRs for each area and condition, `create_tfr_figure_per_condition` is called. This ensures that a TFR plot is generated and saved for every processed combination of session, area, and condition. The output directory for these figures is `FIG_05_OUTPUT_DIR`.

## `create_band_summary_figure` (Figure 06)

The `create_band_summary_figure` function is designed to visualize the mean power of specific frequency bands over time, typically for multiple areas or conditions, and includes error bars (±SEM). This corresponds to Figure 06 in the GAMMA PLAN, which focuses on summarizing band power dynamics.

### Implementation Details:

*   **Input Data**: The function accepts `data_to_plot` (a nested dictionary containing mean and SEM traces for various bands and areas), `session_id`, `times` (the common time axis), and `output_dir`.
*   **Subplots per Band**: The figure utilizes `plotly.subplots.make_subplots` to create a grid of subplots, with each row representing a different frequency band (e.g., Delta, Theta, Alpha, Beta, Gamma). This allows for a concise comparison of different oscillatory dynamics.
*   **Area Coloring**: To distinguish between different brain areas, a predefined `area_colors` dictionary is used, mapping specific areas (e.g., 'V1', 'V4', 'FEF') to their designated color from `lfp_constants.py` (e.g., `GOLD`, `VIOLET`, `TEAL`). This adheres to the project's palette mandates.
*   **SEM Shading**: For each mean trace, a shaded region representing the standard error of the mean (SEM) is plotted. This is achieved using two `go.Scatter` traces that define the upper and lower bounds of the error region, filled with a semi-transparent color derived from the main trace color (`replace(')', ', 0.2)').replace('rgb', 'rgba')`).
*   **Mean Line Plotting**: The mean band power for each area and band is plotted as a solid line (`go.Scatter` with `mode='lines'`). The legend is configured to show only once per subplot for clarity.
*   **Event Timings**: Similar to the TFR plots, vertical dashed lines are added to mark event timings, maintaining consistency across figures.
*   **Layout and Styling**: The figure layout is configured for clarity and adherence to mandates:
    *   **Title**: Includes `session_id` and a general description.
    *   **Axis Labels**: "Time (ms)" and "Normalized Power".
    *   **Template**: `"plotly_white"`.
    *   **Font**: "Arial", size 12, color black.
    *   **Backgrounds**: `plot_bgcolor` and `paper_bgcolor` are set to `WHITE`.
    *   **Dynamic Height**: The figure height adjusts based on the number of bands being plotted to ensure optimal use of space.
*   **Output**: Figures are saved in `.html` and `.svg` formats, with a filename like `ALL_band_summary_[session_id]`.

### Integration into `run-lfp-analysis-pipeline.py`:

The integration of `create_band_summary_figure` required careful data preparation within `run-lfp-analysis-pipeline.py`. To accurately plot mean and SEM, the pipeline first computes band power for *each individual trial* (`_compute_trial_tfr_and_band_power` helper function). This trial-level data is then used to calculate the mean and SEM time series across trials for each band and area. This mean and SEM data is then passed to `create_band_summary_figure` to generate Figure 06. The output directory for these figures is `FIG_06_OUTPUT_DIR`.

## Conclusion of TFR and Band Summary Figure Generation

The development of `lfp_plotting_utils.py` and the implementation of `create_tfr_figure_per_condition` and `create_band_summary_figure` represent significant progress in the "GAMMA PLAN". These functions ensure that two of the primary visualization requirements for the LFP analysis pipeline are met, providing clear, standardized, and aesthetically consistent representations of Time-Frequency and Band Power data. The modular design allows for easy expansion to other figure types while maintaining adherence to the overall project mandates. The next summary will focus on the final figure implementation (Figure 03) and the overall project conclusion.
