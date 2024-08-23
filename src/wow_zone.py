from pathlib import Path
from typing import List

from src.wow_npc import WowNpc
from src.wow_item import WowItem
from src.wow_zone_scraper import WowZoneScraper

class WowZone:
    """Represents a WoW Npc (or boss) with data scraped from Wowhead."""

    folder: Path = Path.cwd() / "output" / "wowhead_zones"

    def __init__(self, zone_id: int):
        """Initialize WowZone by scraping data via WowZoneScraper"""
        self.zone_id = zone_id
        scraper = WowZoneScraper.scrape_wowhead_zone(zone_id)
        scraper.print_extracted_info()
        self.zone_name = scraper.zone_name
        self.shortened_zone_name = WowZone.shorten_zone_name(scraper.zone_name)
        self.bosses: List[WowNpc] = scraper.bosses
        self.wow_items: List[WowItem] = []
        for item_id in scraper.item_ids:
            wow_item = WowItem(item_id)
            wow_item.add_zone_data_to_item(self.zone_name, self.shortened_zone_name, self.bosses)
            self.wow_items.append(wow_item)
        self.item_ids = scraper.item_ids

    def get_all_wow_items(self) -> List[WowItem]:
        """Get the item_id for each WowItem in this zone """
        all_item_ids = []
        for wow_item in self.wow_items:
            all_item_ids.append(wow_item)
        return list(set(all_item_ids))

    def get_boss_position(self, boss_name: str) -> str:
        return WowNpc.get_boss_position(boss_name, self.bosses)

    @staticmethod
    def shorten_zone_name(zone_name: str) -> str:
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