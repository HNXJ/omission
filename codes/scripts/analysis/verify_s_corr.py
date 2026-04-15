#!/usr/bin/env python3
"""
S+ / S- Population Correlation Analysis
Verifies the expected anti-correlation between S+ and S- firing rate populations.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict
from scipy.ndimage import gaussian_filter1d

# Setup paths
PROJECT_ROOT = Path(r"D:\drive\omission").resolve()
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "oglo-figures" / "3"
ARRAY_DIR = Path('data/arrays')
FS = 1000.0

def main():
    print(f"""[action] Starting S+/S- correlation analysis""")
    
    # Reload trace summaries if they exist, or recompute
    summary_path = OUTPUT_DIR / 'figure3_trace_summary.csv'
    if not summary_path.exists():
        print(f"""[action] Summary CSV not found. Run generate_figure_3.py first.""")
        return
        
    df = pd.read_csv(summary_path)
    print(f"""[action] Loaded {len(df)} rows from trace summary""")
    
    # Filter S+ and S-
    s_plus = df[df['group_name'] == 'S+'].groupby('time_ms')['mean_rate_hz'].mean()
    s_minus = df[df['group_name'] == 'S-'].groupby('time_ms')['mean_rate_hz'].mean()
    
    correlation = np.corrcoef(s_plus, s_minus)[0, 1]
    print(f"""[action] Population correlation between S+ and S-: {correlation:.4f}""")
    
    # Save validation report
    with open(OUTPUT_DIR / "correlation_report.txt", "w") as f:
        f.write(f"Correlation between S+ and S- populations: {correlation:.4f}\n")
    print(f"""[action] Correlation report saved""")

if __name__ == "__main__":
    main()
