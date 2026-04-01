
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# Paths
INPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\final_reports\behavioral_decoding'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\final_reports\behavioral_decoding'

def plot_decoding_bars():
    # 1. Load Data
    f_res = os.path.join(INPUT_DIR, 'behavioral_content_decoding_results.csv')
    if not os.path.exists(f_res):
        print("Results file not found.")
        return
    
    df = pd.read_csv(f_res)
    
    # 2. Create Bar Plot
    # We want to group by Task and show FeatureSet performance
    fig = px.bar(df, x='Task', y='Accuracy', color='FeatureSet', barmode='group',
                 text_auto='.3f',
                 title="Behavioral Content Decoding Performance (Eye & Pupil)",
                 category_orders={'Task': ['Global_3C', 'Specific_5C']})
    
    # Add Chance Lines
    fig.add_shape(type="line", x0=-0.5, x1=0.5, y0=1/3, y1=1/3, 
                  line=dict(color="gray", width=2, dash="dash"))
    fig.add_annotation(x=0, y=1/3, text="Chance (33%)", showarrow=False, yshift=10)
    
    fig.add_shape(type="line", x0=0.5, x1=1.5, y0=1/5, y1=1/5, 
                  line=dict(color="gray", width=2, dash="dash"))
    fig.add_annotation(x=1, y=1/5, text="Chance (20%)", showarrow=False, yshift=10)
    
    fig.update_layout(yaxis_range=[0, 0.7], template="plotly_white",
                      yaxis_title="Accuracy (5-Fold Balanced CV)")
    
    fig.write_html(os.path.join(OUTPUT_DIR, "FIG_Decoding_Performance_Bars.html"))
    print("Saved Decoding Performance Bar Plot.")

if __name__ == '__main__':
    plot_decoding_bars()
