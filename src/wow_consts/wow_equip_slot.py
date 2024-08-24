from typing import Optional

from .wow_enum_base import WowEnumBase

class WowEquipSlot(WowEnumBase):
    """Equip slot names in WoW (do NOT rename these. They must match names used on Wowhead.com)"""
    HEAD = "Head"
    SHOULDERS = "Shoulder"
    CHEST = "Chest"
    WRISTS = "Wrist"
    HANDS = "Hands"
    WAIST = "Waist"
    LEGS = "Legs"
    FEET = "Feet"
    NECK = "Neck"
    BACK = "Back"
    RING = "Finger"
    ONEHAND = "One-Hand"
    TWOHAND = "Two-Hand"
    RANGED = "Ranged"
    OFFHAND = "Held In Off-hand"
    MAINHAND = "Main Hand"
    SHIELD = "Off Hand"
    TRINKET = "Trinket"