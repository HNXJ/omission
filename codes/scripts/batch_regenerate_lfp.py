import os
from pathlib import Path
from codes.scripts.analysis.generate_figure_6 import generate_figure_6 as gen_fig6

NWB_DIR = Path(r'D:\analysis\nwb')

def run_batch():
    # Only process files that exist
    nwb_files = list(NWB_DIR.glob('*.nwb'))
    print(f"Found {len(nwb_files)} sessions. Starting batch process...")
    
    for f in nwb_files:
        print(f"--- Processing session: {f.name} ---")
        try:
            gen_fig6(session_file=f)
        except Exception as e:
            print(f"Failed session {f.name}: {e}")

if __name__ == "__main__":
    run_batch()
