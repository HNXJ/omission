import os

class FigureRegistry:
    # CANONICAL REPOSITORY TOPOLOGY
    FIGURE_DATA = [
        {"id": "f001", "title": "Theory Schematic", "module": "src/f001_theory", "phase": 1, "x": "Time", "y": "Area Hierarchy"},
        {"id": "f002", "title": "Omission PSTH", "module": "src/f002_psth", "phase": 1, "x": "Time", "y": "Firing Rate"},
        
        {"id": "f003", "title": "Surprise Dynamics", "module": "src/f003_surprise", "phase": 2, "x": "Time", "y": "FR Delta"},
        {"id": "f004", "title": "Unit Coding Suite", "module": "src/f004_coding", "phase": 2, "x": "Time", "y": "FR / Trials"},
        
        {"id": "f005", "title": "Time-Frequency Representation", "module": "src/f005_tfr", "phase": 3, "x": "Time", "y": "Frequency"},
        {"id": "f006", "title": "Band-Specific Power", "module": "src/f006_band_power", "phase": 3, "x": "Time", "y": "Power (dB)"},
        
        {"id": "f007", "title": "Spike-Field Coherence", "module": "src/f007_sfc", "phase": 4, "x": "Frequency", "y": "Coherence"},
        {"id": "f008", "title": "Cross-Area Coordination", "module": "src/f008_coordination", "phase": 4, "x": "Time", "y": "Correlation"},
        {"id": "f009", "title": "Individual SFC Units", "module": "src/f009_individual_sfc", "phase": 4, "x": "Frequency", "y": "Coherence"},
        {"id": "f010", "title": "SFC Delta (Surprise)", "module": "src/f010_sfc_delta", "phase": 4, "x": "Frequency", "y": "Delta Coh"},
        
        {"id": "f011", "title": "Laminar Mapping", "module": "src/f011_laminar", "phase": 5, "x": "Time", "y": "Depth"},
        {"id": "f012", "title": "CSD Profiling", "module": "src/f012_csd_profiling", "phase": 5, "x": "Time", "y": "Sink/Source Intensity"},
        {"id": "f013", "title": "Rhythmic Evolution", "module": "src/f013_rhythmic_evolution", "phase": 5, "x": "Time", "y": "Frequency"},
        {"id": "f014", "title": "Spiking Granger", "module": "src/f014_spiking_granger", "phase": 5, "x": "Frequency", "y": "Causality (GC)"},
        {"id": "f015", "title": "Spectral Granger", "module": "src/f015_spectral_granger", "phase": 5, "x": "Frequency", "y": "Causality (GC)"},
        {"id": "f016", "title": "Impedance Profiles", "module": "src/f016_impedance_profiles", "phase": 5, "x": "Frequency", "y": "Impedance (kOhm)"},
        {"id": "f017", "title": "Prediction Error Scaling", "module": "src/f017_prediction_errors", "phase": 5, "x": "Surprise Level", "y": "Response Amplitude"},
        {"id": "f018", "title": "Ghost Signals", "module": "src/f018_ghost_signals", "phase": 5, "x": "Time", "y": "LFP (uV)"},
        {"id": "f019", "title": "PAC Analysis", "module": "src/f019_pac_analysis", "phase": 5, "x": "Phase Freq", "y": "Amp Freq"},
        {"id": "f020", "title": "Effective Connectivity", "module": "src/f020_effective_connectivity", "phase": 5, "x": "Area 1", "y": "Area 2"},
        
        {"id": "f021", "title": "MaDeLaMo Schematic", "module": "src/f021_madelamo", "phase": 5, "x": "Latent State", "y": "Area Activity"},
        {"id": "f022", "title": "MaDeLaNe Projection", "module": "src/f022_madelane", "phase": 5, "x": "Component 1", "y": "Component 2"}
    ]

    @classmethod
    def get_all(cls):
        return cls.FIGURE_DATA

    @classmethod
    def get_by_id(cls, fid):
        for fig in cls.FIGURE_DATA:
            if fig['id'] == fid:
                return fig
        return None

    @classmethod
    def get_by_phase(cls, phase_num):
        return [f for f in cls.FIGURE_DATA if f['phase'] == phase_num]
