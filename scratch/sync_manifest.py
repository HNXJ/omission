import os, json

manifest_path = r'D:\drive\omission\dashboard\src\data\manifest.json'
output_base = r'D:\drive\outputs\oglo-8figs'

with open(manifest_path, 'r') as f:
    data = json.load(f)

new_figures = []
for d in sorted(os.listdir(output_base)):
    dir_path = os.path.join(output_base, d)
    if os.path.isdir(dir_path):
        if not d.startswith('f0'): continue
        
        files = [f for f in os.listdir(dir_path) if f.endswith('.html')]
        has_readme = os.path.exists(os.path.join(dir_path, 'README.md'))
        
        title_parts = d.replace('_', ' ').replace('-', ' ').split(' ')[1:]
        title = f"{d[:4].upper()} {' '.join(p.capitalize() for p in title_parts)}"
        if len(title_parts) == 0:
            title = d.upper()
            
        new_figures.append({
            'id': d,
            'title': title.strip(),
            'baseUrl': f'/@fs/D:/drive/outputs/oglo-8figs/{d}',
            'files': files,
            'has_readme': has_readme
        })

fig_groups = {}
for fig in new_figures:
    prefix = fig['id'][:4]
    if prefix not in fig_groups:
        fig_groups[prefix] = []
    fig_groups[prefix].append(fig)

filtered_figures = []
for prefix, figs in fig_groups.items():
    if len(figs) > 1:
        # Prefer dashed
        dashed = [f for f in figs if '-' in f['id']]
        if dashed:
            filtered_figures.append(dashed[0])
        else:
            filtered_figures.append(figs[0])
    else:
        filtered_figures.append(figs[0])

data['figures'] = filtered_figures

with open(manifest_path, 'w') as f:
    json.dump(data, f, indent=2)

print(f'Updated manifest with {len(filtered_figures)} figures.')
