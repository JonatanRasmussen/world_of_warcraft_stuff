import re
from typing import Dict, List, Set, Optional

from src.wow_consts.wow_loot_category import WowLootCategory
from src.wow_consts.wow_equip_slot import WowEquipSlot
from src.wow_consts.wow_role import WowRole
from src.wow_consts.wow_spec import WowSpec
from src.wow_consts.wow_stat_primary import WowStatPrimary
from src.wow_consts.wow_stat_secondary import WowStatSecondary
from scrape_utils import ScrapeUtils

class WowItemScraper:
    """Scrapes data from Wowhead for specified WowZone"""

    UNKNOWN_VALUE = ""
    VALID_ONLY_FOR_TANK_SPECS = "Valid only for tank specializations."

    def __init__(self, item_id: int, html_string: str):
        """Scrape wowhead data for zone_id"""
        self.item_id = item_id
        self.html_string = html_string
        self.name = self.extract_name()
        self.item_level = self.extract_item_level()
        self.bind = self.extract_bind()
        self.gear_slot = self.extract_gear_slot()
        self.gear_type = self.extract_gear_type()
        self.unique = self.extract_unique()
        self.primary_stats = self.extract_primary_stats()
        self.secondary_stats = self.extract_secondary_stats()
        self.required_level = self.extract_required_level()
        self.sell_price = self.extract_sell_price()
        self.dropped_by = self.extract_dropped_by()
        self.spec_ids = self.extract_spec_ids()
        self.spec_names = self.extract_spec_names(self.spec_ids)
        self.mainstat = self.extract_mainstat()
        self.distribution = self.extract_distribution()
        self.stats = self.extract_stats()
        self.check_if_trinket_is_valid_only_for_tanks()

    @classmethod
    def create_empty(cls, item_id: int) -> 'WowItemScraper':
        empty_html = ""
        return WowItemScraper(item_id, empty_html)

    @staticmethod
    def scrape_wowhead_item(item_id: int) -> 'WowItemScraper':
        """Scrape zone data from Wowhead and save it."""
        WowItemScraper._set_trimmer_ruleset_for_wowhead_item()
        url = f"https://www.wowhead.com/item={item_id}"
        html_content = ScrapeUtils.Html.fetch_url(url)
        if len(html_content) == 0:
            print(f"Warning: html_content is Empty for item_id {item_id}")
        return WowItemScraper(item_id, html_content)

    @staticmethod
    def _set_trimmer_ruleset_for_wowhead_item() -> None:
        """In ScrapeUtils.Trimmer, register trimming ruleset for wowhead.com/item"""
        target_url = "wowhead.com/item="
        html_start = '<h1 class="heading-size-1">'
        html_end = '<h2 class="heading-size-2 clear">Related</h2></div>'
        ScrapeUtils.Trimmer.register_trimming_ruleset(target_url, html_start, html_end)

    def check_if_trinket_is_valid_only_for_tanks(self) -> None:
        if WowItemScraper.VALID_ONLY_FOR_TANK_SPECS not in self.html_string:
            if self.gear_slot == WowEquipSlot.TRINKET.get_ingame_name():
                self.gear_type = WowLootCategory.get_trinket_gear_type()
        else:
            self.spec_ids = WowSpec.get_all_spec_ids_for_role(WowRole.TANK)
            self.spec_names = WowItemScraper.extract_spec_names(self.spec_ids)
            self.gear_type = WowLootCategory.get_trinket_gear_type(WowRole.TANK)
            self.stats = WowLootCategory.get_trinket_category(self.gear_type, self.stats)
            if self.gear_slot != WowEquipSlot.TRINKET.get_ingame_name():
                print("Warning: 'Only valid for tanks' was found in a non-Trinket description.")

    def extract_content(self, pattern: str) -> str:
        match = re.search(pattern, self.html_string)
        return match.group(1) if match else WowItemScraper.UNKNOWN_VALUE

    def extract_name(self) -> str:
        return self.extract_content(r'<h1 class="heading-size-1">(.*?)</h1>')

    def extract_item_level(self) -> int:
        item_level = self.extract_content(r'Item Level <!--ilvl-->(\d+)')
        return int(item_level) if item_level else 0

    def extract_bind(self) -> str:
        return "Soulbound" if "Binds when picked up" in self.html_string else "BoE"

    def extract_gear_slot(self) -> str:
        return self.extract_content(r'<table width="100%"><tr><td>(.*?)</td>')

    def extract_gear_type(self) -> str:
        pattern = r'<table width="100%"><tr><td>[^<]+</td><th><!--scstart\d+:\d+--><span class="q1">([^<]+)</span><!--scend--></th></tr></table>'
        return self.extract_content(pattern)

    def extract_unique(self) -> bool:
        return "Unique-Equipped" in self.html_string

    def extract_primary_stats(self) -> Dict[str, int]:
        stats = {}
        for stat_enum in WowStatPrimary.get_all():
            stat = stat_enum.get_ingame_name()
            pattern = rf'\+([0-9,]+) \[?([^\]]*{stat}[^\]]*)\]?'
            value = self.extract_content(pattern)
            if value:
                stats[stat] = int(value.replace(',', ''))
        return stats

    def extract_secondary_stats(self) -> Dict[str, int]:
        stats = {}
        for stat in WowStatSecondary.get_all_ingame_names():
            value = self.extract_content(rf'([0-9,]+) {stat}')
            if value and value.isnumeric():
                stats[stat] = int(value.replace(',', ''))
        return stats

    def extract_required_level(self) -> int:
        level = self.extract_content(r'Requires Level <!--rlvl-->(\d+)')
        return int(level) if level else 0

    def extract_sell_price(self) -> str:
        gold = self.extract_content(r'<span class="moneygold">(\d+)</span>')
        silver = self.extract_content(r'<span class="moneysilver">(\d+)</span>')
        copper = self.extract_content(r'<span class="moneycopper">(\d+)</span>')
        return f"{gold or 0} gold, {silver or 0} silver, {copper or 0} copper"

    def extract_dropped_by(self) -> str:
        return self.extract_content(r'Dropped by: (.*?)</div>')

    def extract_spec_ids(self) -> List[int]:
        spec_ids = []
        pattern = r'<div class="iconsmall spec(\d+)"'
        matches = re.findall(pattern, self.html_string)
        for match in matches:
            spec_ids.append(int(match))
        return spec_ids if spec_ids else WowSpec.get_all_spec_ids()

    @staticmethod
    def extract_spec_names(spec_ids: List[int]) -> List[str]:
        return [WowSpec.get_abbr_from_id(spec_id) for spec_id in spec_ids]

    def extract_mainstat(self) -> str:
        primary_stats = self.primary_stats.keys()
        all_stats = {WowStatPrimary.AGI.get_ingame_name(), WowStatPrimary.STR.get_ingame_name(), WowStatPrimary.INT.get_ingame_name()}
        if primary_stats == all_stats:
            return "All3"
        stats_found: List[str] = []
        for stat in primary_stats:
            wow_stat = WowStatPrimary.get_from_ingame_name(stat)
            if wow_stat is not None:
                stats_found.append(wow_stat.get_abbr())
        return ",".join(stats_found)

    def extract_distribution(self) -> str:
        total_stats = sum(self.secondary_stats.values())
        distribution = []
        for stat, value in self.secondary_stats.items():
            percent = f"{100 * value // total_stats}%"
            distribution.append(f"{percent} {stat}")
        distribution.sort(reverse=True)
        return " + ".join(distribution)

    def extract_stats(self) -> str:
        equip_slot = WowEquipSlot.get_from_ingame_name(self.gear_slot)
        if equip_slot in [WowEquipSlot.ONEHAND, WowEquipSlot.TWOHAND, WowEquipSlot.RANGED,
                          WowEquipSlot.OFFHAND, WowEquipSlot.SHIELD, WowEquipSlot.TRINKET]:
            return self.mainstat
        single_letter_distribution = []
        for stat in self.distribution.split(" + "):
            if len(stat) >= 5:
                if stat[2] in WowStatSecondary.get_first_letters():
                    single_letter_distribution.append(stat[2])
                elif stat[3] in WowStatSecondary.get_first_letters():
                    single_letter_distribution.append(stat[3])
                elif stat[4] in WowStatSecondary.get_first_letters():
                    single_letter_distribution.append(stat[4])
                else:
                    single_letter_distribution.append("")
        return ">".join(single_letter_distribution)