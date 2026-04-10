
import pandas as pd
import numpy as np

# Load the metadata
df = pd.read_csv(r'D:\drive\omission\outputs\all_units_metadata.csv', low_memory=False)

# Clean up data
df = df.dropna(subset=['presence_ratio', 'firing_rate', 'isi_violations', 'waveform_duration'])
df['snr'] = pd.to_numeric(df['snr'], errors='coerce')
df['snr'] = df['snr'].replace([np.inf, -np.inf], np.nan)

# 1. Presence Ratio Distribution
presence_bins = [0, 0.1, 0.5, 0.8, 0.9, 0.95, 1.0]
presence_dist = pd.cut(df['presence_ratio'], bins=presence_bins).value_counts().sort_index()

# 2. Firing Rate Distribution
fr_bins = [0, 0.1, 1, 5, 10, 20, 50, 1000]
fr_dist = pd.cut(df['firing_rate'], bins=fr_bins).value_counts().sort_index()

# 3. ISI Violations Distribution
# Assuming these are percentages? Or absolute counts? Let's assume < 1.0 is "good".
isi_bins = [0, 0.01, 0.1, 0.5, 1, 5, 10, 1000000]
isi_dist = pd.cut(df['isi_violations'], bins=isi_bins).value_counts().sort_index()

# 4. Area-wise statistics
area_stats = df.groupby('area_est').agg({
    'presence_ratio': 'mean',
    'firing_rate': 'mean',
    'isi_violations': 'median', # Median due to outliers
    'waveform_duration': 'mean',
    'waveform_halfwidth': 'mean',
    'amplitude': 'mean',
    'snr': 'mean',
    'id': 'count'
}).rename(columns={'id': 'unit_count'})

# 5. Channel Distribution (by electrode/probe)
# peak_channel_id is available.
# Since we have multiple sessions, channel 0-128 is typical for a probe.
channel_dist = df['peak_channel_id'].value_counts().sort_index()

# Format for the report
print("### 🟢 Distribution of Quality Metrics")
print("\n#### Presence Ratio")
print(presence_dist.to_markdown())
print("\n#### Firing Rate (Hz)")
print(fr_dist.to_markdown())
print("\n#### ISI Violations")
print(isi_dist.to_markdown())

print("\n### 🟢 Population Statistics per Area")
print(area_stats.to_markdown())

print("\n### 🟢 Waveform Characteristics Summary")
print(df[['waveform_duration', 'waveform_halfwidth', 'amplitude', 'snr']].describe().to_markdown())

# For channel distribution, maybe just top 10 or a summary.
print("\n### 🟢 Channel-wise Unit Density (Top 10 Channels)")
print(df['peak_channel_id'].value_counts().head(10).to_markdown())
