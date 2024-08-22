from .wow_enum_base import WowEnumBase
from .wow_equip_slot import WowEquipSlot
from .wow_stat_primary import WowStatPrimary
from dataclasses import dataclass
from typing import Optional

@dataclass
class WowLootCategoryData:
    """Data for a WoW loot category"""
    equip_slot: WowEquipSlot
    mainstat: Optional[WowStatPrimary]

class WowLootCategory(WowEnumBase):
    """Loot categories for items in WoW"""
    HEAD = WowLootCategoryData(WowEquipSlot.HEAD, None)
    SHOULDERS = WowLootCategoryData(WowEquipSlot.SHOULDERS, None)
    CHEST = WowLootCategoryData(WowEquipSlot.CHEST, None)
    WRISTS = WowLootCategoryData(WowEquipSlot.WRISTS, None)
    HANDS = WowLootCategoryData(WowEquipSlot.HANDS, None)
    WAIST = WowLootCategoryData(WowEquipSlot.WAIST, None)
    LEGS = WowLootCategoryData(WowEquipSlot.LEGS, None)
    FEET = WowLootCategoryData(WowEquipSlot.FEET, None)
    NECK = WowLootCategoryData(WowEquipSlot.NECK, None)
    BACK = WowLootCategoryData(WowEquipSlot.BACK, None)
    RING = WowLootCategoryData(WowEquipSlot.RING, None)
    AGI_1H_Weapon = WowLootCategoryData(WowEquipSlot.ONEHAND, WowStatPrimary.AGI)
    STR_1H_Weapon = WowLootCategoryData(WowEquipSlot.ONEHAND, WowStatPrimary.STR)
    INT_1H_Weapon = WowLootCategoryData(WowEquipSlot.ONEHAND, WowStatPrimary.INT)
    AGI_2H_Weapon = WowLootCategoryData(WowEquipSlot.TWOHAND, WowStatPrimary.AGI)
    STR_2H_Weapon = WowLootCategoryData(WowEquipSlot.TWOHAND, WowStatPrimary.STR)
    INT_2H_Weapon = WowLootCategoryData(WowEquipSlot.TWOHAND, WowStatPrimary.INT)
    RANGED = WowLootCategoryData(WowEquipSlot.RANGED, None)
    OFFHAND = WowLootCategoryData(WowEquipSlot.OFFHAND, None)
    MAINHAND = WowLootCategoryData(WowEquipSlot.MAINHAND, None)
    SHIELD = WowLootCategoryData(WowEquipSlot.SHIELD, None)
    TRINKET = WowLootCategoryData(WowEquipSlot.TRINKET, None)

    def get_ingame_name(self) -> str:
        return self.get_equip_slot().get_ingame_name()

    def get_equip_slot(self) -> WowEquipSlot:
        return self.value.equip_slot

    def get_mainstat(self) -> Optional[WowStatPrimary]:
        return self.value.mainstat