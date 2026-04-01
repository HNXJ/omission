
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# Parameters
DECODING_DIR = r'D:\Analysis\Omission\local-workspace\figures\final_reports\decoding'
CHECKPOINT_DIR = r'D:\Analysis\Omission\local-workspace\checkpoints'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\final_reports\decoding'

AREA_ORDER = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']

def plot_decoding_hubs():
    # 1. Individual Unit Hubs
    unit_df = pd.read_csv(os.path.join(DECODING_DIR, 'individual_unit_decoding.csv'))
    
    # Clean area names
    def clean_area(x):
        for a in AREA_ORDER:
            if a in str(x): return a
        return 'Other'
    unit_df['area_clean'] = unit_df['area'].apply(clean_area)
    
    # Accuracy Boxplot by Area
    fig_unit = px.box(unit_df[unit_df['area_clean'] != 'Other'], 
                      x='area_clean', y='accuracy', color='category',
                      category_orders={'area_clean': AREA_ORDER},
                      title="Individual Neuron Decoding Hubs (3-Class Identity Context)")
    fig_unit.add_hline(y=1/3, line_dash="dash", annotation_text="Chance (0.33)")
    fig_unit.write_html(os.path.join(OUTPUT_DIR, "FIG_09_Unit_Decoding_Hubs.html"))
    
    # 2. Individual LFP Hubs
    lfp_df = pd.read_csv(os.path.join(DECODING_DIR, 'individual_lfp_decoding.csv'))
    
    # Map LFP channels to layers using crossover
    vflip_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'vflip2_mapping_v3.csv'))
    
    def get_layer(row):
        crossover = vflip_df[(vflip_df['session_id'] == int(row['session'])) & 
                             (vflip_df['probe_id'] == int(row['probe']))]['crossover'].values
        if len(crossover) > 0:
            return 'Superficial' if row['channel'] < crossover[0] else 'Deep'
        return 'Unknown'
    
    lfp_df['layer'] = lfp_df.apply(get_layer, axis=1)
    
    # Map area to probe
    def get_area(row):
        area = vflip_df[(vflip_df['session_id'] == int(row['session'])) & 
                        (vflip_df['probe_id'] == int(row['probe']))]['area'].values
        if len(area) > 0: return area[0]
        return 'Unknown'
    
    lfp_df['area'] = lfp_df.apply(get_area, axis=1)
    lfp_df['area_clean'] = lfp_df['area'].apply(clean_area)
    
    # Filter and plot
    lfp_plot = lfp_df[(lfp_df['area_clean'] != 'Other') & (lfp_df['layer'] != 'Unknown')]
    
    fig_lfp = px.box(lfp_plot, x='area_clean', y='accuracy', color='layer',
                     category_orders={'area_clean': AREA_ORDER},
                     title="Individual LFP Channel Decoding Hubs (3-Class Identity Context)")
    fig_lfp.add_hline(y=1/3, line_dash="dash", annotation_text="Chance (0.33)")
    fig_lfp.write_html(os.path.join(OUTPUT_DIR, "FIG_09_LFP_Decoding_Hubs.html"))
    
    print("Saved FIG_09 Unit and LFP decoding hub plots.")

if __name__ == '__main__':
    plot_decoding_hubs()
