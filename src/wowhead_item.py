import csv
import json
import re
from io import StringIO
from pathlib import Path
from typing import Optional, Set, Dict, Any, List

from src.wow_consts.item_const import ItemConst
from src.wow_consts.wow_class import WowClass
from src.wow_consts.wow_equip_slot import WowEquipSlot
from src.wow_consts.wow_loot_category import WowLootCategory
from src.wow_consts.wow_role import WowRole
from src.wow_consts.wow_spec import WowSpec
from src.wow_consts.wow_stat_primary import WowStatPrimary
from src.wow_consts.wow_stat_secondary import WowStatSecondary
from src.wowhead_parse_helpers import WowheadParseHelper
from scrape_utils import ScrapeUtils

class WowheadItem:
    def __init__(self, item_id: int, html_string: str):
        self.item_id = item_id
        self.html_string = html_string
        self.parsed_data: Dict[str, Any] = {}
        self.parse()

    def parse(self) -> None:
        self.parsed_data[ItemConst.ITEM_ID] = self.item_id
        self.parsed_data[ItemConst.NAME] = self.extract_content(r'<h1 class="heading-size-1">(.*?)</h1>')
        self.parsed_data[ItemConst.ITEM_LEVEL] = self.extract_content(r'Item Level <!--ilvl-->(\d+)')
        self.parsed_data[ItemConst.BIND] = "Soulbound" if "Binds when picked up" in self.html_string else "BoE"
        self.parsed_data[ItemConst.GEAR_SLOT] = self.extract_content(r'<table width="100%"><tr><td>(.*?)</td>')
        self.parsed_data[ItemConst.GEAR_TYPE] = self.extract_item_subtype()
        self.parsed_data[ItemConst.UNIQUE] = "Unique-Equipped" in self.html_string
        self.parsed_data[ItemConst.PRIMARY_STATS] = self.extract_primary_stats()
        self.parsed_data[ItemConst.SECONDARY_STATS] = self.extract_secondary_stats()
        self.parsed_data[ItemConst.REQUIRED_LEVEL] = self.extract_content(r'Requires Level <!--rlvl-->(\d+)')
        self.parsed_data[ItemConst.SELL_PRICE] = self.extract_sell_price()
        self.parsed_data[ItemConst.DROPPED_BY] = self.extract_content(r'Dropped by: (.*?)</div>')
        self.parsed_data[ItemConst.SPEC_IDS] = self.extract_spec_ids()
        self.parsed_data[ItemConst.SPEC_NAMES] = self.extract_spec_names()

    def extract_content(self, pattern: str) -> Optional[str]:
        return WowheadParseHelper.extract_content(pattern, self.html_string)

    def extract_item_subtype(self) -> Optional[str]:
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
        agi_stat = WowStatPrimary.AGI.get_ingame_name()
        str_stat = WowStatPrimary.STR.get_ingame_name()
        int_stat = WowStatPrimary.INT.get_ingame_name()
        if agi_stat in stats_found and str_stat in stats_found and int_stat in stats_found:
            self.parsed_data[ItemConst.MAINSTAT] = "All3"
        else:
            stats_abbr: List[str] = []
            for stat in stats_found:
                stat_enum = WowStatPrimary.get_from_ingame_name(stat)
                if stat_enum is not None:
                    stats_abbr.append(stat_enum.get_abbr())
            self.parsed_data[ItemConst.MAINSTAT] = ",".join(stats_abbr)

    def extract_secondary_stats(self) -> Dict[str, int]:
        stats = {}
        for stat in WowStatSecondary.get_all_ingame_names():
            value = self.extract_content(rf'([0-9,]+) {stat}')
            if value and value.isnumeric():
                stats[stat] = int(value.replace(',', ''))
        self.extract_secondary_stat_distribution(stats)
        return stats

    def extract_secondary_stat_distribution(self, stat_dict: Dict[str, int]) -> None:
        total_stats = sum(stat_dict.values())
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
                if stat[2] in "CHMV":
                    single_letter_distribution.append(stat[2])
                elif stat[3] in "CHMV":
                    single_letter_distribution.append(stat[3])
                elif stat[4] in "CHMV":
                    single_letter_distribution.append(stat[4])
                else:
                    single_letter_distribution.append("")
        if self.parsed_data[ItemConst.GEAR_SLOT] in ["One-Hand", "Wand", "Two-Hand", "Ranged", "Offhand",
                                             "Held In Off-hand", "Off Hand", "Trinket"]:
            self.parsed_data[ItemConst.STATS] = self.parsed_data[ItemConst.MAINSTAT]
        else:
            self.parsed_data[ItemConst.STATS] = ">".join(single_letter_distribution)

    def extract_sell_price(self) -> str:
        gold: Optional[str] = self.extract_content(r'<span class="moneygold">(\d+)</span>')
        silver: Optional[str] = self.extract_content(r'<span class="moneysilver">(\d+)</span>')
        copper: Optional[str] = self.extract_content(r'<span class="moneycopper">(\d+)</span>')
        return f"{gold or 0} gold, {silver or 0} silver, {copper or 0} copper"

    def extract_spec_ids(self) -> List[int]:
        spec_ids = []
        pattern = r'<div class="iconsmall spec(\d+)"'
        matches = re.findall(pattern, self.html_string)
        for match in matches:
            spec_ids.append(int(match))
        if len(spec_ids) == 0:
            return WowSpec.get_all_spec_ids()
        return spec_ids

    def extract_spec_names(self) -> List[str]:
        spec_names: List[str] = []
        spec_ids = self.extract_spec_ids()
        for spec_id in spec_ids:
            spec_names.append(WowSpec.get_abbr_from_id(spec_id))
        return spec_names
