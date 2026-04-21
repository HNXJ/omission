import pandas as pd
import numpy as np
from pathlib import Path

# Load metrics
df = pd.read_csv("D:/drive/outputs/oglo-8figs/f041_laminar_analysis/putative_cell_metrics.csv")

# Create 10 bins for duration (0 to 2000us)
bins = np.linspace(0, 2000, 11)
labels = [f"{int(bins[i])}-{int(bins[i+1])}" for i in range(10)]
df['duration_bin'] = pd.cut(df['duration_us'], bins=bins, labels=labels, include_lowest=True)

# Generate table
table = df.groupby(['type', 'duration_bin']).size().unstack(fill_value=0)
print(table)
table.to_csv("D:/drive/outputs/oglo-8figs/f041_laminar_analysis/putative_cell_histogram.csv")
