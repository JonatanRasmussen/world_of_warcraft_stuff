from .wow_class import WowClass
from .wow_enum_base import WowEnumBase
from .wow_role import WowRole
from .wow_stat_primary import WowStatPrimary
from dataclasses import dataclass
from typing import List

@dataclass
class WowSpecData:
    """Data for a WoW spec"""
    spec_id: int
    ingame_name: str
    wowclass: WowClass
    role: WowRole
    mainstat: WowStatPrimary


class WowSpec(WowEnumBase):
    """Specs in WoW"""
    DK_BLOOD = WowSpecData(250, "Blood", WowClass.DK, WowRole.TANK, WowStatPrimary.STR)
    DK_FROST = WowSpecData(251, "Frost", WowClass.DK, WowRole.DPS, WowStatPrimary.STR)
    DK_UNHOLY = WowSpecData(252, "Unholy", WowClass.DK, WowRole.DPS, WowStatPrimary.STR)

    DH_HAVOC = WowSpecData(577, "Havoc", WowClass.DH, WowRole.DPS, WowStatPrimary.AGI)
    DH_VENG = WowSpecData(581, "Vengeance", WowClass.DH, WowRole.TANK, WowStatPrimary.AGI)

    DRUID_BOOMIE = WowSpecData(102, "Balance", WowClass.DRUID, WowRole.DPS, WowStatPrimary.INT)
    DRUID_CAT = WowSpecData(103, "Feral", WowClass.DRUID, WowRole.DPS, WowStatPrimary.AGI)
    DRUID_BEAR = WowSpecData(104, "Guardian", WowClass.DRUID, WowRole.TANK, WowStatPrimary.AGI)
    DRUID_RESTO = WowSpecData(105, "Restoration", WowClass.DRUID, WowRole.HEAL, WowStatPrimary.INT)

    EVOKER_DEV = WowSpecData(1467, "Devastation", WowClass.EVOKER, WowRole.DPS, WowStatPrimary.INT)
    EVOKER_PRES = WowSpecData(1468, "Preservation", WowClass.EVOKER, WowRole.HEAL, WowStatPrimary.INT)
    EVOKER_AUG = WowSpecData(1473, "Augmentation", WowClass.EVOKER, WowRole.DPS, WowStatPrimary.INT)

    HUNTER_BM = WowSpecData(253, "Beast Mastery", WowClass.HUNTER, WowRole.DPS, WowStatPrimary.AGI)
    HUNTER_MM = WowSpecData(254, "Marksmanship", WowClass.HUNTER, WowRole.DPS, WowStatPrimary.AGI)
    HUNTER_SV = WowSpecData(255, "Survival", WowClass.HUNTER, WowRole.DPS, WowStatPrimary.AGI)

    MAGE_ARCANE = WowSpecData(62, "Arcane", WowClass.MAGE, WowRole.DPS, WowStatPrimary.INT)
    MAGE_FIRE = WowSpecData(63, "Fire", WowClass.MAGE, WowRole.DPS, WowStatPrimary.INT)
    MAGE_FROST = WowSpecData(64, "Frost", WowClass.MAGE, WowRole.DPS, WowStatPrimary.INT)

    MONK_BREW = WowSpecData(268, "Brewmaster", WowClass.MONK, WowRole.TANK, WowStatPrimary.AGI)
    MONK_MW = WowSpecData(270, "Mistweaver", WowClass.MONK, WowRole.HEAL, WowStatPrimary.INT)
    MONK_WW = WowSpecData(269, "Windwalker", WowClass.MONK, WowRole.DPS, WowStatPrimary.AGI)

    PALADIN_HOLY = WowSpecData(65, "Holy", WowClass.PALADIN, WowRole.HEAL, WowStatPrimary.INT)
    PALADIN_PROT = WowSpecData(66, "Protection", WowClass.PALADIN, WowRole.TANK, WowStatPrimary.STR)
    PALADIN_RET = WowSpecData(70, "Retribution", WowClass.PALADIN, WowRole.DPS, WowStatPrimary.STR)

    PRIEST_DISC = WowSpecData(256, "Discipline", WowClass.PRIEST, WowRole.HEAL, WowStatPrimary.INT)
    PRIEST_HOLY = WowSpecData(257, "Holy", WowClass.PRIEST, WowRole.HEAL, WowStatPrimary.INT)
    PRIEST_SHADOW = WowSpecData(258, "Shadow", WowClass.PRIEST, WowRole.DPS, WowStatPrimary.INT)

    ROGUE_SIN = WowSpecData(259, "Assassination", WowClass.ROGUE, WowRole.DPS, WowStatPrimary.AGI)
    ROGUE_OUTLAW = WowSpecData(260, "Outlaw", WowClass.ROGUE, WowRole.DPS, WowStatPrimary.AGI)
    ROGUE_SUB = WowSpecData(261, "Subtlety", WowClass.ROGUE, WowRole.DPS, WowStatPrimary.AGI)

    SHAMAN_ELE = WowSpecData(262, "Elemental", WowClass.SHAMAN, WowRole.DPS, WowStatPrimary.INT)
    SHAMAN_ENH = WowSpecData(263, "Enhancement", WowClass.SHAMAN, WowRole.DPS, WowStatPrimary.AGI)
    SHAMAN_RESTO = WowSpecData(264, "Restoration", WowClass.SHAMAN, WowRole.HEAL, WowStatPrimary.INT)

    WARLOCK_AFF = WowSpecData(265, "Affliction", WowClass.WARLOCK, WowRole.DPS, WowStatPrimary.INT)
    WARLOCK_DEMO = WowSpecData(266, "Demonology", WowClass.WARLOCK, WowRole.DPS, WowStatPrimary.INT)
    WARLOCK_DEST = WowSpecData(267, "Destruction", WowClass.WARLOCK, WowRole.DPS, WowStatPrimary.INT)

    WARRIOR_ARMS = WowSpecData(71, "Arms", WowClass.WARRIOR, WowRole.DPS, WowStatPrimary.STR)
    WARRIOR_FURY = WowSpecData(72, "Fury", WowClass.WARRIOR, WowRole.DPS, WowStatPrimary.STR)
    WARRIOR_PROT = WowSpecData(73, "Protection", WowClass.WARRIOR, WowRole.TANK, WowStatPrimary.STR)

    @classmethod
    def get_spec_from_id(cls, spec_id: int) -> 'WowSpec':
        for spec in cls:
            if spec.value.spec_id == spec_id:
                return spec
        raise ValueError(f"No spec found with id {spec_id}")

    @classmethod
    def get_abbr_from_id(cls, spec_id: int) -> str:
        return cls.get_spec_from_id(spec_id).get_abbr()

    @classmethod
    def get_all_spec_ids(cls) -> List[int]:
        spec_ids: List[int] = []
        for enum in cls:
            spec_ids.append(enum.value.spec_id)
        return spec_ids

    @classmethod
    def get_all_spec_ids_for_class(cls, wowclass: WowClass) -> List[int]:
        spec_list: List[int] = []
        for spec in cls:
            if spec.value.wowclass == wowclass:
                spec_list.append(spec.get_spec_id())
        return spec_list

    @classmethod
    def get_all_spec_ids_for_role(cls, role: WowRole) -> List[int]:
        spec_list: List[int] = []
        for spec in cls:
            if spec.value.role == role:
                spec_list.append(spec.get_spec_id())
        return spec_list

    @classmethod
    def get_all_spec_ids_for_mainstat(cls, mainstat: WowStatPrimary) -> List[int]:
        spec_list: List[int] = []
        for spec in cls:
            if spec.value.mainstat == mainstat:
                spec_list.append(spec.get_spec_id())
        return spec_list

    def get_spec_id(self) -> int:
        return self.value.spec_id

    def get_ingame_name(self) -> str:
        return self.value.ingame_name

    def get_class(self) -> WowClass:
        return self.value.wowclass

    def get_role(self) -> WowRole:
        return self.value.role

    def get_mainstat(self) -> WowStatPrimary:
        return self.value.mainstat

