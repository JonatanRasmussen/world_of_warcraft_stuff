from dataclasses import dataclass
from typing import Optional

from .wow_enum_base import WowEnumBase
from .wow_role import WowRole
from .wow_equip_slot import WowEquipSlot
from .wow_stat_primary import WowStatPrimary


@dataclass
class WowLootCategoryData:
    """Data for a WoW loot category"""
    equip_slot: WowEquipSlot
    mainstat: Optional[WowStatPrimary]
    role: Optional[WowRole]

class WowLootCategory(WowEnumBase):
    """Loot categories for items in WoW"""
    HEAD = WowLootCategoryData(WowEquipSlot.HEAD, None, None)
    SHOULDERS = WowLootCategoryData(WowEquipSlot.SHOULDERS, None, None)
    CHEST = WowLootCategoryData(WowEquipSlot.CHEST, None, None)
    WRISTS = WowLootCategoryData(WowEquipSlot.WRISTS, None, None)
    HANDS = WowLootCategoryData(WowEquipSlot.HANDS, None, None)
    WAIST = WowLootCategoryData(WowEquipSlot.WAIST, None, None)
    LEGS = WowLootCategoryData(WowEquipSlot.LEGS, None, None)
    FEET = WowLootCategoryData(WowEquipSlot.FEET, None, None)
    NECK = WowLootCategoryData(WowEquipSlot.NECK, None, None)
    BACK = WowLootCategoryData(WowEquipSlot.BACK, None, None)
    RING = WowLootCategoryData(WowEquipSlot.RING, None, None)
    AGI_1H_Weapon = WowLootCategoryData(WowEquipSlot.ONEHAND, WowStatPrimary.AGI, None)
    STR_1H_Weapon = WowLootCategoryData(WowEquipSlot.ONEHAND, WowStatPrimary.STR, None)
    INT_1H_Weapon = WowLootCategoryData(WowEquipSlot.ONEHAND, WowStatPrimary.INT, None)
    AGI_2H_Weapon = WowLootCategoryData(WowEquipSlot.TWOHAND, WowStatPrimary.AGI, None)
    STR_2H_Weapon = WowLootCategoryData(WowEquipSlot.TWOHAND, WowStatPrimary.STR, None)
    INT_2H_Weapon = WowLootCategoryData(WowEquipSlot.TWOHAND, WowStatPrimary.INT, None)
    RANGED = WowLootCategoryData(WowEquipSlot.RANGED, None, None)
    OFFHAND = WowLootCategoryData(WowEquipSlot.OFFHAND, None, None)
    MAINHAND = WowLootCategoryData(WowEquipSlot.MAINHAND, None, None)
    SHIELD = WowLootCategoryData(WowEquipSlot.SHIELD, None, None)
    DPS_TRINKET = WowLootCategoryData(WowEquipSlot.TRINKET, None, WowRole.DPS)
    HEAL_TRINKET = WowLootCategoryData(WowEquipSlot.TRINKET, None, WowRole.HEAL)
    TANK_TRINKET = WowLootCategoryData(WowEquipSlot.TRINKET, None, WowRole.TANK)
    ANYROLE_TRINKET = WowLootCategoryData(WowEquipSlot.TRINKET, None, None)

    @staticmethod
    def get_trinket_gear_type(wow_role: Optional['WowRole'] = None) -> str:
        if wow_role:
            abbr = wow_role.get_abbr()
        else:
            abbr = WowLootCategory.get_trinket_multirole_str()
        return f"{abbr} {WowEquipSlot.TRINKET.get_abbr()}"

    @staticmethod
    def get_trinket_multirole_str() -> str:
        return "Anyrole"

    @staticmethod
    def convert_abbr_to_ingame_equipslot(loot_category_abbr: str) -> str:
        return WowLootCategory.get_from_abbr(loot_category_abbr).get_ingame_name()

    def get_ingame_name(self) -> str:
        return self.get_equip_slot().get_ingame_name()

    def get_equip_slot(self) -> WowEquipSlot:
        return self.value.equip_slot

    def get_mainstat(self) -> Optional[WowStatPrimary]:
        return self.value.mainstat

    def get_role(self) -> Optional[WowRole]:
        return self.value.role