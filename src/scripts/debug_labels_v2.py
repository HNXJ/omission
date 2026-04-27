import re
import sys

def check_labels(path):
    print(f"Checking: {path}")
    content = open(path, 'r', errors='ignore').read()
    
    # Use re.DOTALL and non-greedy matching
    # Search for "xaxis": { ... "title": { "text": "..." } }
    xaxis_titles = re.findall(r'"xaxis\d*":\s*\{.*?"title":\s*\{.*?"text":\s*"(.*?)"', content, re.DOTALL)
    print(f"X-Axis Titles: {xaxis_titles}")
    
    yaxis_titles = re.findall(r'"yaxis\d*":\s*\{.*?"title":\s*\{.*?"text":\s*"(.*?)"', content, re.DOTALL)
    print(f"Y-Axis Titles: {yaxis_titles}")

    titles = re.findall(r'"title":\s*\{.*?"text":\s*"(.*?)"', content, re.DOTALL)
    print(f"Layout Titles: {titles}")

if __name__ == "__main__":
    check_labels(sys.argv[1])
