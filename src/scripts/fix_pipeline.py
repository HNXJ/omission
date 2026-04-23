import os
import re

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    src_dir = os.path.join(repo_root, 'src')
    pipeline_file = os.path.join(src_dir, 'scripts', 'run_pipeline.py')
    
    # Get all f0xx_ folders
    all_f0xx = []
    for item in os.listdir(src_dir):
        if os.path.isdir(os.path.join(src_dir, item)) and re.match(r'^f\d{3}_', item):
            all_f0xx.append(item)
    
    # Sort them by number
    all_f0xx.sort(key=lambda x: int(re.search(r'^f(\d{3})_', x).group(1)))
    
    with open(pipeline_file, 'r') as f:
        content = f.read()

    # Rewrite imports
    imports = []
    for item in all_f0xx:
        func_name = f"run_{item.split('_')[0]}"
        imports.append(f"from src.{item}.script import {func_name}")
    
    import_block = "\n".join(imports)
    
    content = re.sub(
        r'# Figure Imports.*?def run_all\(\):',
        f'# Figure Imports\n{import_block}\n\ndef run_all():',
        content,
        flags=re.DOTALL
    )
    
    # Rewrite pipeline steps
    steps = []
    for item in all_f0xx:
        num = item.split('_')[0][1:]
        name = " ".join([word.capitalize() for word in item.split('_')[1:]])
        func_name = f"run_{item.split('_')[0]}"
        steps.append(f'        ("Figure {int(num)}: {name}", {func_name}),')
    
    steps_block = "\n".join(steps)
    
    content = re.sub(
        r'pipeline_steps = \[.*?\]',
        f'pipeline_steps = [\n{steps_block}\n    ]',
        content,
        flags=re.DOTALL
    )
    
    with open(pipeline_file, 'w') as f:
        f.write(content)
    
    print("run_pipeline.py fixed successfully.")

if __name__ == "__main__":
    main()