import plotly.graph_objects as go
from pathlib import Path
from src.f047_stability_audit.analysis import run_stability_audit
from src.analysis.io.logger import log

def run_f047():
    """
    Standard runner for Figure 47: Pipeline Stability Audit.
    """
    print(f"""[action] Starting Figure 47 generation runner...""")
    
    # Execute analysis
    print(f"""[action] Calling run_stability_audit()...""")
    audit_results = run_stability_audit()
    print(f"""[action] Audit results received.""")
    
    # Extract data for plotting
    print(f"""[action] Parsing audit results for Plotly...""")
    tests = [r['test'] for r in audit_results]
    statuses = [r['status'] for r in audit_results]
    details = [r['detail'] for r in audit_results]
    print(f"""[action] Data arrays prepared.""")
    
    # Map status to colors
    print(f"""[action] Mapping status to colors...""")
    colors = []
    for s in statuses:
        if s == "PASS": colors.append("green")
        elif s == "FAIL": colors.append("red")
        else: colors.append("orange") # WARN
    print(f"""[action] Color mapping complete.""")

    # Create Table Figure
    print(f"""[action] Building Plotly Table figure...""")
    fig = go.Figure(data=[go.Table(
        header=dict(values=['Test Case', 'Status', 'Details'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[tests, statuses, details],
                   fill_color=[['white']*len(tests), colors, ['white']*len(tests)],
                   align='left'))
    ])
    print(f"""[action] Figure object constructed.""")

    print(f"""[action] Updating layout templates...""")
    fig.update_layout(
        title="Omission Pipeline Stability Audit (Phase 6)",
        template="plotly_white",
        modebar_add=['toImage']
    )
    print(f"""[action] Layout updated.""")

    # Save output
    print(f"""[action] Ensuring output directory existence...""")
    output_dir = Path("outputs/oglo-8figs/f047-stability-audit")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"""[action] Directory ready: {output_dir}""")
    
    output_path = output_dir / "index.html"
    print(f"""[action] Writing HTML to {output_path}...""")
    fig.write_html(str(output_path))
    print(f"""[action] SUCCESS: Audit report generated.""")

if __name__ == "__main__":
    run_f047()
