from codes.config.paths import FIGURES_DIR

import os
import glob
import base64
import json
import requests
import time

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def audit_images(directory):
    png_files = glob.glob(os.path.join(directory, '**', '*.png'), recursive=True)
    print(f"Vision Audit Starting. Found {len(png_files)} PNG files to audit in {directory}")
    
    log_file = os.path.join(directory, 'vision_audit_log.txt')
    
    with open(log_file, 'w', encoding='utf-8') as f:
        for img_path in png_files:
            filename = os.path.basename(img_path)
            base64_image = encode_image(img_path)
            
            prompt = (
                "You are a strict quality control engineer auditing scientific plots. "
                "Look at this figure. Does it look legitimate? Are there actual data traces visible, "
                "or is it blank/empty? Is it excessively noisy or disorganized? "
                f"Reply with a short sentence like '{filename} looks legit' or '{filename} has no traces' "
                f"or '{filename} is too noisy' or '{filename} has no image in subpanel X'. "
                "Do not explain your reasoning, just give the verdict."
            )
            
            payload = {
                "model": "llama3.2-vision:11b-instruct-q8_0",
                "prompt": prompt,
                "images": [base64_image],
                "stream": False
            }
            
            try:
                # Assuming Ollama is running locally on default port
                response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
                response.raise_for_status()
                verdict = response.json().get('response', '').strip()
                result = f"[{time.strftime('%H:%M:%S')}] {filename}: {verdict}"
                print(result)
                f.write(result + "\n")
            except requests.exceptions.RequestException as e:
                err = f"[{time.strftime('%H:%M:%S')}] Error connecting to Vision Model for {filename}: {e}"
                print(err)
                f.write(err + "\n")
            except Exception as e:
                err = f"[{time.strftime('%H:%M:%S')}] Unexpected error auditing {filename}: {e}"
                print(err)
                f.write(err + "\n")

if __name__ == '__main__':
    target_dir = str(FIGURES_DIR / 'oglo')
    audit_images(target_dir)
    print("Vision Audit Complete.")
