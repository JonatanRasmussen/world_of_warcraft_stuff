import csv
import json
import re
from io import StringIO
from pathlib import Path
from typing import Optional, Set, Dict, Any, List

from src.wowhead_zone import WowheadZone
from src.wow_consts.zone_const import ZoneConst
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

class WowZone:
    """Represents a WoW zone with data scraped from Wowhead."""

    folder: Path = Path.cwd() / "output" / "wowhead_zones"
    instances: Dict[int, 'WowZone'] = {}

    def __init__(self, zone_id: int, html_string: str):
        """Initialize WowZone with zone ID and HTML content."""
        self.zone_id: int = zone_id
        self.parsed_data: Dict[str, Any] = {}
        wowhead_zone = WowheadZone(zone_id, html_string)
        self.parsed_data.update(wowhead_zone.parsed_data)
        WowZone.instances[zone_id] = self

    @staticmethod
    def register_instance(zone_id: int, instance: 'WowZone') -> None:
        WowZone.instances[zone_id] = instance

    @staticmethod
    def get_all_item_ids() -> List[int]:
        all_item_ids = []
        for instance in WowZone.instances.values():
            all_item_ids.extend(instance.parsed_data[ZoneConst.ITEM_IDS])
        return list(set(all_item_ids))

    @staticmethod
    def get_boss_zone_name(boss_name: str) -> str:
        href_boss_name = WowheadZone.convert_boss_name_to_href_name(boss_name)
        if boss_name is not None:
            for zone in WowZone.instances.values():
                boss_order = zone.parsed_data[ZoneConst.BOSS_ORDER]
                for boss in boss_order:
                    if boss.lower() == boss_name.lower():
                        return zone.parsed_data[ZoneConst.NAME]
                boss_hrefs = zone.parsed_data[ZoneConst.BOSS_HREFS]
                for href in boss_hrefs:
                    if href_boss_name == href:
                        return zone.parsed_data[ZoneConst.NAME]
        return WowheadZone.UNKNOWN_VALUE

    @staticmethod
    def get_shortened_boss_zone_name(boss_name: str) -> str:
        name_length_limit = 16
        boss_zone_name = WowZone.get_boss_zone_name(boss_name)
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
            for zone in WowZone.instances.values():
                boss_order = zone.parsed_data[ZoneConst.BOSS_ORDER]
                for index, boss in enumerate(boss_order):
                    if boss.lower() == boss_name.lower():
                        return f"{index + 1} of {len(boss_order)}"
                boss_hrefs = zone.parsed_data[ZoneConst.BOSS_HREFS]
                for index, href in enumerate(boss_hrefs):
                    if href_boss_name == href:
                        return f"{index + 1} of {len(boss_hrefs)}"
        return "? of ?"

    def convert_to_json_and_save_to_disk(self) -> None:
        """Convert parsed data to JSON and save to disk."""
        json_str = json.dumps(self.parsed_data, indent=4)
        path = WowZone.folder / f"{self.zone_id}.json"
        ScrapeUtils.Persistence.write_textfile(path, json_str)

    @staticmethod
    def _set_trimmer_ruleset_for_wowhead_zone() -> None:
        """In ScrapeUtils.Trimmer, register trimming ruleset for wowhead.com/zone"""
        target_url = "wowhead.com/zone="
        html_start = '<div class="text">'
        html_end = 'var tabsRelated = new Tabs'
        ScrapeUtils.Trimmer.register_trimming_ruleset(target_url, html_start, html_end)

    @staticmethod
    def scrape_wowhead_zone(zone_id: int) -> None:
        """Scrape zone data from Wowhead and save it."""
        WowZone._set_trimmer_ruleset_for_wowhead_zone()
        url = f"https://www.wowhead.com/zone={zone_id}"
        html_content = ScrapeUtils.Html.fetch_url(url)

        if len(html_content) == 0:
            print(f"Warning: html_content is Empty for zone_id {zone_id}")
        wow_zone = WowZone(zone_id, html_content)
        WowZone.register_instance(zone_id, wow_zone)
