"""
Configuration for EEG channel mapping and layout.
"""

# Physical-to-logical channel mapping for your board

# #FG_P 16/5
# # EEGCAP = Tenocom 32ch
# CHANNEL_MAPPING = {1: "T7", 2: "T8", 3: "C3", 4: "C4", 5: "FC3", 6: "FC4", 7: "CP3", 8: "CP4"} # FG_P 16/5
# # Active EEG channels to use (hardware indices)
# EXG_CHANNELS = [1, 2, 4, 5, 6, 7, 8] #F G_P 06/11
# # Optional: define a virtual differential channel (e.g. C3–C4)
# VIRTUAL_CHANNEL_NAME = "C3–C4"
# # REFERENCE = linked ears
# # VCM_BIAS = GND (FPZ|FZ)

# #FG_P 06/11
# # EEGCAP = Tenocom 32ch
# CHANNEL_MAPPING = {1: "T7", 2: "C3", 5: "T8", 6: "FC4", 9: "FC3", 10: "C4", 13: "CP3", 14: "CP4"} # FG_P 06/11
# # Active EEG channels to use (hardware indices)
# EXG_CHANNELS = [1, 2, 5, 6, 9, 10, 13, 14] #F G_P 06/11
# # Optional: define a virtual differential channel (e.g. C3–C4)
# VIRTUAL_CHANNEL_NAME = "C3–C4"
# # REFERENCE = REF (CZ|CPZ)
# # VCM_BIAS = GND (FPZ|FZ)

#FREG8#
# FG_P 13/11
# EEGCAP = Tenocom 32ch
CHANNEL_MAPPING = {1: "T7", 2: "C3", 5: "T8", 6: "FC4", 9: "FC3", 10: "C4", 13: "CP3", 14: "CP4", 26: "x26", 30: "x30"} # FG_P 06/11
# Active EEG channels to use (hardware indices)
EXG_CHANNELS = [1, 2, 5, 6, 9, 10, 13, 14, 26, 30] #F G_P 06/11
# Optional: define a virtual differential channel (e.g. C3–C4)
VIRTUAL_CHANNEL_NAME = "C3–C4"
# REFERENCE = linked ears
# VCM_BIAS = GND (FPZ|FZ)
# x26 = 'shorted with jumper'
# x30 = 'open | floating | no wire'