# PENDING [antigravity] [Task]: Visual QA Audit & Aesthetic Remediation (f001-f020)

**CONTEXT:**
The Sentinel Audit of the Omission pipeline has flagged 19 out of 20 modules in the core hierarchy (Phase 1-3) for aesthetic and structural violations. Most modules are stuck at a "Pass" (80/100) or "Fail" (50/100) status.

**INPUT DATA:**
  ┌────────────────────────┬─────────┬─────────┬────────────────────────────────────────┐
  │ Module                 │ Status  │ Score   │ Notes                                  │
  ├────────────────────────┼─────────┼─────────┼────────────────────────────────────────┤
  │ f001 - Theory Schem.   │ pass    │ 80/100  │ Missing essential labels (Title/X/Y)   │
  │ f002 - Task Timeline   │ pass    │ 80/100  │ Missing essential labels (Title/X/Y)   │
  │ f003 - Omission PSTH   │ pass    │ 80/100  │ Missing essential labels (Title/X/Y)   │
  │ f004 - Pop. Manifold   │ fail    │ 50/100  │ Corrupt Data (NaN/INF); Missing Labels │
  │ f005 - TFR             │ fail    │ 50/100  │ Corrupt Data (NaN/INF); Missing Labels │
  │ f006 - Band Power      │ pass    │ 80/100  │ Missing essential labels (Title/X/Y)   │
  │ f007 - SFC             │ pass    │ 80/100  │ Missing essential labels (Title/X/Y)   │
  │ f008 - Coordination    │ pass    │ 80/100  │ Missing essential labels (Title/X/Y)   │
  │ f009 - Individual SFC  │ pass    │ 80/100  │ Missing essential labels (Title/X/Y)   │
  │ f010 - SFC Delta       │ pass    │ 80/100  │ Missing essential labels (Title/X/Y)   │
  │ f011 - Laminar Mapping │ fail    │ 50/100  │ Corrupt Data (NaN/INF); Missing Labels │
  │ f012 - CSD Profiling   │ fail    │ 50/100  │ Corrupt Data (NaN/INF); Missing Labels │
  │ f013 - Rhythmic Evol.  │ pass    │ 80/100  │ Missing essential labels (Title/X/Y)   │
  │ f014 - Spiking Granger │ pass    │ 80/100  │ Missing essential labels (Title/X/Y)   │
  │ f015 - Spectral Grang. │ pass    │ 80/100  │ Missing essential labels (Title/X/Y)   │
  │ f016 - Impedance Prof. │ fail    │ 50/100  │ Corrupt Data (NaN/INF); Missing Labels │
  │ f017 - Pred. Error     │ pass    │ 80/100  │ Missing essential labels (Title/X/Y)   │
  │ f018 - Ghost Signals   │ fail    │ 50/100  │ Corrupt Data (NaN/INF); Missing Labels │
  │ f019 - PAC Analysis    │ pass    │ 80/100  │ Missing essential labels (Title/X/Y)   │
  │ f020 - Effective Conn. │ awesome │ 100/100 │ All Sentinel checks passed.            │
  └────────────────────────┴─────────┴─────────┴────────────────────────────────────────┘

**OBJECTIVES:**
1. **Label Restoration**: Locate the source scripts for modules f001-f019. Ensure `fig.update_layout` includes explicit `title`, `xaxis_title`, and `yaxis_title`. 
2. **Background Normalization**: Force all plot backgrounds to `#FFFFFF` (White). No transparency or gray defaults allowed.
3. **Data Integrity Scrub**: Investigate the `NaN/Infinity` artifacts in the fail-state modules (f004, f005, f011, f012, f016, f018). These are likely caused by edge cases in the `DataLoader` or empty area assignments in the hierarchical split.
4. **Documentation Audit**: Ensure each output folder contains a high-density `README.md` summarizing the findings.

**CONSTRAINTS:**
- **Aesthetic**: Madelane Golden Dark (#CFB87C / #9400D3).
- **Format**: All plots must remain as interactive HTML but force the Plotly modebar to show the "Download to SVG" button.
- **Python**: Use Python 3.14 exclusively.
- **Git**: Commit remediations as a single "Aesthetic/QA Milestone" once all scores reach 100.

**SUCCESS CRITERIA:**
Rerun `src/scripts/sentinel_audit.py` and achieve an "Awesome" (100/100) status for the entire f001-f020 range in the `scoreboard.json`.
