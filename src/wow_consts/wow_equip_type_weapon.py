from .wow_enum_base import WowEnumBase

class WowEquipTypeWeapon(WowEnumBase):
    """Weapon types in WoW"""
    SWORD = "Sword"
    MACE = "Mace"
    AXE = "Axe"
    DAGGER = "Dagger"
    FIST_WEAPON = "Fist Weapon"
    WARGLAIVE = "Warglaive"
    POLEARM = "Polearm"
    STAFF = "Staff"
    BOW = "Bow"
    CROSSBOW = "Crossbow"
    GUN = "Gun"

    @staticmethod
    def get_custom_name_shared_for_weapon_gear_type() -> str:
        return "Weapon"