---
name: analysis-omission-suite
---
# analysis-omission-suite

## Purpose
Central router for the `src/f0xx_*` figure generation pipeline. Maps analytical modules to output figures in `outputs/oglo-8figs/`.

## Input
| Name | Type | Description |
|------|------|-------------|
| target_module | str | `f0xx` analysis directory name (e.g. `f038_layer_granger`) |
| data_source | DataLoader | Via `src/core/data_loader.py` |

## Output
| Name | Type | Description |
|------|------|-------------|
| html_figures | list[str] | Interactive HTML files in `outputs/oglo-8figs/f0xx/` |
| csv_results | list[str] | Raw data exports |

## Example
```python
import subprocess
subprocess.run(["python", "src/f038_layer_granger/script.py"])
print(f"""[result] Check outputs/oglo-8figs/f038/""")
```

## Files
- [run_pipeline.py](file:///D:/drive/omission/src/scripts/run_pipeline.py) — Master executor
- [src/f0xx_*/script.py] — Per-figure entrypoints
