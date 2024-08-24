from pathlib import Path
from typing import List, Dict

from src.wow_npc import WowNpc
from src.wow_item import WowItem
from src.wow_zone_scraper import WowZoneScraper
from src.wow_zone_fixer import WowZoneFixer

class WowZone:
    """Represents a WoW Npc (or boss) with data scraped from Wowhead."""

    folder: Path = Path.cwd() / "output" / "wowhead_zones"

    def __init__(self, zone_id: int):
        """Initialize WowZone by scraping data via WowZoneScraper"""
        self.zone_id = zone_id
        scraper = WowZoneScraper.scrape_wowhead_zone(zone_id)
        self.zone_name = scraper.zone_name
        self.shortened_zone_name = WowZone.shorten_zone_name(scraper.zone_name)
        self.bosses: List[WowNpc] = scraper.bosses
        self.week: str = WowZoneFixer.get_release_week(zone_id)
        self.wow_items: List[WowItem] = []
        self.item_ids = scraper.item_ids
        self.check_if_any_hardcoded_values_exist_for_this_zone()
        self.cascade_scrape_items(self.item_ids)

    def check_if_any_hardcoded_values_exist_for_this_zone(self) -> None:
        """Check in WowZoneFixer if any hardcoded bosses or items are provided for this zone_id"""
        optional_fixed_boss_list = WowZoneFixer.try_fix_boss_list(self.zone_id)
        if optional_fixed_boss_list is not None:
            self.bosses = optional_fixed_boss_list
        optional_fixed_item_list = WowZoneFixer.try_fix_item_list(self.zone_id)
        if optional_fixed_item_list is not None:
            self.item_ids = optional_fixed_item_list

    def cascade_scrape_items(self, item_ids: List[int]) -> None:
        """Scrape and initialize wow_items for the provided item_ids"""
        self.print_extracted_info()
        self.wow_items.clear()
        for item_id in item_ids:
            wow_item = WowItem(item_id)
            wow_item.add_zone_data_to_item(self.zone_name, self.shortened_zone_name, self.week, self.bosses)
            self.wow_items.append(wow_item)

    def print_extracted_info(self) -> None:
        print(f"Info: Zone_id {self.zone_id} was parsed as {self.zone_name} "
              f"with {len(self.bosses)} bosses and "
              f"{len(self.item_ids)} items")

    def get_all_wow_items(self) -> List[WowItem]:
        """Get the item_id for each WowItem in this zone """
        all_item_ids = []
        for wow_item in self.wow_items:
            all_item_ids.append(wow_item)
        return list(set(all_item_ids))

    def get_boss_position(self, boss_name: str) -> str:
        return WowNpc.get_boss_position(boss_name, self.bosses)

    def validate_that_each_boss_has_loot(self, all_items: List[WowItem]) -> None:
        items_missing_source: List[int] = []
        missing_drop_source = "missing"
        boss_drops_count: Dict[str, int] = {missing_drop_source: 0}
        for boss in self.bosses:

            boss_drops_count[boss.display_name] = 0
        for item in all_items:
            if item.dropped_in == self.zone_name:
                boss_found = False
                for boss in self.bosses:
                    if boss.has_matching_name(item.dropped_by):
                        boss_drops_count[boss.display_name] += 1
                        boss_found = True
                if item.dropped_by == WowItem.UNKNOWN_VALUE:
                    boss_drops_count[missing_drop_source] += 1
                    items_missing_source.append(item.item_id)
                    boss_found = True
                if not boss_found:
                    print()
                    href_name = WowNpc.convert_display_name_to_href_name(item.dropped_by)
                    print(f"Warning: item {item.item_id} has {item.dropped_by} (href {href_name}) which did not map to anything.")
                    for boss in self.bosses:
                        boss.print_info()
                    print()
        all_bosses_has_drops = True
        for key, value in boss_drops_count.items():
            if value == 0 and key != missing_drop_source:
                all_bosses_has_drops = False
        if not all_bosses_has_drops and boss_drops_count[missing_drop_source] == 0:
            print(f"Warning: zone {self.zone_id} has missing loot! {boss_drops_count}")
        elif not all_bosses_has_drops and not WowZoneFixer.missing_source_is_ok(self.zone_id):
            print(f"Info: zone {self.zone_id} has loot without source: {boss_drops_count}")
            print(f"The followings items are missing: {items_missing_source}")

    @staticmethod
    def shorten_zone_name(zone_name: str) -> str:
        """Shorten a too-long zone name using verious techniques"""
        name_length_limit = 16
        if zone_name.startswith("The "):
            zone_name = zone_name[4:]
        if len(zone_name) > name_length_limit and "," in zone_name:
            zone_name = zone_name.split(",")[0]
        if len(zone_name) <= name_length_limit:
            return zone_name
        words = zone_name.split()
        while len(' '.join(words)) > name_length_limit and len(words) > 1:
            words.pop()
        while len(words) > 1 and not words[-1].istitle():
            words.pop()
        shortened_name = ' '.join(words)
        return shortened_name