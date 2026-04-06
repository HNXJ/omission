
import os
import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="Omission Analysis Viewer")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WORKSPACE_ROOT = "D:/Analysis/Omission/local-workspace"
CHECKPOINT_DIR = os.path.join(WORKSPACE_ROOT, "data/checkpoints")
FIGURES_DIR = os.path.join(WORKSPACE_ROOT, "figures")

# Mount figures directory to serve static files
if os.path.exists(FIGURES_DIR):
    app.mount("/static_figures", StaticFiles(directory=FIGURES_DIR), name="static_figures")

@app.get("/api/files")
def list_files():
    all_files = []
    
    # 1. Checkpoints
    if os.path.exists(CHECKPOINT_DIR):
        for f in os.listdir(CHECKPOINT_DIR):
            if f.endswith(('.json', '.csv')):
                all_files.append({"name": f, "type": "checkpoint", "path": f"checkpoints/{f}"})
    
    # 2. Figures (Recursive)
    if os.path.exists(FIGURES_DIR):
        for root, dirs, files in os.walk(FIGURES_DIR):
            for f in files:
                if f.endswith(('.html', '.svg', '.png', '.jpg')):
                    rel_path = os.path.relpath(os.path.join(root, f), FIGURES_DIR)
                    all_files.append({
                        "name": f, 
                        "type": "figure", 
                        "path": rel_path.replace("\\", "/")
                    })
    
    return {"files": all_files}

@app.get("/api/data/checkpoints/{filename}")
def get_checkpoint_data(filename: str):
    path = os.path.join(CHECKPOINT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    
    if filename.endswith('.json'):
        with open(path, 'r') as f:
            return json.load(f)
    elif filename.endswith('.csv'):
        df = pd.read_csv(path)
        return df.head(2000).to_dict(orient='records')
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>🏺 Omission Viewer</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: 'Consolas', 'Courier New', monospace; background: #000; color: #CFB87C; margin: 0; padding: 20px; overflow: hidden;}
        h1 { border-bottom: 2px solid #8F00FF; padding-bottom: 10px; margin-top: 0; font-size: 20px;}
        .container { display: flex; gap: 20px; height: 90vh; }
        .sidebar { width: 350px; background: #111; padding: 15px; border-radius: 8px; border: 1px solid #333; overflow-y: auto; }
        .main { flex-grow: 1; background: #050505; padding: 20px; border-radius: 8px; border: 1px solid #333; display: flex; flex-direction: column; overflow: hidden;}
        .file-item { padding: 6px 10px; cursor: pointer; border-bottom: 1px solid #222; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .file-item:hover { background: #8F00FF22; color: #fff; }
        .file-item.active { background: #8F00FF; color: #000; font-weight: bold; }
        .tag { font-size: 10px; padding: 2px 4px; border-radius: 3px; margin-right: 5px; text-transform: uppercase; }
        .tag-checkpoint { background: #444; color: #fff; }
        .tag-figure { background: #8F00FF; color: #fff; }
        
        #viewer-content { flex-grow: 1; position: relative; width: 100%; height: 100%; }
        #plot, #frame { width: 100%; height: 100%; border: none; background: #fff; border-radius: 4px;}
        #plot { background: #111; }
        
        .controls { margin-bottom: 10px; display: flex; gap: 10px; align-items: center; }
        select, button { background: #111; color: #CFB87C; border: 1px solid #CFB87C; padding: 4px 8px; border-radius: 4px; font-family: inherit;}
        button:hover { background: #CFB87C; color: #000; cursor: pointer;}
        #stats-panel { height: 150px; overflow: auto; background: #111; border: 1px solid #333; padding: 10px; font-size: 11px; margin-top: 10px; color: #888;}
    </style>
</head>
<body>
    <h1>🏺 OMISSION ANALYSIS HUB <span style="color:#8F00FF">| Golden Dark</span></h1>
    <div class="container">
        <div class="sidebar">
            <div id="files-container">Loading assets...</div>
        </div>
        <div class="main">
            <div class="controls" id="controls">
                <span id="current-filename">Select an asset from the vault</span>
            </div>
            <div id="viewer-content">
                <div id="plot"></div>
                <iframe id="frame" style="display:none"></iframe>
            </div>
            <div id="stats-panel">JSON/CSV Metadata Preview...</div>
        </div>
    </div>

    <script>
        const THEME = {
            plot_bgcolor: "#111", paper_bgcolor: "#111",
            font: { color: "#CFB87C", family: "Consolas" },
            xaxis: { gridcolor: "#222", zerolinecolor: "#444" },
            yaxis: { gridcolor: "#222", zerolinecolor: "#444" }
        };

        async function init() {
            const resp = await fetch('/api/files');
            const data = await resp.json();
            const container = document.getElementById('files-container');
            container.innerHTML = '';
            
            data.files.forEach(f => {
                const div = document.createElement('div');
                div.className = 'file-item';
                const tag = document.createElement('span');
                tag.className = `tag tag-${f.type}`;
                tag.innerText = f.type[0];
                div.appendChild(tag);
                div.appendChild(document.createTextNode(f.name));
                div.onclick = () => selectFile(f, div);
                container.appendChild(div);
            });
        }

        async function selectFile(file, element) {
            document.querySelectorAll('.file-item').forEach(e => e.classList.remove('active'));
            element.classList.add('active');
            document.getElementById('current-filename').innerText = file.name;
            
            const plotDiv = document.getElementById('plot');
            const frame = document.getElementById('frame');
            const controls = document.getElementById('controls');
            const stats = document.getElementById('stats-panel');
            
            if (file.type === 'figure') {
                plotDiv.style.display = 'none';
                frame.style.display = 'block';
                frame.src = `/static_figures/${file.path}`;
                controls.innerHTML = `<span>FIGURE: ${file.name}</span>`;
                stats.innerText = `Location: figures/${file.path}`;
            } else {
                frame.style.display = 'none';
                plotDiv.style.display = 'block';
                const resp = await fetch(`/api/data/${file.path}`);
                const data = await resp.json();
                stats.innerText = JSON.stringify(data, null, 2).substring(0, 5000);
                renderData(file.name, data);
            }
        }

        function renderData(filename, data) {
            const controls = document.getElementById('controls');
            controls.innerHTML = '';
            
            if (Array.isArray(data)) {
                // Table / Scatter from CSV or List
                renderTablePlot(data);
            } else {
                // Nested JSON Traces
                renderTraceSelector(data);
            }
        }

        function renderTablePlot(data) {
            const keys = Object.keys(data[0] || {}).filter(k => typeof data[0][k] === 'number');
            if (keys.length < 2) return;
            
            const controls = document.getElementById('controls');
            controls.innerHTML = `
                X: <select id="x-sel">${keys.map(k=>`<option>${k}</option>`).join('')}</select>
                Y: <select id="y-sel">${keys.map(k=>`<option ${k.includes('acc')?'selected':''}>${k}</option>`).join('')}</select>
                Group: <select id="g-sel"><option>None</option>${Object.keys(data[0]).map(k=>`<option>${k}</option>`).join('')}</select>
                <button onclick="updateTablePlot()">Update Plot</button>
            `;
            window.currentTableData = data;
            updateTablePlot();
        }

        function updateTablePlot() {
            const xk = document.getElementById('x-sel').value;
            const yk = document.getElementById('y-sel').value;
            const gk = document.getElementById('g-sel').value;
            const data = window.currentTableData;
            
            let plotData = [];
            if (gk === 'None') {
                plotData.push({
                    x: data.map(d => d[xk]),
                    y: data.map(d => d[yk]),
                    mode: 'markers',
                    type: 'scatter',
                    marker: { color: '#8F00FF', size: 10 }
                });
            } else {
                const groups = [...new Set(data.map(d => d[gk]))];
                groups.forEach(g => {
                    const gd = data.filter(d => d[gk] === g);
                    plotData.push({
                        x: gd.map(d => d[xk]),
                        y: gd.map(d => d[yk]),
                        name: String(g),
                        mode: 'markers',
                        type: 'scatter'
                    });
                });
            }
            Plotly.newPlot('plot', plotData, { ...THEME, title: `${yk} vs ${xk}` });
        }

        function renderTraceSelector(data) {
            const keys = Object.keys(data);
            const controls = document.getElementById('controls');
            const select = document.createElement('select');
            select.multiple = true;
            select.style.height = "30px";
            keys.forEach(k => {
                const opt = document.createElement('option');
                opt.value = opt.innerText = k;
                select.appendChild(opt);
            });
            controls.appendChild(select);
            const btn = document.createElement('button');
            btn.innerText = "Trace Plot";
            btn.onclick = () => {
                const selected = Array.from(select.selectedOptions).map(o => o.value);
                const plotData = [];
                selected.forEach(k => {
                    let d = data[k];
                    if (!Array.isArray(d)) return;
                    
                    // Handle list of sessions or direct list
                    const series = Array.isArray(d[0]) ? d[0] : (d[0].val || d);
                    const time = d[0].time || series.map((_, i) => i);
                    
                    plotData.push({
                        x: time,
                        y: series,
                        name: k,
                        type: 'scatter',
                        mode: 'lines'
                    });
                });
                Plotly.newPlot('plot', plotData, { ...THEME, title: 'Temporal Dynamics' });
            };
            controls.appendChild(btn);
        }

        init();
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8181)
