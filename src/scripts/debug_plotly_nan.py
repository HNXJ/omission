import re
import sys

def check_file(path):
    print(f"Checking: {path}")
    try:
        content = open(path, 'r', errors='ignore').read()
    except Exception as e:
        print(f"Error reading: {e}")
        return

    # Find Plotly JSON data
    # Plotly.newPlot("id", [DATA], {LAYOUT})
    matches = list(re.finditer(r'Plotly\.newPlot\(', content))
    if not matches:
        print("No Plotly.newPlot found")
        return

    for match in matches:
        start = match.end()
        # Find the start of the data array [
        data_start = content.find('[', start)
        if data_start == -1: continue
        
        # Simple bracket matcher to find the end of [ ... ]
        bracket_level = 0
        data_end = -1
        for i in range(data_start, len(content)):
            if content[i] == '[': bracket_level += 1
            elif content[i] == ']':
                bracket_level -= 1
                if bracket_level == 0:
                    data_end = i + 1
                    break
        
        if data_end == -1: continue
        
        data_json = content[data_start:data_end]
        nan_count = data_json.count('NaN')
        inf_count = data_json.count('Infinity')
        
        print(f"Data section ({data_start}:{data_end}): NaN={nan_count}, Infinity={inf_count}")
        if nan_count > 0:
            # Show snippet of first NaN
            idx = data_json.find('NaN')
            print(f"  Snippet: ...{data_json[max(0, idx-50):idx+50]}...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_file(sys.argv[1])
