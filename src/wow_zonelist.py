import csv
import json
import re
from io import StringIO
from pathlib import Path
from typing import Optional, Set, Dict, Any, List

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
from src.wowhead_zone_list import WowheadZoneList
from scrape_utils import ScrapeUtils

class WowZoneList:
    """Represents a WoW zone list with data scraped from Wowhead."""

    folder: Path = Path.cwd() / "output" / "wowhead_zone_list"
    instances: Dict[str, 'WowZoneList'] = {}

    def __init__(self, zone_list: str, html_string: str):
        """Initialize WowZoneList with zone list and HTML content."""
        self.zone_list: str = zone_list
        self.parsed_data: Dict[str, Any] = {}
        wowhead_zone_list = WowheadZoneList(zone_list, html_string)
        self.parsed_data.update(wowhead_zone_list.parsed_data)
        self.convert_to_json_and_save_to_disk()
        WowZoneList.instances[zone_list] = self

    @staticmethod
    def register_instance(zone_list: str, instance: 'WowZoneList') -> None:
        WowZoneList.instances[zone_list] = instance

    @staticmethod
    def get_all_zone_ids() -> List[int]:
        """
        Goes over each instance in the class variable 'instances' and returns a list of
        each zone_id found in parsed_data['zones'].keys()
        """
        all_zone_ids = []
        for instance in WowZoneList.instances.values():
            all_zone_ids.extend(instance.parsed_data[ZoneConst.ZONES].keys())
        return list(set(all_zone_ids))  # Remove duplicates and return as list

    def convert_to_json_and_save_to_disk(self) -> None:
        """Convert parsed data to JSON and save to disk."""
        json_str = json.dumps(self.parsed_data, indent=4)
        path = WowZoneList.folder / f"{self.zone_list}.json"
        ScrapeUtils.Persistence.write_textfile(path, json_str)

    @staticmethod
    def _set_trimmer_ruleset_for_wowhead_zone_list() -> None:
        """In ScrapeUtils.Trimmer, register trimming ruleset for wowhead.com/zones"""
        target_url = "wowhead.com/zones"
        html_start = '<script type="text/javascript">//'
        html_end = '//]]></script>'
        ScrapeUtils.Trimmer.register_trimming_ruleset(target_url, html_start, html_end)

    @staticmethod
    def scrape_wowhead_zone_list(zone_list: str) -> None:
        """Scrape zone list data from Wowhead and save it."""
        WowZoneList._set_trimmer_ruleset_for_wowhead_zone_list()
        url = f"https://www.wowhead.com/zones/{zone_list}"
        html_content = ScrapeUtils.Html.fetch_url(url)

        if len(html_content) == 0:
            print(f"Warning: html_content is Empty for zone_list {zone_list}")
        wow_zone_list = WowZoneList(zone_list, html_content)
        WowZoneList.register_instance(zone_list, wow_zone_list)
