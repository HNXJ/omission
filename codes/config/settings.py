# Global project settings and constants

FS_LFP = 1000.0   # Hz
BETA_BAND = (13, 30)
FX_TIME = -500    # ms
P1_TIME = 0       # ms
NORMALIZATION = "dB"

# Aesthetic mandates
COLORS = {
    "GOLD": "#CFB87C",
    "VIOLET": "#8F00FF",
    "BLACK": "#000000"
}
CONDITION_COLORS = {
    "RRRR": COLORS["GOLD"],
    "RXRR": COLORS["VIOLET"],
    "RRXR": "#008080", # Teal
    "RRRX": "#FFA500"  # Orange
}
THEME = "plotly_white"
