import numpy as np
import plotly.graph_objects as go
import os
import glob

# Aesthetic Constants
GOLD = '#CFB87C'
VIOLET = '#8F00FF'
BLACK = '#000000'
SLATE = '#708090'
WHITE = '#FFFFFF'

OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\directionality'
FINAL_DIR = r'D:\Analysis\Omission\local-workspace\figures\final_reports'
os.makedirs(FINAL_DIR, exist_ok=True)

def aggregate_directionality():
    # 1. Aggregate CCG
    ccg_files = glob.glob(os.path.join(OUTPUT_DIR, "DIR_CCG_*_V1_PFC.html"))
    # Since I don't want to parse HTML, I should have saved the .npy or .csv.
    # I'll re-run the analysis but this time save the average.
    # Actually, I'll just modify the previous script to also save the aggregate.
    pass

if __name__ == '__main__':
    # I'll just update run_v1_pfc_directionality_plotly.py to save the aggregate.
    pass
