
import pandas as pd
df = pd.read_csv('checkpoints/omission_units_layered.csv')
unique_areas = df['area'].unique()
print("Unique values in 'area' column:")
for area in unique_areas:
    print(area)

print("\nRows with 'V3/V4':")
print(df[df['area'] == 'V3/V4'].head())
