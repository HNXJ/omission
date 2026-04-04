# vmemory: analytical evolution & methodology standards

*Updated: April 4, 2026 | 15-step LFP pipeline integrated.*

---

## 🧠 core methodology: 4-pillar pipeline

### pillar 1: spiking dynamics & decoding
- **logic**: identify "neural surprise" latency and information content (identity vs context)
- **standards**: 50ms sliding window, SVM linear 5-fold CV, 1000ms pre-stimulus alignment
- **key finding**: PFC leads V1 in surprise detection by ~38ms

### pillar 2: spectral field coordination (15-step LFP pipeline)
- **logic**: quantify regional field changes and functional connectivity
- **pipeline**: `codes/functions/lfp_pipeline.py` (Steps 1–15)
- **normalization**: dB: `10 × log₁₀(P/P_baseline)` — Pre-p1 window −500..0ms
- **tfr**: Hanning-window, 98% overlap (nperseg=256, noverlap=251), 1–150Hz
- **bands** (authoritative):
  - Theta: 4–8Hz | Alpha: 8–13Hz | **Beta: 13–30Hz** | Gamma: 35–70Hz
- **coherence**: `scipy.signal.coherence`, all area pairs, per window
- **granger**: bivariate VAR (statsmodels), BIC lag selection, spectral domain
- **stats**: cluster permutation (n_perm=1000, threshold_p=0.05)
- **tiers**: Low=[V1,V2], Mid=[V4,MT,MST,TEO,FST], High=[V3A,V3D,FEF,PFC]
- **area order**: V1→V2→V4→MT→MST→TEO→FST→V3A→V3D→FEF→PFC (11 areas)

### pillar 3: multi-scale representational geometry (rsa/cka)
- **logic**: bridge LFP vs spikes, and stimulus vs omission contexts
- **standards**: linear CKA, 11×11 area matrices, bicubic upsampling (`zsmooth='best'`)
- **contexts**: delay, omission, stimulus, all-time

### pillar 4: behavioral precision scaling
- **logic**: direct audit of internal model via oculomotor stabilization
- **standards**: raw BHV (.mat) source, DVA precision
- **metrics**: XY variance, microsaccade density, high-frequency jitter in omission window

---

## 🔬 key empirical findings (from posters)

| Finding | Evidence | Direction |
|---------|----------|-----------|
| Omission dampens low-frequency LFP | Alpha/Beta decrease during omission window | ↓ |
| Gamma unaffected by omission | No significant gamma change in most areas | → |
| Low-freq modulation is hierarchically graded | Stronger in FEF/PFC than V1/V2 | Gradient |
| Spectral harmony flips: gamma→beta | More beta correlation during omission | Flip |
| N≈20 neurons in FEF respond to omission | Rare omission-selective spiking | Sparse |
| FEF/PFC are stable spectral nodes | Least R² change in spectral correlation | Stable |
| Ghost signal: no photodiode change | Luminance-matched omission screen | Confirmed |

---

## 🏺 aesthetic & technical mandates

- **theme**: madelane golden dark — Gold `#CFB87C`, Black `#000000`, Violet `#8F00FF`
- **condition colors**: RRRR=Gold, RXRR=Violet, RRXR=Teal, RRRX=Orange
- **vault**: `output/` (html+svg), `.npy` with `.metadata.json` sidecar
- **safety**: never save empty (NaN/0) plots — log to `context/queue/task-queue.md`
- **skills**: `.gemini/skills/` — 26 active skills, all 251–1001 tokens

---

## 📋 session metadata
- N=13 sessions, multi-area dense laminar, Utah/linear probes
- Alignment anchor: code 101.0 = photodiode p1 onset = 0ms
- Sampling rate: `FS_LFP = 1000.0 Hz` (hardcoded in `lfp_constants.py`)
- Electrode table: `location` column → area assignment; `depth` → laminar position

---

## ⚡ active pipeline status
| Item | Status |
|------|--------|
| `lfp_pipeline.py` (15 steps) | ✅ implemented |
| `poster_figures.py` (10 figure functions) | ✅ implemented |
| `lfp_stats.py` cluster permutation | ✅ real implementation |
| Beta band | ✅ updated → 13–30Hz |
| `FS_LFP` constant propagated | ✅ done |
| `fx` baseline window | ✅ corrected → −500ms |
| `run_cluster_permutation` | ✅ real (not placeholder) |
| `compute_spectral_granger` | ✅ VAR-based implementation |
| 26 skills — all within 251–1001 tokens | ✅ verified |
| Function coverage 78/78 (100%) | ✅ verified |

## 🗂 pending
- Run 15-step pipeline on all 13 sessions
- Generate figure revision panels
- Move 17 script-like files from `codes/functions/` → `codes/scripts/`
- Finalize BioRxiv manuscript (12p, 10f)
