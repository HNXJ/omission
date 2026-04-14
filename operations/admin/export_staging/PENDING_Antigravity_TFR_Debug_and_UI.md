# Directive: TFR Pipeline Debugging & UI Construction

## Assigned To: Antigravity Node
## From: Gemini CLI (Executive Orchestrator)

### Objective
The TFR generation pipeline is currently slow and prone to hangs during the processing of high-channel-count probes (PFC area). You are tasked with deep-inspecting the trace extraction logic and building a real-time UI for monitoring these results.

### Tasks
1. **Deep Inspection**: Audit the `generate_figure_6_7_tfr.py` execution logs. Identify why `local_ch` processing hangs or slows down significantly beyond epoch 311.
2. **UI Construction**: Generate an interactive HTML/JS dashboard that visualizes the TFR results in real-time as they are computed.
3. **Real-time Testing**: Implement a test harness that validates the spectral consistency of the traces as they are generated.

### Mandatory Protocols
- **Safety**: Commit-Pull-Push after EVERY change.
- **Reporting**: Stage results in `Export_Staging/PENDING_Antigravity_TFR_Dashboard.md` for executive review before transfer.
- **Efficiency**: Use the `nwbinspector` reports (found in `operations/qc/reports/nwbinspector/`) as context for potential data-quality-related bottlenecks.
