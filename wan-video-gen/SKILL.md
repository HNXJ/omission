---
name: wan-video-gen
description: Specialized skill for generating AI videos and images using Wan2.1 models on Apple Silicon (M1/M2/M3) using Metal (MPS).
---

# Wan Video Generation Skill

This skill manages AI video generation on Apple Silicon using the **Wan2.1** model family and **Metal Performance Shaders (MPS)**.

## Core Workflows

### 1. Generating a Video (T2V)
Use the optimized Python script to generate high-quality videos on your M1 Max.
- **Environment**: `wan21-mlx`
- **Script**: `workspace/src/generate_video.py`
- **Output**: `workspace/media/video/`

**Command**:
```bash
conda run -n wan21-mlx python workspace/src/generate_video.py "<your prompt>"
```

### 2. Generating an Image (T2I)
For quick image concepts before committing to video.
- **Script**: `workspace/src/run_wan.py`

**Command**:
```bash
conda run -n wan21-mlx python workspace/src/run_wan.py "<your prompt>"
```

## Hardware Optimization (Apple Silicon)
- **MPS (Metal)**: All scripts are pre-configured to use `device="mps"`.
- **Unified Memory**: The 14B model requires 8-bit quantization to fit comfortably on 64GB RAM.
- **FFmpeg**: Required for exporting `.mp4` files.

## Troubleshooting
- **Model Download**: The first run will download ~3-10GB of weights from Hugging Face.
- **Performance**: If slow, ensure no other heavy GPU apps (like Chrome with many tabs or LM Studio) are active.
