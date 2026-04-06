import os
import re
from pathlib import Path

mapping = {
    'lfp_constants': 'lfp',
    'lfp_preproc': 'lfp',
    'lfp_tfr': 'lfp',
    'lfp_stats': 'lfp',
    'lfp_connectivity': 'lfp',
    'lfp_laminar_mapping': 'lfp',
    'lfp_pipeline': 'lfp',
    'lfp_io': 'io',
    'extract_metadata': 'io',
    'master_npy_export': 'io',
    'lfp_events': 'events',
    'photodiode_alignment': 'events',
    'verify_timing': 'events',
    'verify_timing_multi': 'events',
    'behavioral_utils': 'behavior',
    'neuro_variability_suite': 'spiking',
    'spike_lfp_coordination': 'spiking',
    'omission_hierarchy_utils': 'spiking',
    'compute_mean_matched_fano': 'spiking',
    'lfp_plotting': 'visualization',
    'lfp_plotting_utils': 'visualization',
    'poster_figures': 'visualization',
    'timing_validation_plot': 'visualization',
    'lfp_plotting_sup_fig2': 'visualization',
    'enrich_summary': 'utilities',
    'extract_omission_factors': 'utilities',
    'update_data_summary': 'utilities',
    'update_summary': 'utilities'
}

def replace_imports(content):
    def repl(match):
        prefix = match.group(1) # e.g. "from "
        base = match.group(2)   # e.g. "src.functions" or "codes.functions"
        sep = match.group(3)    # " import " or "."
        module = match.group(4)
        
        # Strip trailing dot if any, though regex handles it
        if module in mapping:
            subpkg = mapping[module]
            if sep.strip() == "import":
                return f"{prefix}codes.functions.{subpkg}.{module}{sep}"
            else:
                return f"{prefix}codes.functions.{subpkg}.{module}"
        return match.group(0)

    # regex to catch:
    # from codes.functions.io.lfp_io import ... -> from codes.functions.io.lfp_io import ...
    # from codes.functions.io.lfp_io import ...
    # import codes.functions.io.lfp_io
    # import codes.functions.io.lfp_io
    
    pattern1 = r'(from\s+)(codes\.functions|src\.functions)\.([a-zA-Z0-9_]+)(\s+import)'
    def repl1(m):
        mod = m.group(3)
        if mod in mapping:
            return f"from codes.functions.{mapping[mod]}.{mod} import"
        return m.group(0)
    
    content = re.sub(pattern1, repl1, content)
    
    pattern2 = r'(import\s+)(codes\.functions|src\.functions)\.([a-zA-Z0-9_]+)'
    def repl2(m):
        mod = m.group(3)
        if mod in mapping:
            return f"import codes.functions.{mapping[mod]}.{mod}"
        return m.group(0)

    content = re.sub(pattern2, repl2, content)
    
    return content

root = Path("D:/drive/omission/codes")
for p in root.rglob("*.py"):
    if "site-packages" in str(p) or "__pycache__" in str(p):
        continue
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = replace_imports(content)
    if new_content != content:
        with open(p, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {p}")
