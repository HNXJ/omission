# Methods extraction from the two uploaded papers

This file consolidates the analysis methods described in:

- **Westerberg et al. (2025)**, *Hierarchical substrates of prediction in visual cortical spiking*.
- **Bastos et al. (2020)**, *Layer and rhythm specificity for predictive routing*.

The goal here is not to recreate the exact experimental data. Instead, the goal is to provide:

1. a faithful inventory of the analyses actually reported,
2. the likely tensor shapes used by those analyses,
3. pseudocode and executable-style example code that runs on **zero matrices with approximately matching dimensional structure**.

The example code is intentionally minimal and synthetic. It preserves the **indexing logic, contrasts, aggregation axes, and statistical workflow shape** without pretending to reproduce the papers' real values.

---

# 1. Study-by-study task and data structure

## 1.1 Westerberg et al. (2025): global-local oddball, laminar multi-area spiking

### Core experimental structure

The paper uses a **4-item visual sequence** with oriented gratings. Animals are habituated to a predicted sequence such as `x-x-x-y`. In the main block, `x-x-x-y` occurs on 80% of trials and `x-x-x-x` occurs on 20% of trials. Control blocks alternate predictable sequences to isolate local and global effects. The critical oddball comparison is made at the **4th item (P4)** and normalized relative to **P3**, yielding the main contrast `P4-P3` in main block versus control block. The paper explicitly states this double-contrast design and uses it to separate prediction-related effects from short-term adaptation.

### Real data modalities

- Mouse: single-unit spiking from Neuropixels, plus LFP/CSD, plus optotagging.
- Monkey: multiunit envelope-like signal (MUAe), laminar probes, plus optotagging in some areas.
- Multi-area recordings across visual cortex, plus prefrontal cortex in monkeys.
- Layer grouping into superficial/extragranular vs granular/deep depending on analysis.

### Practical tensor shapes for mock analysis

These are not claimed to be the paper's on-disk storage format. They are analysis-friendly shapes that match the operations described.

#### A. Trial-resolved sequence responses

```text
mouse_spikes_main:    [mouse, area, unit, trial, position, time]
mouse_spikes_control: [mouse, area, unit, trial, position, time]

monkey_muae_main:     [session, area, channel, trial, position, time]
monkey_muae_control:  [session, area, channel, trial, position, time]
```

Recommended zero-matrix mock shapes:

```text
mouse_spikes_main    = zeros([14, 6, 64, 120, 4, 500])
mouse_spikes_control = zeros([14, 6, 64, 120, 4, 500])

monkey_muae_main     = zeros([19, 8, 32, 120, 4, 500])
monkey_muae_control  = zeros([19, 8, 32, 120, 4, 500])
```

Interpretation of axes:

- `mouse=14` because final mouse sample was 14 animals.
- `area=6` mouse visual areas: V1, LM, RL, AL, PM, AM.
- `area=8` monkey areas: V1, V2, V3, V4, MT, MST, 8A, PFC.
- `position=4` because each sequence has P1..P4.
- `time=500` here means 500 ms at 1 ms resolution during a stimulus epoch. This is a convenient mock dimension, not a claim about the exact internal sampling used for every figure.

#### B. Layer-resolved activity

```text
layered_activity: [subject, area, layer_group, unit_or_channel, trial, time]
```

Suggested mock shape:

```text
layered_activity = zeros([19, 8, 3, 16, 120, 500])
```

Where `layer_group` might be one of:

- `0 = superficial/L2/3`
- `1 = granular/L4`
- `2 = deep/L5/6`

#### C. Granger-causality input time series in mice

The paper states that for mice they pooled simultaneously recorded neurons into one time series per area and computed nonparametric Granger causality per mouse, condition, and time window.

```text
gc_input: [mouse, condition, trial, area, time]
```

Suggested mock shape:

```text
gc_input = zeros([14, 2, 120, 6, 200])
```

- `condition=2` can be `local_oddball` and `global_oddball`.
- `time=200` can represent a 200 ms analysis window, matching the paper's 200 ms Fourier window for GC.

#### D. Frequency-domain GC output

```text
gc_spectrum: [mouse, condition, source_area, target_area, freq]
```

Suggested mock shape:

```text
gc_spectrum = zeros([14, 2, 6, 6, 101])
```

with `freq = 0..100 Hz`.

---

## 1.2 Bastos et al. (2020): predictable vs unpredictable blocks, laminar spiking/LFP/GC

### Core experimental structure

This paper uses a delayed-match-to-sample task with **blockwise predictability**. In predictable blocks, the same sample repeats for 50 trials. In unpredictable blocks, one of three sample objects is selected randomly on each trial. Analyses focus on the **presample interval** and the **sample interval** and compare predictable versus unpredictable blocks.

### Real data modalities

- Laminar multi-contact recordings in V4, 7A, PFC.
- Non-laminar recordings in LIP and FEF.
- Multiunit activity, thresholded spikes, LFP power, coherence, Granger causality.
- Single-neuron information analyses.
- GLM linking higher-order rhythmic power to V4 spiking/gamma.

### Practical tensor shapes for mock analysis

#### A. Session-wise MUA/LFP tensors

```text
mua: [session, area, channel, condition, trial, time]
lfp: [session, area, channel, condition, trial, time]
```

Suggested mock shapes:

```text
mua = zeros([71, 5, 32, 2, 50, 1000])
lfp = zeros([71, 5, 32, 2, 50, 1000])
```

Axis meaning:

- `session=71`
- `area=5` for V4, LIP, 7A, FEF, PFC
- `condition=2` for predictable/unpredictable
- `trial=50` because each block has 50 trials
- `time=1000` for a 1 s interval sampled at 1 ms in the mock tensor

#### B. Layer-resolved tensors for gyri areas only

```text
laminar_mua: [session, area_laminar, layer, channel, condition, trial, time]
laminar_lfp: [session, area_laminar, layer, channel, condition, trial, time]
```

Suggested mock shapes:

```text
laminar_mua = zeros([71, 3, 2, 16, 2, 50, 1000])
laminar_lfp = zeros([71, 3, 2, 16, 2, 50, 1000])
```

- `area_laminar=3` for V4, 7A, PFC
- `layer=2` for superficial vs deep

#### C. Frequency-domain power

```text
power: [session, area, channel, condition, freq]
```

Suggested mock shape:

```text
power = zeros([71, 5, 32, 2, 101])
```

#### D. Interareal coherence / Granger causality

```text
coh: [session, source_area, target_area, condition, freq]
gc:  [session, source_area, target_area, condition, freq]
```

Suggested mock shapes:

```text
coh = zeros([71, 5, 5, 2, 101])
gc  = zeros([71, 5, 5, 2, 101])
```

#### E. Single-neuron information / selectivity

```text
spike_counts: [session, area, neuron, condition, trial, timebin]
```

Suggested mock shape:

```text
spike_counts = zeros([71, 5, 32, 2, 50, 50])
```

where `timebin=50` might correspond to 20 ms bins across a 1 s epoch.

---

# 2. Method inventory with pseudocode and zero-matrix code

---

## 2.1 Westerberg et al. (2025)

### Method W1. Habituation-based local/global oddball design

#### What the paper did

- Habituated animals to `x-x-x-y` or `y-y-y-x`.
- Main block: 80% habituated local oddball sequence, 20% global oddball sequence.
- Control block: predictable alternation for matched comparison.
- Compared neural responses at P4 relative to P3, then compared main versus control.

#### Logical tensor

```text
activity[subject, area, unit, trial, position, time]
```

#### Pseudocode

```python
for subject in subjects:
    for area in areas:
        for unit in units:
            p4_main = mean(main[subject, area, unit, :, P4, :], axis=0)
            p3_main = mean(main[subject, area, unit, :, P3, :], axis=0)
            p4_ctrl = mean(ctrl[subject, area, unit, :, P4, :], axis=0)
            p3_ctrl = mean(ctrl[subject, area, unit, :, P3, :], axis=0)

            oddball_effect = (p4_main - p3_main) - (p4_ctrl - p3_ctrl)
```

#### Zero-matrix code

```python
import numpy as np

mouse_main = np.zeros((14, 6, 64, 120, 4, 500))
mouse_ctrl = np.zeros((14, 6, 64, 120, 4, 500))

P3, P4 = 2, 3

p4_main = mouse_main[:, :, :, :, P4, :].mean(axis=3)
p3_main = mouse_main[:, :, :, :, P3, :].mean(axis=3)
p4_ctrl = mouse_ctrl[:, :, :, :, P4, :].mean(axis=3)
p3_ctrl = mouse_ctrl[:, :, :, :, P3, :].mean(axis=3)

oddball_effect = (p4_main - p3_main) - (p4_ctrl - p3_ctrl)
# shape: [mouse, area, unit, time]
```

---

### Method W2. Local oddball population effect

#### What the paper did

Computed population-average local oddball responses and tested significance with a **nonparametric cluster-based permutation test** over time.

#### Logical tensor

```text
lo_effect[subject, area, unit, time]
```

#### Pseudocode

```python
for area in areas:
    population_trace = mean(lo_effect[:, area, :, :], axis=(0, 1))
    significant_clusters = cluster_permutation_test(lo_effect[:, area, :, :])
```

#### Zero-matrix code

```python
lo_effect = np.zeros((14, 6, 64, 500))
pop_lo = lo_effect.mean(axis=(0, 2))  # [area, time]
```

---

### Method W3. Global oddball population effect

#### What the paper did

Same structure as local oddball, but for the global oddball contrast. The paper emphasizes sparse higher-order responses and lack of hierarchical feedforward progression.

#### Zero-matrix code

```python
go_effect = np.zeros((14, 6, 64, 500))
pop_go = go_effect.mean(axis=(0, 2))  # [area, time]
```

---

### Method W4. Percentage of oddball-encoding units/channels

#### What the paper did

For each area, quantified what proportion of units/channels significantly encoded local or global oddballs.

#### Logical tensor

```text
sig_mask[subject, area, unit]
```

#### Pseudocode

```python
for area in areas:
    percent_sig = 100 * mean(sig_mask[:, area, :])
```

#### Zero-matrix code

```python
sig_mask_lo = np.zeros((14, 6, 64), dtype=bool)
sig_mask_go = np.zeros((14, 6, 64), dtype=bool)

percent_lo = 100 * sig_mask_lo.mean(axis=(0, 2))
percent_go = 100 * sig_mask_go.mean(axis=(0, 2))
```

---

### Method W5. Onset-latency analysis across hierarchy

#### What the paper did

Estimated onset time of significance for local and global oddball effects and related latency to hierarchical position.

#### Logical tensor

```text
latency[subject_or_session, area, unit]
```

#### Pseudocode

```python
for unit in units:
    ttest_each_timepoint()
    onset = first_contiguous_cluster_longer_than_threshold()
```

#### Zero-matrix code

```python
latency_lo = np.full((14, 6, 64), np.nan)
latency_go = np.full((14, 6, 64), np.nan)

# downstream hierarchical regression would use nanmean across units
mean_latency_lo = np.nanmean(latency_lo, axis=(0, 2))
mean_latency_go = np.nanmean(latency_go, axis=(0, 2))
```

---

### Method W6. Layer-specific analysis: L2/3, L4, L5/6 or extragranular vs granular

#### What the paper did

- Compared local oddball and global oddball effects by laminar compartment.
- Tested whether prediction-error-like signals preferentially appeared in superficial layers.
- For global oddballs, grouped granular vs extragranular compartments to distinguish feedforward- vs feedback-associated laminae.

#### Logical tensor

```text
layer_effect[subject, area, layer_group, unit, time]
```

#### Zero-matrix code

```python
layer_effect = np.zeros((19, 8, 3, 16, 500))
# 3 layer groups: superficial, granular, deep
layer_pop = layer_effect.mean(axis=(0, 3))   # [area, layer_group, time]
```

---

### Method W7. Deviance-scaling test for local oddballs

#### What the paper did

Compared local oddball responses across contexts with different local oddball probabilities, asking whether response magnitude scaled with deviance.

#### Logical tensor

```text
lo_by_probability[subject, area, unit, prob_level, time]
```

Suggested mock shape:

```text
[14, 6, 64, 3, 500]
```

with `prob_level = [100%, 80%, 12.5%]`.

#### Zero-matrix code

```python
lo_by_probability = np.zeros((14, 6, 64, 3, 500))
mean_by_prob = lo_by_probability.mean(axis=(0, 2, 4))  # [area, prob_level]
```

---

### Method W8. Current source density (CSD)

#### What the paper did

Estimated CSD from LFP by taking a second spatial derivative across channels, after median filtering and downsampling to one laminar column. Then computed condition contrasts and assessed significance via spatiotemporal cluster testing.

#### Formula given in the paper

```text
CSD(t,c) = -sigma * (V(t,c-2) - 2V(t,c) + V(t,c+2)) / (2*s^2)
```

#### Logical tensor

```text
lfp[subject, area, channel, condition, time]
csd[subject, area, channel, condition, time]
```

#### Zero-matrix code

```python
lfp = np.zeros((14, 6, 32, 2, 500))
sigma = 0.4
s = 1.0

csd = np.zeros_like(lfp)
csd[:, :, 2:-2, :, :] = -sigma * (
    lfp[:, :, 0:-4, :, :] - 2 * lfp[:, :, 2:-2, :, :] + lfp[:, :, 4:, :, :]
) / (2 * s**2)
```

---

### Method W9. Mouse single-unit inclusion criteria

#### What the paper did

Restricted analysis to units with:

- visually evoked response > 5 SD above baseline,
- minimum firing rate of 0.1 spikes/s,
- ISI violations < 0.33,
- presence ratio > 0.95,
- amplitude cutoff < 0.1,
- location in targeted areas.

#### Logical tensor

```text
unit_metrics[mouse, area, unit, metric]
valid_mask[mouse, area, unit]
```

#### Zero-matrix code

```python
vis_sd = np.zeros((14, 6, 64))
fr = np.zeros((14, 6, 64))
isi = np.zeros((14, 6, 64))
presence = np.zeros((14, 6, 64))
amp_cutoff = np.zeros((14, 6, 64))

valid_mask = (
    (vis_sd > 5) &
    (fr >= 0.1) &
    (isi < 0.33) &
    (presence > 0.95) &
    (amp_cutoff < 0.1)
)
```

---

### Method W10. Monkey MUAe extraction

#### What the paper did

For monkey broadband data, filtered 500 to 5000 Hz, rectified, low-pass filtered below 250 Hz, and downsampled to 1000 Hz to obtain MUAe.

#### Logical tensor

```text
broadband[session, area, channel, time]
muae[session, area, channel, time]
```

#### Pseudocode

```python
filtered = bandpass(raw, 500, 5000)
rectified = abs(filtered)
muae = lowpass(rectified, 250)
muae = downsample(muae, target_fs=1000)
```

#### Zero-matrix code

```python
raw = np.zeros((19, 8, 32, 30000))
filtered = raw.copy()
rectified = np.abs(filtered)
muae = rectified[..., ::30]  # crude placeholder for downsampling from 30 kHz to 1 kHz
```

---

### Method W11. Optotagging of inhibitory interneurons

#### What the paper did

- Mice: tagged SST and PV cells by response to optical stimulation.
- Monkeys: tagged inhibitory interneurons using viral targeting plus firing-rate and coherence criteria during laser stimulation.

#### Logical tensor

```text
laser_trials[subject, area, unit, stim_type, time]
optotag_mask[subject, area, unit]
```

#### Zero-matrix code

```python
laser_trials = np.zeros((14, 6, 64, 3, 1000))
optotag_mask = np.zeros((14, 6, 64), dtype=bool)
```

---

### Method W12. Pupil and behavior-aligned auxiliary analyses

#### What the paper did

Measured pupil and wheel/behavioral variables, primarily to support task interpretation and quality control.

#### Logical tensor

```text
pupil[subject, trial, time]
running[subject, trial, time]
```

#### Zero-matrix code

```python
pupil = np.zeros((14, 120, 500))
running = np.zeros((14, 120, 500))
```

---

### Method W13. Nonparametric cluster-based permutation testing

#### What the paper did

Used cluster-based permutation statistics on time series, and for CSD also on spatiotemporal data, controlling family-wise error rate.

#### Generic pseudocode

```python
def cluster_perm(data_a, data_b, threshold, n_perm=1000):
    observed_t = pointwise_test(data_a, data_b)
    observed_clusters = clusterize(observed_t, threshold)
    null_max = []
    for _ in range(n_perm):
        shuffled = permute_labels(data_a, data_b)
        t_perm = pointwise_test(*shuffled)
        clusters_perm = clusterize(t_perm, threshold)
        null_max.append(max_cluster_mass(clusters_perm))
    return clusters_surviving(observed_clusters, null_max)
```

#### Zero-matrix code skeleton

```python
def cluster_perm_placeholder(a, b):
    return {
        "t": np.zeros(a.shape[-1]),
        "significant_mask": np.zeros(a.shape[-1], dtype=bool)
    }
```

---

### Method W14. Feature selectivity index

#### What the paper did

Computed orientation selectivity by subtracting GO-orientation response from LO-orientation response and dividing by their sum, using 0 to 500 ms visual responses.

#### Formula

```text
selectivity = (LO - GO) / (LO + GO)
```

#### Zero-matrix code

```python
lo_resp = np.zeros((14, 6, 64))
go_resp = np.zeros((14, 6, 64))
selectivity = (lo_resp - go_resp) / np.where((lo_resp + go_resp) == 0, 1, (lo_resp + go_resp))
```

---

### Method W15. Nonparametric Fourier-domain Granger causality from spike time series

#### What the paper did

- One time series per area.
- Sliding windows of 200 ms.
- Multitaper Fourier coefficients.
- Nonparametric bivariate Granger causality.
- Baseline and two post-oddball windows: 100 to 300 ms, and 300 to 500 ms.

#### Logical tensor

```text
area_ts[mouse, condition, trial, area, time]
GC[mouse, condition, window, source_area, target_area, freq]
```

Suggested mock shape:

```text
area_ts = zeros([14, 2, 120, 6, 200])
GC      = zeros([14, 2, 3, 6, 6, 101])
```

#### Zero-matrix code

```python
area_ts = np.zeros((14, 2, 120, 6, 200))
gc = np.zeros((14, 2, 3, 6, 6, 101))  # baseline, early, late windows

# Example asymmetry: lower->higher minus higher->lower
hierarchy = [0, 1, 2, 3, 4, 5]
gc_asym = np.zeros((14, 2, 3, 101))
for src in range(6):
    for dst in range(6):
        if src < dst:
            gc_asym += gc[:, :, :, src, dst, :] - gc[:, :, :, dst, src, :]
```

---

## 2.2 Bastos et al. (2020)

### Method B1. Blocked predictability design in delayed match-to-sample

#### What the paper did

- Predictable block: one repeated sample for 50 trials.
- Unpredictable block: one of three objects chosen randomly on each trial for 50 trials.
- Compared neural activity in presample and sample intervals.

#### Logical tensor

```text
activity[session, area, channel, condition, trial, time]
```

#### Zero-matrix code

```python
activity = np.zeros((71, 5, 32, 2, 50, 1000))
PRED, UNPRED = 0, 1
pred_block = activity[:, :, :, PRED]
unpred_block = activity[:, :, :, UNPRED]
```

---

### Method B2. Multiunit activity difference: unpredictable minus predictable

#### What the paper did

Computed MUA differences across areas and tested significance over time with cluster-based randomization.

#### Logical tensor

```text
mua[session, area, channel, condition, time]
```

#### Zero-matrix code

```python
mua = np.zeros((71, 5, 32, 2, 1000))
mua_diff = mua[:, :, :, 1, :] - mua[:, :, :, 0, :]
pop_mua_diff = mua_diff.mean(axis=(0, 2))
```

---

### Method B3. Percent explained variance / omega-squared information analysis

#### What the paper did

Quantified how much spike-rate variance explained sample identity, separately for predictable and unpredictable blocks.

#### Logical tensor

```text
spike_counts[session, area, neuron, condition, trial, timebin]
sample_id[session, condition, trial]
pev[session, area, neuron, condition, timebin]
```

#### Pseudocode

```python
for neuron in neurons:
    for timebin in timebins:
        pev = omega_squared(spike_counts[..., timebin], sample_id)
```

#### Zero-matrix code

```python
spike_counts = np.zeros((71, 5, 32, 2, 50, 50))
sample_id = np.zeros((71, 2, 50), dtype=int)
pev = np.zeros((71, 5, 32, 2, 50))
```

---

### Method B4. Frequency-resolved LFP power analysis

#### What the paper did

Estimated power from 0 to 250 Hz using multitaper spectral estimation on 1 s windows, then compared predictable vs unpredictable power spectra.

#### Logical tensor

```text
lfp[session, area, channel, condition, trial, time]
power[session, area, channel, condition, freq]
```

#### Zero-matrix code

```python
lfp = np.zeros((71, 5, 32, 2, 50, 1000))
power = np.zeros((71, 5, 32, 2, 101))
power_change = power[:, :, :, 1, :] - power[:, :, :, 0, :]
```

---

### Method B5. Band-specific summaries: theta, alpha, beta, gamma

#### What the paper did

Summarized modulation in canonical bands:

- theta 2 to 6 Hz
- alpha 8 to 14 Hz
- beta 15 to 30 Hz
- gamma 40 to 90 Hz

#### Zero-matrix code

```python
freqs = np.arange(101)
bands = {
    "theta": (freqs >= 2) & (freqs <= 6),
    "alpha": (freqs >= 8) & (freqs <= 14),
    "beta":  (freqs >= 15) & (freqs <= 30),
    "gamma": (freqs >= 40) & (freqs <= 90),
}

band_summary = {
    name: power_change[..., mask].mean(axis=-1)
    for name, mask in bands.items()
}
```

---

### Method B6. Laminar contrasts for power and MUA

#### What the paper did

Compared superficial vs deep layers in V4, 7A, PFC for predictability-related modulation of MUA and power.

#### Logical tensor

```text
laminar_power[session, area_laminar, layer, condition, freq]
laminar_mua[session, area_laminar, layer, condition, time]
```

#### Zero-matrix code

```python
laminar_power = np.zeros((71, 3, 2, 2, 101))
laminar_mua = np.zeros((71, 3, 2, 2, 1000))

lam_power_diff = laminar_power[:, :, :, 1, :] - laminar_power[:, :, :, 0, :]
lam_mua_diff = laminar_mua[:, :, :, 1, :] - laminar_mua[:, :, :, 0, :]
```

---

### Method B7. Trial-by-trial evolution after block switches

#### What the paper did

Tracked how power changed across repeated predictable trials after switching from an unpredictable block, identifying when gamma reached a minimum and alpha/beta reached plateaus.

#### Logical tensor

```text
trial_power[session, area, condition, block_trial, freq]
```

Suggested mock shape:

```text
[71, 5, 2, 50, 101]
```

#### Zero-matrix code

```python
trial_power = np.zeros((71, 5, 2, 50, 101))
predictable_trial_power = trial_power[:, :, 0]
unpredictable_trial_power = trial_power[:, :, 1]

relative_to_unpred = predictable_trial_power - unpredictable_trial_power.mean(axis=2, keepdims=True)
```

---

### Method B8. Stimulus selectivity of predictability effects

#### What the paper did

Defined each V4 site's preferred vs nonpreferred sample object based on MUA, then compared predictability-related modulation separately for preferred and nonpreferred stimuli.

#### Logical tensor

```text
object_mua[session, channel, object, condition, time]
preferred_index[session, channel]
```

Suggested mock shape:

```text
object_mua = zeros([71, 32, 3, 2, 1000])
```

#### Zero-matrix code

```python
object_mua = np.zeros((71, 32, 3, 2, 1000))
mean_response = object_mua.mean(axis=(3, 4))
preferred_index = mean_response.argmax(axis=-1)
nonpreferred_index = mean_response.argmin(axis=-1)
```

---

### Method B9. Bipolar derivation of LFP prior to coherence / GC

#### What the paper did

Computed bipolar derivations by subtracting contacts separated by 400 um to reduce common reference and improve localization.

#### Logical tensor

```text
raw_lfp[session, area, contact, time]
bipolar_lfp[session, area, bipolar_pair, time]
```

#### Zero-matrix code

```python
raw_lfp = np.zeros((71, 5, 32, 1000))
bipolar_lfp = raw_lfp[:, :, 2:, :] - raw_lfp[:, :, :-2, :]
```

---

### Method B10. Coherence analysis between areas

#### What the paper did

Computed interareal coherence spectra and compared predictable vs unpredictable conditions.

#### Logical tensor

```text
coh[session, source_area, target_area, condition, freq]
```

#### Zero-matrix code

```python
coh = np.zeros((71, 5, 5, 2, 101))
coh_diff = coh[:, :, :, 1, :] - coh[:, :, :, 0, :]
```

---

### Method B11. Nonparametric Granger causality and feedforward vs feedback decomposition

#### What the paper did

- Computed nonparametric spectral GC from Fourier-domain estimates.
- Separated directed pairs into feedforward vs feedback using assumed cortical hierarchy: V4 < LIP < 7A < FEF < PFC.
- Compared frequency-resolved modulation under predictability.

#### Logical tensor

```text
gc[session, source_area, target_area, condition, freq]
```

#### Zero-matrix code

```python
gc = np.zeros((71, 5, 5, 2, 101))
hierarchy = {"V4": 0, "LIP": 1, "7A": 2, "FEF": 3, "PFC": 4}

ff_mask = np.zeros((5, 5), dtype=bool)
fb_mask = np.zeros((5, 5), dtype=bool)
for i in range(5):
    for j in range(5):
        if i < j:
            ff_mask[i, j] = True
        elif i > j:
            fb_mask[i, j] = True

gc_diff = gc[:, :, :, 1, :] - gc[:, :, :, 0, :]
ff_gc = gc_diff[:, ff_mask, :]
fb_gc = gc_diff[:, fb_mask, :]
```

---

### Method B12. Layer-specific GC from V4 and PFC

#### What the paper did

Focused on:

- V4-to-rest as feedforward.
- PFC-to-rest as feedback.
- Compared superficial vs deep contributions.

#### Logical tensor

```text
layered_gc[session, seed_area, layer, target_area, condition, freq]
```

Suggested mock shape:

```text
layered_gc = zeros([71, 2, 2, 4, 2, 101])
```

where `seed_area=0` means `V4`, `seed_area=1` means `PFC`.

#### Zero-matrix code

```python
layered_gc = np.zeros((71, 2, 2, 4, 2, 101))
layered_gc_diff = layered_gc[..., 1, :] - layered_gc[..., 0, :]
```

---

### Method B13. GLM linking higher-order cortex rhythms to V4 spiking/gamma

#### What the paper did

Used a general linear model to test whether trial-by-trial fluctuations in higher-order cortex power explained variance in V4 gamma power and MUA. Negative coefficients were interpreted as inhibitory coupling.

#### Logical tensor

```text
X_regressors[session, trial, regressor]
y_v4_gamma[session, trial]
y_v4_mua[session, trial]
beta_coeff[session, regressor]
```

Suggested mock shape:

```text
X_regressors = zeros([71, 50, 12])
y_v4_gamma   = zeros([71, 50])
y_v4_mua     = zeros([71, 50])
```

#### Zero-matrix code

```python
X_regressors = np.zeros((71, 50, 12))
y_v4_gamma = np.zeros((71, 50))
y_v4_mua = np.zeros((71, 50))
beta_gamma = np.zeros((71, 12))
beta_mua = np.zeros((71, 12))
```

If you want actual numerical fitting on synthetic nonzero data, one would do:

```python
# beta = (X^T X)^-1 X^T y
```

but for zero matrices the solution trivially stays zero.

---

### Method B14. Cluster-based randomization test for MUA, power, coherence, GC

#### What the paper did

Used nonparametric cluster-based randomization tests for time series and frequency spectra when comparing predictable vs unpredictable conditions.

#### Zero-matrix code skeleton

```python
def spectral_cluster_test_placeholder(a, b):
    return {
        "stat": np.zeros(a.shape[-1]),
        "sig": np.zeros(a.shape[-1], dtype=bool)
    }
```

---

# 3. Minimal end-to-end example pipelines on zeros

## 3.1 Westerberg-style pipeline

```python
import numpy as np

# subject x area x unit x trial x position x time
main = np.zeros((14, 6, 64, 120, 4, 500))
ctrl = np.zeros((14, 6, 64, 120, 4, 500))
P3, P4 = 2, 3

# P4-P3 main vs control
main_delta = main[:, :, :, :, P4, :] - main[:, :, :, :, P3, :]
ctrl_delta = ctrl[:, :, :, :, P4, :] - ctrl[:, :, :, :, P3, :]
effect = main_delta.mean(axis=3) - ctrl_delta.mean(axis=3)
# effect shape: [14, 6, 64, 500]

# population trace per area
population = effect.mean(axis=(0, 2))

# significant units placeholder
sig_units = np.zeros((14, 6, 64), dtype=bool)
percent_sig = 100 * sig_units.mean(axis=(0, 2))

# onset latency placeholder
onset_latency = np.full((14, 6, 64), np.nan)
```

## 3.2 Bastos-style pipeline

```python
import numpy as np

# session x area x channel x condition x trial x time
mua = np.zeros((71, 5, 32, 2, 50, 1000))
lfp = np.zeros((71, 5, 32, 2, 50, 1000))

PRED, UNPRED = 0, 1

# MUA difference
mua_pred = mua[:, :, :, PRED].mean(axis=3)
mua_unpred = mua[:, :, :, UNPRED].mean(axis=3)
mua_diff = mua_unpred - mua_pred

# power placeholder: session x area x channel x condition x freq
power = np.zeros((71, 5, 32, 2, 101))
power_diff = power[:, :, :, UNPRED, :] - power[:, :, :, PRED, :]

# GC placeholder: session x source x target x condition x freq
gc = np.zeros((71, 5, 5, 2, 101))
gc_diff = gc[:, :, :, UNPRED, :] - gc[:, :, :, PRED, :]

# preferred object indexing placeholder
object_mua = np.zeros((71, 32, 3, 2, 1000))
mean_obj = object_mua.mean(axis=(3, 4))
preferred_obj = mean_obj.argmax(axis=-1)
```

---

# 4. Critical notes and limitations

## 4.1 What these mock tensors do well

They preserve:

- the **contrast logic**,
- the **axis structure**,
- the **laminar grouping logic**,
- the **feedforward/feedback decomposition**,
- the **time/frequency organization**,
- and the **unit/channel/session nesting**.

## 4.2 What they do not preserve

They do not preserve:

- exact acquisition sampling rates after every preprocessing stage,
- exact per-session channel counts,
- exact per-area unit counts,
- exact trial counts after exclusions,
- exact taper settings or FieldTrip object formats,
- exact statistics implementation details from supplementary material,
- or biological variance.

## 4.3 Best improvement if you want the next version

The most valuable next improvement would be to convert this from descriptive pseudocode into **fully runnable NumPy code modules** with:

- exact function signatures,
- named dimensions,
- mock metadata tables for area/layer/hierarchy,
- and placeholder cluster/GC APIs that match the papers' real analysis order.

That would make the document directly usable as a scaffold for your omission repo.

---

# 5. Source anchoring

This methods inventory was extracted from the two uploaded papers and especially from their task, results, discussion, and methods sections:

- Westerberg et al. oddball design, main/control contrasts, hierarchy, layers, CSD, optotagging, data inclusion, and GC methods.
- Bastos et al. blocked predictability design, laminar MUA/LFP, power/coherence/GC, selectivity, and GLM methods.

