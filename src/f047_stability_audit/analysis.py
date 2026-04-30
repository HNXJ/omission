import os
import json
from pathlib import Path
from src.analysis.registry import FigureRegistry
from src.analysis.io.logger import log

def run_stability_audit():
    """
    Executes a series of stability checks for the Omission portal pipeline.
    """
    print(f"""[action] Starting stability audit logic...""")
    results = []
    print(f"""[action] Results list initialized.""")

    # 1. REGISTRY CHECK: Latency Calibration
    print(f"""[action] Verifying AREA_LATENCY calibration in registry...""")
    v1_lat = FigureRegistry.AREA_LATENCY.get("V1")
    print(f"""[action] Retrieved V1 latency: {v1_lat}""")
    pfc_lat = FigureRegistry.AREA_LATENCY.get("PFC")
    print(f"""[action] Retrieved PFC latency: {pfc_lat}""")
    
    if v1_lat == 31 and pfc_lat == 100:
        print(f"""[action] Latency check PASSED.""")
        results.append({"test": "Latency Registry", "status": "PASS", "detail": "V1/PFC offsets verified."})
    else:
        print(f"""[action] Latency check FAILED.""")
        results.append({"test": "Latency Registry", "status": "FAIL", "detail": f"Mismatched latencies: V1={v1_lat}, PFC={pfc_lat}"})

    # 2. DIRECTORY HYGIENE: Output Cleanliness
    print(f"""[action] Verifying output directory hygiene...""")
    output_base = Path("outputs/oglo-8figs")
    print(f"""[action] Target base: {output_base}""")
    
    if output_base.exists():
        print(f"""[action] Output base exists. Scanning for stale patterns...""")
        stale_found = False
        for fid, patterns in FigureRegistry.STALE_PATTERNS.items():
            print(f"""[action] Checking figure {fid} for stale patterns {patterns}""")
            fig_dir = output_base / f"{fid}-sfc"
            if fig_dir.exists():
                print(f"""[action] Scanning {fig_dir}""")
                for f in fig_dir.iterdir():
                    if not FigureRegistry.should_include_file(fid, f.name):
                        print(f"""[action] STALE DETECTED: {f.name}""")
                        stale_found = True
        
        if not stale_found:
            print(f"""[action] Hygiene check PASSED.""")
            results.append({"test": "Directory Hygiene", "status": "PASS", "detail": "No stale artifacts found in tracked figures."})
        else:
            print(f"""[action] Hygiene check FAILED.""")
            results.append({"test": "Directory Hygiene", "status": "FAIL", "detail": "Stale artifacts detected in outputs."})
    else:
        print(f"""[action] Output base MISSING.""")
        results.append({"test": "Directory Hygiene", "status": "WARN", "detail": "Output directory not found. Skipping."})

    # 3. MANIFEST INTEGRITY: Phase Coverage
    print(f"""[action] Verifying manifest integrity...""")
    manifest_path = Path("dashboard/src/data/manifest.json")
    print(f"""[action] Target manifest: {manifest_path}""")
    
    if manifest_path.exists():
        print(f"""[action] Manifest exists. Loading JSON...""")
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        
        print(f"""[action] Filtering figures from manifest...""")
        figs_in_manifest = [fig["id"] for fig in manifest.get("figures", [])]
        print(f"""[action] Total figs in manifest: {len(figs_in_manifest)}""")
        
        phase_5_figs = [fig["id"] for fig in FigureRegistry.get_by_phase(5)]
        print(f"""[action] Phase 5 target figs: {phase_5_figs}""")
        
        missing = [f for f in phase_5_figs if f not in figs_in_manifest]
        if not missing:
            print(f"""[action] Manifest coverage PASSED.""")
            results.append({"test": "Manifest Coverage", "status": "PASS", "detail": "All Phase 5 figures registered."})
        else:
            print(f"""[action] Manifest coverage FAILED: missing {missing}""")
            results.append({"test": "Manifest Coverage", "status": "FAIL", "detail": f"Missing figs: {missing}"})
    else:
        print(f"""[action] Manifest MISSING.""")
        results.append({"test": "Manifest Coverage", "status": "FAIL", "detail": "manifest.json missing."})

    print(f"""[action] Returning audit results.""")
    return results
