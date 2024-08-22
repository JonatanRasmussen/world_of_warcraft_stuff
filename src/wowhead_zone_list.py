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
from scrape_utils import ScrapeUtils

class WowheadZoneList:
    def __init__(self, zone_list: str, html_string: str):
        self.zone_list = zone_list
        self.html_string = html_string
        self.parsed_data: Dict[str, Any] = {}
        self.parse()

    def parse(self) -> None:
        self.parsed_data[ZoneConst.ZONE_LIST] = self.zone_list
        self.parsed_data[ZoneConst.ZONES] = self.extract_zone_list()

    def extract_zone_list(self) -> Dict[int, str]:
        zone_data = {}
        data_match = re.search(r'data: (\[.*?\])', self.html_string, re.DOTALL)
        if data_match:
            data_str = data_match.group(1)
            try:
                data = json.loads(data_str)
                for zone in data:
                    if 'id' in zone and 'name' in zone:
                        zone_data[zone['id']] = zone['name']
            except json.JSONDecodeError:
                print("Error decoding JSON data")
        return zone_data
