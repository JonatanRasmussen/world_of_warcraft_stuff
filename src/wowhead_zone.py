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

class WowheadZone:
    UNKNOWN_VALUE = "UNKNOWN"
    def __init__(self, zone_id: int, html_string: str):
        self.zone_id = zone_id
        self.html_string = html_string
        self.parsed_data: Dict[str, Any] = {}
        self.parse()

    @staticmethod
    def convert_boss_name_to_href_name(boss_name: Optional[str]) -> str:
        if boss_name is None:
            return WowheadZone.UNKNOWN_VALUE
        href_name = boss_name.lower()
        return re.sub(r'[^a-z0-9]+', '-', href_name)

    def parse(self) -> None:
        self.parsed_data[ZoneConst.ZONE_ID] = self.zone_id
        self.parsed_data[ZoneConst.NAME] = self.extract_name()
        self.parsed_data[ZoneConst.BOSSES] = self.extract_bosses()
        self.parsed_data[ZoneConst.ITEM_IDS] = self.extract_item_ids()
        boss_order = [boss[ZoneConst.DISPLAY_NAME] for boss in self.parsed_data[ZoneConst.BOSSES].values()]
        self.parsed_data[ZoneConst.BOSS_ORDER] = boss_order
        boss_href_name = [boss[ZoneConst.HREF_NAME] for boss in self.parsed_data[ZoneConst.BOSSES].values()]
        self.parsed_data[ZoneConst.BOSS_HREFS] = boss_href_name

    def extract_name(self) -> str:
        pattern = r'var myMapper = new Mapper\({"parent":"[^"]+","zone":\d+,"name":"([^"]+)"\}\);'
        match = re.search(pattern, self.html_string)
        return match.group(1) if match else WowheadZone.UNKNOWN_VALUE

    def extract_bosses(self) -> Dict[str, Dict[str, str]]:
        boss_data: Dict[str, Dict[str, str]] = {}
        li_elements = re.findall(r'<li><div><a[^>]*>.*?</a>.*?</div></li>', self.html_string, re.DOTALL)

        for li in li_elements:
            npc_match = re.search(r'href="/npc=(\d+)/([^"]+)"', li)
            name_match = re.search(r'<a[^>]*>([^<]+)</a>', li)
            if npc_match:
                npc_id = int(npc_match.group(1))
                href_name = npc_match.group(2)
            else:
                npc_id = -1
                href_name = WowheadZone.UNKNOWN_VALUE

            display_name = name_match.group(1) if name_match else None
            if href_name == WowheadZone.UNKNOWN_VALUE and isinstance(display_name, str):
                href_name = WowheadZone.convert_boss_name_to_href_name(display_name)
            if display_name:
                boss_data[display_name] = {
                    ZoneConst.NPC_ID: str(npc_id),
                    ZoneConst.HREF_NAME: href_name,
                    ZoneConst.DISPLAY_NAME: display_name
                }
        return boss_data

    def extract_item_ids(self) -> List[int]:
        gatherer_data_pattern = r'WH\.Gatherer\.addData\(3, 1, ({.*?})\);'
        gatherer_data_match = re.search(gatherer_data_pattern, self.html_string, re.DOTALL)

        if gatherer_data_match:
            gatherer_data_str = gatherer_data_match.group(1)
            item_id_pattern = r'"(\d+)":\s*{'
            return [int(item_id) for item_id in re.findall(item_id_pattern, gatherer_data_str)]
        return []
