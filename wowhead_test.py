import csv
import json
import re
from dataclasses import dataclass
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Optional, Final, Set, Dict, Any, List, TypeVar, Type

from scrape_utils import ScrapeUtils

WowEnumT = TypeVar('WowEnumT', bound='WowEnumBase')

class WowEnumBase(Enum):
    """Base class for all WoW enums."""

    @classmethod
    def get_all(cls: Type[WowEnumT]) -> List[WowEnumT]:
        return list(cls)

    @classmethod
    def get_all_abbrs(cls) -> List[str]:
        abbreviations: List[str] = []
        for enum in cls:
            abbreviations.append(enum.get_abbr())
        return abbreviations

    @classmethod
    def get_all_ingame_names(cls) -> str:
        ingame_names: List[str] = []
        for enum in cls:
            ingame_names.append(enum.get_ingame_name())
        return ingame_names

    @classmethod
    def get_from_ingame_name(cls, ingame_name: str) -> Type[WowEnumT]:
        for enum in cls:
            if enum.get_ingame_name() == ingame_name:
                return enum

    def get_abbr(self) -> str:
        return ''.join(word.capitalize() for word in self.name.split('_'))

    def get_ingame_name(self) -> str:
        return self.value




class WowStatBase(WowEnumBase):
    """Base class for WoW primary and secondary stats providing common methods."""

    def get_single_letter_name(self) -> str:
        return self.name[0]


class WowStatPrimary(WowStatBase):
    """Primary stats in WoW (do NOT rename these. They must match names used on Wowhead.com) """
    AGI = "Agility"
    STR = "Strength"
    INT = "Intellect"


class WowStatSecondary(WowStatBase):
    """Secondary stats in WoW (do NOT rename these. They must match names used on Wowhead.com) """
    CRIT = "Critical Strike"
    HASTE = "Haste"
    MASTERY = "Mastery"
    VERS = "Versatility"


class WowRole(WowEnumBase):
    """Roles in WoW"""
    TANK = "Tank"
    HEAL = "Healer"
    DPS = "Dps"


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
    TANK_TRINKET = WowLootCategoryData(WowEquipSlot.TRINKET, None, WowRole.TANK)
    HEAL_TRINKET = WowLootCategoryData(WowEquipSlot.TRINKET, None, WowRole.HEAL)
    DPS_AGI_TRINKET = WowLootCategoryData(WowEquipSlot.TRINKET, WowStatPrimary.AGI, WowRole.DPS)
    DPS_STR_TRINKET = WowLootCategoryData(WowEquipSlot.TRINKET, WowStatPrimary.STR, WowRole.DPS)
    DPS_INT_TRINKET = WowLootCategoryData(WowEquipSlot.TRINKET, WowStatPrimary.INT, WowRole.DPS)

    def get_ingame_name(self) -> str:
        return self.get_equip_slot().get_ingame_name

    def get_name(self) -> str:
        return self.value.name

    def get_equip_slot(self) -> WowEquipSlot:
        return self.value.equip_slot

    def get_mainstat(self) -> Optional[WowStatPrimary]:
        return self.value.mainstat

    def get_role(self) -> Optional[WowRole]:
        return self.value.role

class WowClass(WowEnumBase):
    """Classes in WoW """
    DK = "Death Knight"
    DH = "Demon Hunter"
    DRUID = "Druid"
    EVOKER = "Evoker"
    HUNTER = "Hunter"
    MAGE = "Mage"
    MONK = "Monk"
    PALADIN = "Paladin"
    PRIEST = "Priest"
    ROGUE = "Rogue"
    SHAMAN = "Shaman"
    WARLOCK = "Warlock"
    WARRIOR = "Warrior"


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
        return self.value.spec_id

    def get_role(self) -> WowRole:
        return self.value.role

    def get_mainstat(self) -> WowStatPrimary:
        return self.value.mainstat



class WowheadItem:
    """Represents a WoW item with data scraped from Wowhead."""

    # Constants for parsed data keys
    ITEM_ID = 'item_id'
    NAME = 'name'
    ITEM_LEVEL = 'item_level'
    BIND = 'bind'
    GEAR_SLOT = 'gear_slot'
    GEAR_TYPE = 'gear_type'
    UNIQUE = 'unique'
    PRIMARY_STATS = 'primary_stats'
    SECONDARY_STATS = 'secondary_stats'
    REQUIRED_LEVEL = 'required_level'
    SELL_PRICE = 'sell_price'
    DROPPED_BY = 'dropped_by'
    SPEC_IDS = 'spec_ids'
    SPEC_NAMES = 'spec_names'
    MAINSTAT = 'mainstat'
    DISTRIBUTION = 'distribution'
    STATS = 'stats'
    DROPPED_IN = 'dropped_in'
    FROM = 'from'
    BOSS_POSITION = 'boss_position'

    json_folder: Path = Path.cwd() / "wowhead_items"
    csv_folder: Path = Path.cwd() / "wowhead_item_csv"
    instances: Dict[int, 'WowheadItem'] = {}

    def __init__(self, item_id: int, html_string: str):
        """Initialize WowheadItem with item ID and HTML content."""
        self.item_id: int = item_id
        self.html_string: str = html_string
        self.parsed_data: Dict[str, Any] = {}
        self.parse(item_id)
        WowheadItem.instances[item_id] = self

    @staticmethod
    def register_instance(item_id: int, instance: 'WowheadItem') -> None:
        WowheadItem.instances[item_id] = instance

    @staticmethod
    def get_all_items_for_spec(spec_id: int) -> Set['WowheadItem']:
        items: Set['WowheadItem'] = set()
        for item in WowheadItem.instances.values():
            if not item.is_mount_or_quest_item():
                integer_spec_ids: List[int] = []
                for scraped_spec_id in item.parsed_data[WowheadItem.SPEC_IDS]:
                    if isinstance(scraped_spec_id, int):
                        integer_spec_ids.append(scraped_spec_id)
                    else:
                        print(f"{scraped_spec_id} is not an int. It is type {scraped_spec_id.type()}")
                if spec_id in integer_spec_ids:
                    items.add(item)
        return items

    @staticmethod
    def get_all_items_for_spec_and_slot(spec_id: int, slot_name: str) -> Set['WowheadItem']:
        items: Set['WowheadItem'] = set()
        for item in WowheadItem.get_all_items_for_spec(spec_id):
            if item.parsed_data['gear_slot'] == slot_name:
                items.add(item)
        return items

    def parse(self, item_id: int) -> None:
        """Parse HTML content to extract item data."""
        self.parsed_data[self.ITEM_ID] = item_id
        self.parsed_data[self.NAME] = self.extract_content(r'<h1 class="heading-size-1">(.*?)</h1>')
        self.parsed_data[self.ITEM_LEVEL] = self.extract_content(r'Item Level <!--ilvl-->(\d+)')
        self.parsed_data[self.BIND] = "Soulbound" if "Binds when picked up" in self.html_string else "BoE"
        self.parsed_data[self.GEAR_SLOT] = self.extract_content(r'<table width="100%"><tr><td>(.*?)</td>')
        self.parsed_data[self.GEAR_TYPE] = self.extract_item_subtype()
        self.parsed_data[self.UNIQUE] = "Unique-Equipped" in self.html_string
        self.parsed_data[self.PRIMARY_STATS] = self.extract_primary_stats()
        self.parsed_data[self.SECONDARY_STATS] = self.extract_secondary_stats()
        self.parsed_data[self.REQUIRED_LEVEL] = self.extract_content(r'Requires Level <!--rlvl-->(\d+)')
        self.parsed_data[self.SELL_PRICE] = self.extract_sell_price()
        self.parsed_data[self.DROPPED_BY] = self.extract_content(r'Dropped by: (.*?)</div>')
        self.parsed_data[self.SPEC_IDS] = self.extract_spec_ids()
        self.parsed_data[self.SPEC_NAMES] = self.extract_spec_names()

    @staticmethod
    def parse_statistics_across_all_items_and_write_json() -> None:
        # Requires all other items to have been scraped already
        for item_id in WowheadZone.get_all_item_ids():
            item = WowheadItem.instances[item_id]
            item.add_statistic_item_drop_chance_per_spec()
            item.add_statistic_dungeon_name()
            item.add_statistic_boss_position()
            item.convert_to_json_and_save_to_disk()
        # Also save zones to json
        for zone_id in WowheadZoneList.get_all_zone_ids():
            zone = WowheadZone.instances[zone_id]
            zone.convert_to_json_and_save_to_disk()

    def extract_content(self, pattern: str) -> Optional[str]:
        """Extract content from HTML using regex pattern."""
        match = re.search(pattern, self.html_string)
        return match.group(1) if match else None

    def extract_item_subtype(self) -> Optional[str]:
        """Extract the item subtype (armor type or weapon type) from the HTML content."""
        pattern = r'<table width="100%"><tr><td>[^<]+</td><th><!--scstart\d+:\d+--><span class="q1">([^<]+)</span><!--scend--></th></tr></table>'
        match = re.search(pattern, self.html_string)
        return match.group(1) if match else None

    def extract_primary_stats(self) -> Dict[str, int]:
        stats = {}
        for stat_enum in WowStatPrimary.get_all():
            stat = stat_enum.get_ingame_name()
            pattern = rf'\+([0-9,]+) \[?([^\]]*{stat}[^\]]*)\]?'
            value = self.extract_content(pattern)
            if value:
                # Remove commas and convert to integer
                stats[stat] = int(value.replace(',', ''))
        self.format_primary_stat_label(stats)
        return stats

    def format_primary_stat_label(self, stat_dict: Dict[str, int]) -> None:
        stats_found: List[str] = []
        for stat in WowStatPrimary.get_all_ingame_names():
            if stat in stat_dict:
                stats_found.append(stat)
                self.parsed_data[stat.lower()] = f"{100}%"
            else:
                self.parsed_data[stat.lower()] = f"{0}%"
        if "Str" in stats_found and "Agi" in stats_found and "Int" in stats_found:
            self.parsed_data[self.MAINSTAT] = "All 3"
        else:
            self.parsed_data[self.MAINSTAT] = ",".join(stats_found)

    def extract_secondary_stats(self) -> Dict[str, int]:
        stats = {}
        for stat in WowStatSecondary.get_all_ingame_names():
            value = self.extract_content(rf'([0-9,]+) {stat}')
            if value:
                # Remove commas and convert to integer
                stats[stat] = int(value.replace(',', ''))
        self.extract_secondary_stat_distribution(stats)
        return stats

    def extract_secondary_stat_distribution(self, stat_dict: Dict[str, int]) -> None:
        total_stats = 0
        for stat in stat_dict:
            total_stats += stat_dict[stat]
        distribution: List[str] = []
        for stat in WowStatSecondary.get_all_ingame_names():
            if stat not in stat_dict or stat_dict[stat] == 0:
                self.parsed_data[stat.lower()] = f"{0}%"
            else:
                percent = f"{100 * stat_dict[stat] // total_stats}%"
                self.parsed_data[stat.lower()] = percent
                distribution.append(f"{percent} {stat}")
        distribution.sort(reverse=True)
        self.parsed_data["distribution"] = " + ".join(distribution)
        single_letter_distribution: List[str] = []
        for stat in distribution:
            if len(stat) >= 5:
                if stat[2] == "C" or stat[2] == "H" or stat[2] == "M" or stat[2] == "V":
                    single_letter_distribution.append(stat[2])
                elif stat[3] == "C" or stat[3] == "H" or stat[3] == "M" or stat[3] == "V":
                    single_letter_distribution.append(stat[3])
                elif stat[4] == "C" or stat[4] == "H" or stat[4] == "M" or stat[4] == "V":
                    single_letter_distribution.append(stat[4])
                else:
                    single_letter_distribution.append("")
        if self.parsed_data[self.GEAR_SLOT] in ["One-Hand", "Wand", "Two-Hand", "Ranged", "Offhand",
                                             "Held In Off-hand", "Off Hand", "Trinket"]:
            self.parsed_data[self.STATS] = self.parsed_data[self.MAINSTAT] #Write mainstat type instead
        else:
            self.parsed_data[self.STATS] = ">".join(single_letter_distribution)

    def extract_sell_price(self) -> str:
        """Extract and format item sell price."""
        gold: Optional[str] = self.extract_content(r'<span class="moneygold">(\d+)</span>')
        silver: Optional[str] = self.extract_content(r'<span class="moneysilver">(\d+)</span>')
        copper: Optional[str] = self.extract_content(r'<span class="moneycopper">(\d+)</span>')
        return f"{gold or 0} gold, {silver or 0} silver, {copper or 0} copper"

    def extract_spec_ids(self) -> List[int]:
        """Extract spec IDs from the HTML content."""
        spec_ids = []
        pattern = r'<div class="iconsmall spec(\d+)"'
        matches = re.findall(pattern, self.html_string)
        for match in matches:
            spec_ids.append(int(match))
        if len(spec_ids) == 0:
            return WowSpec.get_all_spec_ids()
        return spec_ids

    def extract_spec_names(self) -> List[str]:
        """Extract spec names from the parsed spec IDs"""
        spec_names: List[str] = []
        spec_ids = self.extract_spec_ids()
        for spec_id in spec_ids:
            spec_names.append(WowSpec.get_abbr_from_id(spec_id))
        return spec_names

    def convert_to_json_and_save_to_disk(self) -> None:
        """Convert parsed data to JSON and save to disk."""
        if len(self.html_string) == 0:
            print(f"Warning: Item {self.item_id} has empty html during json write...")
        json_str = json.dumps(self.parsed_data, indent=4)
        path = WowheadItem.json_folder / f"{self.item_id}.json"
        ScrapeUtils.Persistence.write_textfile(path, json_str)

    def add_statistic_dungeon_name(self) -> None:
        boss_name = self.parsed_data[self.DROPPED_BY]
        dungeon_name = WowheadZone.get_boss_zone_name(boss_name)
        self.parsed_data[self.DROPPED_IN] = dungeon_name
        dungeon_short_name = WowheadZone.get_shortened_boss_zone_name(boss_name)
        self.parsed_data[self.FROM] = dungeon_short_name

    def add_statistic_boss_position(self) -> None:
        boss_name = self.parsed_data[self.DROPPED_BY]
        position = WowheadZone.get_boss_position(boss_name)
        self.parsed_data[self.BOSS_POSITION] = position

    def add_statistic_item_drop_chance_per_spec(self) -> None:
        spec_ids = WowSpec.get_all_spec_ids()
        for spec_id in spec_ids:
            items = WowheadItem.get_all_items_for_spec(spec_id)
            boss_loot_table_size = 0
            for item in items:
                if spec_id in self.parsed_data[self.SPEC_IDS]:
                    if item.parsed_data[self.DROPPED_BY] == self.parsed_data[self.DROPPED_BY]:
                        if item.parsed_data[self.GEAR_SLOT] is not None: #Ignore mounts/quest items
                            boss_loot_table_size += 1
            drop_chance = f"{0}%"
            if not boss_loot_table_size == 0:
                drop_chance = f"{100 // boss_loot_table_size}%"
            column_name = WowSpec.get_abbr_from_id(spec_id)
            self.parsed_data[column_name] = drop_chance

    @staticmethod
    def sim_world_tour() -> None:
        for wow_class in WowClass.get_all():
            loot_chance = 0.2  # Chance of loot per player per boss
            class_drop_rates: Dict[str, Dict[str, str]] = {}
            for loot_category in WowLootCategory.get_all():
                if loot_category.get_mainstat() is not None:
                    matching_spec_found = False
                    for spec_id in WowSpec.get_all_spec_ids_for_class(wow_class):
                        spec = WowSpec.get_spec_from_id(spec_id)
                        if loot_category.get_mainstat() == spec.get_mainstat():
                            matching_spec_found = True
                    if not matching_spec_found:
                        continue
                if loot_category.get_role() is not None:
                    matching_spec_found = False
                    for spec_id in WowSpec.get_all_spec_ids_for_class(wow_class):
                        spec = WowSpec.get_spec_from_id(spec_id)
                        if loot_category.get_role() == spec.get_role():
                            matching_spec_found = True
                    if not matching_spec_found:
                        continue
                loot_category.get_mainstat()
                slot = loot_category.get_equip_slot()
                spec_drop_rates: Dict[str, str] = {}
                best_chance = 0
                for spec_id in WowSpec.get_all_spec_ids_for_class(wow_class):
                    abbr_name = WowSpec.get_abbr_from_id(spec_id)
                    chance_of_no_drops = 1.0
                    items_considered = 0
                    for item in list(WowheadItem.get_all_items_for_spec(spec_id)):
                        matching_slot = item.parsed_data[WowheadItem.GEAR_SLOT] == slot.get_ingame_name()
                        matching_mainstat = loot_category.get_mainstat() is None or item.has_mainstat(loot_category.get_mainstat())
                        matching_role = loot_category.get_role() is None or item.drops_for_role(loot_category.get_role())
                        if matching_slot and matching_mainstat and matching_role:
                            drop_chance = item.parsed_data[abbr_name].rstrip('%')
                            try:
                                drop_chance_float = float(drop_chance) / 100
                            except ValueError:
                                print(f"Warning: drop chance {drop_chance} is not numeric")
                                continue
                            chance_item_not_dropping = 1 - (loot_chance * drop_chance_float)
                            if drop_chance_float > 0:
                                chance_of_no_drops *= chance_item_not_dropping
                                items_considered += 1
                    chance_of_at_least_one = (1 - chance_of_no_drops) * 100
                    best_chance = max(best_chance, chance_of_at_least_one)

                    spec_drop_rates[abbr_name] = f"{chance_of_at_least_one:.0f}% ({items_considered} items)"
                spec_drop_rates[wow_class.get_abbr()] = f"{best_chance:.0f}% ({items_considered} items)"
                class_drop_rates[loot_category.get_abbr()] = spec_drop_rates

            json_str = json.dumps(class_drop_rates, indent=4)
            folder: Path = Path.cwd() / "wow_drop_chances"
            path = folder / f"{wow_class.get_abbr()}.json"
            ScrapeUtils.Persistence.write_textfile(path, json_str)

    @staticmethod
    def scrape_wowhead_item(item_id: int) -> None:
        """Scrape item data from Wowhead and save it."""
        WowheadItem._set_trimmer_ruleset_for_wowhead_items()
        url = f"https://www.wowhead.com/item={item_id}"
        html_content = ScrapeUtils.Html.fetch_url(url)

        if len(html_content) == 0:
            print(f"Warning: html_content is Empty for zone_id {item_id}")
        wowhead_item = WowheadItem(item_id, html_content)
        WowheadItem.register_instance(item_id, wowhead_item)

    def is_mount_or_quest_item(self) -> bool:
        return self.parsed_data[self.GEAR_SLOT] == "" or self.parsed_data[self.GEAR_SLOT] is None

    def has_mainstat(self, mainstat: WowStatPrimary) -> bool:
        return mainstat.get_ingame_name() in self.parsed_data[WowheadItem.PRIMARY_STATS]

    def drops_for_mainstat(self, mainstat: WowStatPrimary) -> bool:
        specs_within_mainstat = WowSpec.get_all_spec_ids_for_mainstat(mainstat)
        for spec_id in specs_within_mainstat:
            spec = WowSpec.get_spec_from_id(spec_id)
            drop_chance = self.parsed_data[spec.get_abbr()].rstrip('%')
            if drop_chance == 0 or drop_chance == "0":
                return False
        return True

    def drops_for_role(self, role: WowRole) -> bool:
        specs_within_role = WowSpec.get_all_spec_ids_for_role(role)
        for spec_id in specs_within_role:
            spec = WowSpec.get_spec_from_id(spec_id)
            drop_chance = self.parsed_data[spec.get_abbr()].rstrip('%')
            if drop_chance == 0 or drop_chance == "0":
                return False
        return True

    @staticmethod
    def _set_trimmer_ruleset_for_wowhead_items() -> None:
        """In ScrapeUtils.Trimmer, register trimming ruleset for wowhead.com/item"""
        target_url = "wowhead.com/item="
        html_start = '<h1 class="heading-size-1">'
        html_end = '<h2 class="heading-size-2 clear">Related</h2></div>'
        ScrapeUtils.Trimmer.register_trimming_ruleset(target_url, html_start, html_end)


class WowheadItemCsvExporter:

    @staticmethod
    def create_fixed_size_csv() -> None:
        """
        Create a fixed-size CSV file containing all class and slot combinations.
        Each combination is represented by a fixed-length row section in the CSV.
        """
        nested_csv_tables: Dict[str, List[WowheadItem]] = {}
        for wow_class in WowClass.get_all():
            for slot_category in WowEquipSlot.get_all_ingame_names():
                items: List[WowheadItem] = []
                key = f"{wow_class.get_abbr()} {slot_category}"
                for spec_id in WowSpec.get_all_spec_ids_for_class(wow_class):
                    items.extend(list(WowheadItem.get_all_items_for_spec_and_slot(int(spec_id), slot_category)))

                # Sort items and ensure exactly a fixed_length number of items
                items = WowheadItemCsvExporter._sort_items(set(items))
                rows_for_slot = WowheadItemCsvExporter._decide_number_of_rows_in_fixed_csv(slot_category)
                if len(items) > rows_for_slot:
                    print(f"Warning: More than {rows_for_slot} items for {key}. Truncating to {rows_for_slot}.")
                    items = items[:rows_for_slot]
                elif len(items) < rows_for_slot:
                    empty_item = WowheadItem(-1, "")  # Create an empty item
                    empty_item.parsed_data = {key: "" for key in WowheadItemCsvExporter._sort_column_order(items)}
                    items.extend([empty_item] * (rows_for_slot - len(items)))

                nested_csv_tables[key] = items

        # Prepare CSV content
        csv_content = StringIO()
        writer = None

        for key, items in nested_csv_tables.items():
            if writer is None:
                columns = ['category'] + WowheadItemCsvExporter._sort_column_order(items)
                writer = csv.DictWriter(csv_content, fieldnames=columns, lineterminator='\n')
                writer.writeheader()

            i = 0
            for item in items:
                i += 1
                row_data = {'category': f"{key} #{i}"}
                row_data.update({col: item.parsed_data.get(col, '') for col in columns if col != 'category'})
                for col, value in row_data.items():
                    if isinstance(value, list):
                        row_data[col] = ', '.join(map(str, value))
                writer.writerow(row_data)

        # Save CSV file
        spreadsheet_csv_path = WowheadItem.csv_folder / "all_class_slots.csv"
        ScrapeUtils.Persistence.write_textfile(spreadsheet_csv_path, csv_content.getvalue())

    @staticmethod
    def export_items_to_csv_for_all_specs_and_classes() -> None:
        all_spec_ids = WowSpec.get_all_spec_ids()
        for wow_class in WowClass.get_all():
            class_spec_ids = WowSpec.get_all_spec_ids_for_class(wow_class)
            for spec_id in class_spec_ids:
                file_name = f"{WowSpec.get_abbr_from_id(spec_id)}.csv"
                csv_path = WowheadItem.csv_folder / file_name
                WowheadItemCsvExporter._export_items_to_csv([spec_id], csv_path)
            wow_class_csv_path = WowheadItem.csv_folder / f"{wow_class.name.replace(' ', '')}.csv"
            WowheadItemCsvExporter._export_items_to_csv(class_spec_ids, wow_class_csv_path)
        all_specs_csv_path = WowheadItem.csv_folder / "all_items.csv"
        WowheadItemCsvExporter._export_items_to_csv(all_spec_ids, all_specs_csv_path)

    @staticmethod
    def _export_items_to_csv(spec_ids: List[int], csv_path: Path) -> None:
        items = set()
        for spec_id in spec_ids:
            items.update(WowheadItem.get_all_items_for_spec(spec_id))
        if not items:
            print(f"Warning: No items found for csv {csv_path}. Creating CSV anyway...")
        # Filter out mounts and quest items
        sorted_items = WowheadItemCsvExporter._sort_items(items)
        columns = WowheadItemCsvExporter._sort_column_order(sorted_items)
        csv_content = StringIO()
        writer = csv.DictWriter(csv_content, fieldnames=columns, lineterminator='\n')
        writer.writeheader()
        for item in sorted_items:  # Write data for each item
            # Ensure all fields are present, use empty string for missing fields
            row_data = {key: item.parsed_data.get(key, '') for key in columns}
            for key, value in row_data.items():
                if isinstance(value, list):  # Convert lists to strings for CSV compatibility
                    row_data[key] = ', '.join(map(str, value))
            writer.writerow(row_data)
        ScrapeUtils.Persistence.write_textfile(csv_path, csv_content.getvalue())

    @staticmethod
    def _decide_number_of_rows_in_fixed_csv(slot_category: str) -> int:
        if slot_category != 0:
            return 24

    @staticmethod
    def _sort_items(sorted_item_list: Set['WowheadItem']) -> List['WowheadItem']:
        return sorted(
            list(sorted_item_list),
            key=lambda x: (
                x.parsed_data.get(WowheadItem.GEAR_SLOT) or '',  # sort by slot #1 prio
                x.parsed_data.get(WowheadItem.GEAR_TYPE) or '',  # sort by type #2 prio
                x.parsed_data.get(WowheadItem.DROPPED_IN) or '',
                x.parsed_data.get(WowheadItem.BOSS_POSITION) or '',
                x.parsed_data.get(WowheadItem.ITEM_ID) or ''  # Finally sort by id to avoid random row order
            )
        )

    @staticmethod
    def _sort_column_order(item_list: List['WowheadItem']) -> List[str]:
        columns: List[str] = []  # Create the fieldnames list with the desired order
        first_columns: List[str] = [WowheadItem.ITEM_ID, WowheadItem.FROM, WowheadItem.DROPPED_BY,
                                    WowheadItem.BOSS_POSITION, WowheadItem.GEAR_SLOT, WowheadItem.GEAR_TYPE,
                                    WowheadItem.NAME, WowheadItem.DISTRIBUTION, WowheadItem.STATS, WowheadItem.MAINSTAT,
                                    "DkBlood", "DkFrost", "DkUnholy"]
        last_columns: List[str] = [WowheadItem.SPEC_IDS, WowheadItem.SPEC_NAMES]
        columns.extend(first_columns)
        all_keys: Set[str] = set()  # Get all unique keys from all items
        for item in item_list:
            all_keys.update(item.parsed_data.keys())
        middle_columns = sorted(list(all_keys - set(first_columns) - set(last_columns)))
        columns.extend(middle_columns)
        columns.extend(last_columns)
        return columns


class WowheadZone:
    """Represents a WoW zone with data scraped from Wowhead."""

    # Constants for parsed data keys
    ZONE_ID = 'zone_id'
    NAME = 'name'
    BOSSES = 'bosses'
    ITEM_IDS = 'item_ids'
    BOSS_ORDER = 'boss_order'
    BOSS_HREFS = 'boss_hrefs'

    # Constants for boss data keys
    NPC_ID = 'npc_id'
    HREF_NAME = 'href_name'
    DISPLAY_NAME = 'display_name'

    folder: Path = Path.cwd() / "wowhead_zones"
    instances: Dict[int, 'WowheadZone'] = {}

    def __init__(self, zone_id: int, html_string: str):
        """Initialize WowheadItem with item ID and HTML content."""
        self.zone_id: int = zone_id
        self.html_string: str = html_string
        self.parsed_data: Dict[str, Any] = {}
        self.parse(zone_id)
        WowheadZone.instances[zone_id] = self

    @staticmethod
    def register_instance(zone_id: int, instance: 'WowheadZone') -> None:
        WowheadZone.instances[zone_id] = instance

    @staticmethod
    def get_all_item_ids() -> List[int]:
        """
        Goes over each instance in the class variable 'instances' and returns a list of
        each item_id found in parsed_data['item_ids']
        """
        all_item_ids = []
        for instance in WowheadZone.instances.values():
            all_item_ids.extend(instance.parsed_data[WowheadZone.ITEM_IDS])
        return list(set(all_item_ids))  # Remove duplicates and return as list

    @staticmethod
    def get_boss_zone_name(boss_name: str) -> str:
        href_boss_name = WowheadZone.convert_boss_name_to_href_name(boss_name)
        if boss_name is not None:
            for zone in WowheadZone.instances.values():
                boss_order = zone.parsed_data[WowheadZone.BOSS_ORDER]
                for boss in boss_order:
                    if boss.lower() == boss_name.lower():
                        return zone.parsed_data[WowheadZone.NAME]
                # Try alternative href names
                boss_hrefs = zone.parsed_data[WowheadZone.BOSS_HREFS]
                for href in boss_hrefs:
                    if href_boss_name == href:
                        return zone.parsed_data[WowheadZone.NAME]
        return "UNKNOWN"

    @staticmethod
    def get_shortened_boss_zone_name(boss_name: str) -> str:
        name_length_limit = 16
        boss_zone_name = WowheadZone.get_boss_zone_name(boss_name)
        if boss_zone_name.startswith("The "):
            boss_zone_name = boss_zone_name[4:]
        if len(boss_zone_name) > name_length_limit and "," in boss_zone_name:
            boss_zone_name = boss_zone_name.split(",")[0]
        if len(boss_zone_name) <= name_length_limit:
            return boss_zone_name
        words = boss_zone_name.split()
        while len(' '.join(words)) > name_length_limit and len(words) > 1:
            words.pop()
        while len(words) > 1 and not words[-1].istitle():
            words.pop()
        shortened_name = ' '.join(words)
        return shortened_name

    @staticmethod
    def get_boss_position(boss_name: str) -> str:
        href_boss_name = WowheadZone.convert_boss_name_to_href_name(boss_name)
        if boss_name is not None:
            for zone in WowheadZone.instances.values():
                boss_order = zone.parsed_data[WowheadZone.BOSS_ORDER]
                for index, boss in enumerate(boss_order):
                    if boss.lower() == boss_name.lower():
                        return f"{index + 1} of {len(boss_order)}"
                # Try alternative href names
                boss_hrefs = zone.parsed_data[WowheadZone.BOSS_HREFS]
                for index, href in enumerate(boss_hrefs):
                    if href_boss_name == href:
                        return f"{index + 1} of {len(boss_hrefs)}"
            return "? of ?"

    def parse(self, zone_id: int) -> None:
        """Parse HTML content to extract item IDs."""
        self.parsed_data[self.ZONE_ID] = zone_id
        self.parsed_data[self.NAME] = self.extract_name()
        self.parsed_data[self.BOSSES] = self.extract_bosses()
        self.parsed_data[self.ITEM_IDS] = self.extract_item_ids()
        boss_order = [boss[self.DISPLAY_NAME] for boss in self.parsed_data[self.BOSSES].values()]
        self.parsed_data[self.BOSS_ORDER] = boss_order
        boss_href_name = [boss[self.HREF_NAME] for boss in self.parsed_data[self.BOSSES].values()]
        self.parsed_data[self.BOSS_HREFS] = boss_href_name

    def extract_name(self) -> str:
        pattern = r'var myMapper = new Mapper\({"parent":"[^"]+","zone":\d+,"name":"([^"]+)"\}\);'
        match = re.search(pattern, self.html_string)
        return match.group(1) if match else "Unknown"

    def extract_bosses(self) -> Dict[str, Dict[str, str]]:
        """Parse HTML content to extract bosses"""
        boss_data: Dict[str, Dict[str, str]] = {}
        # Find all <li> elements containing boss information
        li_elements = re.findall(r'<li><div><a[^>]*>.*?</a>.*?</div></li>', self.html_string, re.DOTALL)

        for li in li_elements:
            # Extract npc_id, href_name, and display_name
            npc_match = re.search(r'href="/npc=(\d+)/([^"]+)"', li)
            name_match = re.search(r'<a[^>]*>([^<]+)</a>', li)
            if npc_match:
                npc_id = int(npc_match.group(1))
                href_name = npc_match.group(2)
            else:
                npc_id = -1
                href_name = "UNKNOWN"

            display_name = name_match.group(1) if name_match else None
            if href_name == "UNKNOWN":
                if isinstance(display_name, str):
                    href_name = WowheadZone.convert_boss_name_to_href_name(display_name)
            if display_name:
                boss_data[display_name] = {
                    self.NPC_ID: str(npc_id),
                    self.HREF_NAME: href_name,
                    self.DISPLAY_NAME: display_name
                }
        return boss_data

    def extract_item_ids(self) -> List[int]:
        """Parse HTML content to extract item IDs."""
        # Extract item IDs from the WH.Gatherer.addData section
        gatherer_data_pattern = r'WH\.Gatherer\.addData\(3, 1, ({.*?})\);'
        gatherer_data_match = re.search(gatherer_data_pattern, self.html_string, re.DOTALL)

        if gatherer_data_match:
            gatherer_data_str = gatherer_data_match.group(1)
            item_id_pattern = r'"(\d+)":\s*{'
            return re.findall(item_id_pattern, gatherer_data_str)
        return []

    def convert_to_json_and_save_to_disk(self) -> None:
        """Convert parsed data to JSON and save to disk."""
        if len(self.html_string) == 0:
            print(f"Warning: Item {self.zone_id} has empty html during json write...")
        json_str = json.dumps(self.parsed_data, indent=4)
        path = WowheadZone.folder / f"{self.zone_id}.json"
        ScrapeUtils.Persistence.write_textfile(path, json_str)

    @staticmethod
    def _set_trimmer_ruleset_for_wowhead_zone() -> None:
        """In ScrapeUtils.Trimmer, register trimming ruleset for wowhead.com/item"""
        target_url = "wowhead.com/zone="
        html_start = '<div class="text">'
        html_end = 'var tabsRelated = new Tabs'
        ScrapeUtils.Trimmer.register_trimming_ruleset(target_url, html_start, html_end)

    @staticmethod
    def scrape_wowhead_zone(zone_id: int) -> None:
        """Scrape zone data from Wowhead and save it."""
        WowheadZone._set_trimmer_ruleset_for_wowhead_zone()
        url = f"https://www.wowhead.com/zone={zone_id}"
        html_content = ScrapeUtils.Html.fetch_url(url)

        if len(html_content) == 0:
            print(f"Warning: html_content is Empty for zone_id {zone_id}")
        wowhead_zone = WowheadZone(zone_id, html_content)
        WowheadZone.register_instance(zone_id, wowhead_zone)

    @staticmethod
    def convert_boss_name_to_href_name(boss_name: Optional[str]) -> str:
        if boss_name is None:
            return "UNKNOWN"
        href_name = boss_name.lower()# Convert to lowercase
        return re.sub(r'[^a-z0-9]+', '-', href_name) #replace special chars with hyphen

class WowheadZoneList:
    """Represents a WoW zone with data scraped from Wowhead."""

    folder: Path = Path.cwd() / "wowhead_zone_list"
    instances: Dict[str, 'WowheadZoneList'] = {}

    def __init__(self, zone_list: str, html_string: str):
        """Initialize WowheadItem with item ID and HTML content."""
        self.zone_list: str = zone_list
        self.html_string: str = html_string
        self.parsed_data: Dict[str, Any] = {}
        self.parse(zone_list)
        WowheadZoneList.instances[zone_list] = self

    @staticmethod
    def register_instance(zone_list: str, instance: 'WowheadZoneList') -> None:
        WowheadZoneList.instances[zone_list] = instance

    @staticmethod
    def get_all_zone_ids() -> List[int]:
        """
        Goes over each instance in the class variable 'instances' and returns a list of
        each zone_id found in parsed_data['zones'].keys()
        """
        all_zone_ids = []
        for instance in WowheadZoneList.instances.values():
            all_zone_ids.extend(instance.parsed_data['zones'].keys())
        return list(set(all_zone_ids))  # Remove duplicates and return as list

    def parse(self, zone_list: str) -> None:
        """Parse HTML content to extract item IDs."""
        self.parsed_data['zone_list'] = zone_list
        self.parsed_data['zones'] = self.extract_zone_list()
        self.convert_to_json_and_save_to_disk()

    def extract_zone_list(self) -> Dict[int, str]:
        """Parse each zone in the zone list in the html"""
        zone_data = {}

        # Find the data array in the JavaScript
        data_match = re.search(r'data: (\[.*?\])', self.html_string, re.DOTALL)
        if data_match:
            data_str = data_match.group(1)
            try:
                # Parse the JSON data
                data = json.loads(data_str)
                for zone in data:
                    if 'id' in zone and 'name' in zone:
                        zone_data[zone['id']] = zone['name']
            except json.JSONDecodeError:
                print("Error decoding JSON data")

        return zone_data

    def convert_to_json_and_save_to_disk(self) -> None:
        """Convert parsed data to JSON and save to disk."""
        if len(self.html_string) == 0:
            print(f"Warning: Item {self.zone_list} has empty html during json write...")
        json_str = json.dumps(self.parsed_data, indent=4)
        path = WowheadZone.folder / f"{self.zone_list}.json"
        ScrapeUtils.Persistence.write_textfile(path, json_str)

    @staticmethod
    def _set_trimmer_ruleset_for_wowhead_zone_list() -> None:
        """In ScrapeUtils.Trimmer, register trimming ruleset for wowhead.com/item"""
        target_url = "wowhead.com/zones"
        html_start = '<script type="text/javascript">//'
        html_end = '//]]></script>'
        ScrapeUtils.Trimmer.register_trimming_ruleset(target_url, html_start, html_end)

    @staticmethod
    def scrape_wowhead_zone_list(zone_list: str) -> None:
        """Scrape zone data from Wowhead and save it."""
        WowheadZoneList._set_trimmer_ruleset_for_wowhead_zone_list()
        url = f"https://www.wowhead.com/zones/{zone_list}"
        html_content = ScrapeUtils.Html.fetch_url(url)

        if len(html_content) == 0:
            print(f"Warning: html_content is Empty for zone_id {zone_list}")
        wowhead_zone_list = WowheadZoneList(zone_list, html_content)
        WowheadZoneList.register_instance(zone_list, wowhead_zone_list)


class OutputValidation:

    @staticmethod
    def validate() -> None:
        test_folder: Path = Path.cwd() / "tests"
        csv_folder = WowheadItem.csv_folder
        all_class_slots_csv = "all_class_slots.csv"
        all_items_csv = "all_items.csv"
        real_out1 = ScrapeUtils.Persistence.read_textfile(csv_folder / all_class_slots_csv)
        real_out2 = ScrapeUtils.Persistence.read_textfile(csv_folder / all_items_csv)
        test_out1 = ScrapeUtils.Persistence.read_textfile(test_folder / all_class_slots_csv)
        test_out2 = ScrapeUtils.Persistence.read_textfile(test_folder / all_items_csv)
        out1_match = real_out1 == test_out1
        out2_match = real_out2 == test_out2
        if not out1_match:
            print("Warning: output1 does not match expected output!")
            OutputValidation.print_differences(real_out1, test_out1)
        elif not out2_match:
            print("Warning: output2 does not match expected output!")
            OutputValidation.print_differences(real_out2, test_out2)
        else:
            print("Validation was passed.")

    @staticmethod
    def print_differences(actual: str, expected: str) -> None:
        expected_lines = expected.splitlines()
        actual_lines = actual.splitlines()
        for i, (expected_line, actual_line) in enumerate(zip(expected_lines, actual_lines), start=1):
            if expected_line != actual_line:
                print(f"Line {i} differs:")
                print(f"Expected: {expected_line}")
                print(f"Actual:   {actual_line}")
                break
        if len(expected_lines) != len(actual_lines):
            print("File lengths differ.")
            print(f"Expected file length: {len(expected_lines)} lines.")
            print(f"Actual file length: {len(actual_lines)} lines.")

class MainWowheadPipeline:

    @staticmethod
    def main() -> None:
        print("Starting code execution...")
        my_zone_list = "war-within/dungeons"
        WowheadZoneList.scrape_wowhead_zone_list(my_zone_list)
        every_zone_ids = WowheadZoneList.get_all_zone_ids()
        for my_zone in every_zone_ids:
            WowheadZone.scrape_wowhead_zone(my_zone)

        every_item_ids = WowheadZone.get_all_item_ids()
        for my_index, my_item in enumerate(every_item_ids):
            print(f"Scraping {my_item} ({my_index+1} of {len(every_item_ids)})")
            WowheadItem.scrape_wowhead_item(my_item)

        print("Creating item jsons...")
        WowheadItem.parse_statistics_across_all_items_and_write_json()

        print("Building csv files...")
        WowheadItemCsvExporter.export_items_to_csv_for_all_specs_and_classes()
        WowheadItemCsvExporter.create_fixed_size_csv()

        WowheadItem.sim_world_tour()

        OutputValidation.validate()
        print("Finished!")


if __name__ == "__main__":
    MainWowheadPipeline.main()