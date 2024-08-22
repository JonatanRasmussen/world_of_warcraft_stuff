from .wow_stat_base import WowStatBase

class WowStatPrimary(WowStatBase):
    """Primary stats in WoW (do NOT rename these. They must match names used on Wowhead.com) """
    AGI = "Agility"
    STR = "Strength"
    INT = "Intellect"