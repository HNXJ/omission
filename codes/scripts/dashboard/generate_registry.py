import os
from pathlib import Path

OUTPUT_ROOT = Path(r'D:\drive\omission\outputs\oglo-figures')

def generate_dashboard():
    dashboard_path = OUTPUT_ROOT / "Project_Figure_Registry.html"
    
    html_content = """
    <html>
    <head>
        <title>Omission Project Figure Registry</title>
        <style>
            body { font-family: sans-serif; background: #1a1a1a; color: #cfb87c; margin: 40px; }
            h1 { color: #9400d3; }
            .section { margin-bottom: 40px; background: #2a2a2a; padding: 20px; border-radius: 8px; }
            a { color: #56b4e9; text-decoration: none; }
            a:hover { text-decoration: underline; }
            ul { list-style-type: none; padding: 0; }
            li { margin-bottom: 5px; }
        </style>
    </head>
    <body>
        <h1>Omission Project: Final Figure Registry</h1>
        <p>Canonical collection of generated figures for the 2026 manuscript.</p>
    """
    
    # Traverse directory and categorize
    for fig_dir in sorted(OUTPUT_ROOT.glob("figure-*")):
        if not fig_dir.is_dir(): continue
        
        section_name = fig_dir.name.replace("-", " ").capitalize()
        html_content += f'<div class="section"><h2>{section_name}</h2><ul>'
        
        for file in sorted(fig_dir.glob("*.html")):
            rel_path = os.path.relpath(file, OUTPUT_ROOT)
            html_content += f'<li><a href="{rel_path}" target="_blank">{file.name}</a></li>'
            
        html_content += '</ul></div>'
        
    html_content += "</body></html>"
    
    with open(dashboard_path, 'w') as f:
        f.write(html_content)
    print(f"Dashboard generated at: {dashboard_path}")

if __name__ == "__main__":
    generate_dashboard()
