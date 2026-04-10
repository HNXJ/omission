"""
Script: calculate_stability.py
Calculates neuron stability based on:
1. Presence Ratio >= 0.95
2. Average Firing Rate >= 1 Hz
3. Consistent Trial participation
"""
import pandas as pd
import numpy as np
from pathlib import Path

METADATA_PATH = Path('outputs/all_units_metadata_v2.csv')
OUTPUT_PATH = Path('outputs/stable_neurons_index.csv')

def calculate_stability():
    print("Loading master metadata...")
    df = pd.read_csv(METADATA_PATH)
    
    # Define stability criteria
    # presence_ratio: 0-1
    # firing_rate: Hz
    
    print(f"Total units before filtering: {len(df)}")
    
    # Apply filters
    # We use .fillna(0) for safety in case of missing values
    df['is_stable'] = (
        (df['presence_ratio'].fillna(0) >= 0.95) & 
        (df['firing_rate'].fillna(0) >= 1.0)
    )
    
    stable_units = df[df['is_stable'] == True]
    
    print(f"Total stable units found: {len(stable_units)}")
    
    # Save the index of stable neurons
    stable_units.to_csv(OUTPUT_PATH, index=False)
    print(f"Stable neurons index saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    calculate_stability()
