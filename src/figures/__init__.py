# Compatibility wrapper for legacy figure paths
# New figures should be accessed via src/f0XX_name/script.py

from src.f001_theory.script import run_f001 as generate_figure_1
from src.f002_psth.script import run_f002 as generate_figure_2
from src.f003_surprise.script import run_f003 as generate_figure_3
from src.f004_coding.script import run_f004 as generate_figure_4
from src.f005_tfr.script import run_f005 as generate_figure_5
from src.f006_band_power.script import run_f006 as generate_figure_6
from src.f007_sfc.script import run_f007 as generate_figure_7
from src.f008_coordination.script import run_f008 as generate_figure_8
from src.f009_individual_sfc.script import run_f009 as generate_figure_9
from src.f010_sfc_delta.script import run_f010 as generate_figure_10
from src.f011_laminar.script import run_f011 as generate_laminar_figure_11
from src.f012_mi_matrix.script import run_f012 as generate_figure_12
from src.f013_connectivity_graph.script import run_f013 as generate_figure_13
from src.f014_connectivity_delta.script import run_f014 as generate_figure_14
from src.f015_global_dynamics.script import run_f015 as generate_figure_15
from src.f016_impedance_profiles.script import run_f016 as plot_impedance_profiles
