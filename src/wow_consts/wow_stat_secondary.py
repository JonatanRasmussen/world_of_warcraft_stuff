from .wow_stat_base import WowStatBase

class WowStatSecondary(WowStatBase):
    """Secondary stats in WoW (do NOT rename these. They must match names used on Wowhead.com) """
    CRIT = "Critical Strike"
    HASTE = "Haste"
    MASTERY = "Mastery"
    VERS = "Versatility"

