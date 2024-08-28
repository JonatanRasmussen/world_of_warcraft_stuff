from .wow_enum_base import WowEnumBase
from .wow_equip_type_weapon import WowEquipTypeWeapon

class WowEquipTypeArmor(WowEnumBase):
    """Armor types in WoW"""
    CLOTH = "Cloth"
    LEATHER = "Leather"
    MAIL = "Mail"
    PLATE = "Plate"

    @staticmethod
    def assign_non_empty_gear_type(armor_type: str) -> str:
        """For correct csv row sorting, ensure the gear type has a value"""
        if armor_type in WowEquipTypeArmor.get_all_ingame_names():
            return armor_type
        weapon_type = armor_type
        if weapon_type in WowEquipTypeWeapon.get_all_ingame_names():
            return WowEquipTypeWeapon.get_custom_name_shared_for_weapon_gear_type()
        return armor_type

    @staticmethod
    def get_empty_value() -> str:
        return "Other"
