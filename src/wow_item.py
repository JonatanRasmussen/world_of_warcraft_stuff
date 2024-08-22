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
from src.wowhead_item import WowheadItem
from src.wow_zone import WowZone, WowheadZone
from src.wow_zonelist import WowZoneList, WowheadZoneList
from scrape_utils import ScrapeUtils

class WowItem:
    """Represents a WoW item with data scraped from Wowhead."""

    json_folder: Path = Path.cwd() / "output" / "wowhead_items"
    csv_folder: Path = Path.cwd() / "output" / "wowhead_item_csv"
    drop_chance_folder: Path = Path.cwd() / "output" / "wow_drop_chances"
    instances: Dict[int, 'WowItem'] = {}

    def __init__(self, item_id: int, html_string: str):
        """Initialize WowItem with item ID and HTML content."""
        self.item_id: int = item_id
        self.parsed_data: Dict[str, Any] = {}
        wowhead_item = WowheadItem(item_id, html_string)
        self.parsed_data.update(wowhead_item.parsed_data)
        WowItem.instances[item_id] = self

    @staticmethod
    def register_instance(item_id: int, instance: 'WowItem') -> None:
        WowItem.instances[item_id] = instance

    @staticmethod
    def get_all_items_for_spec(spec_id: int) -> Set['WowItem']:
        items: Set['WowItem'] = set()
        for item in WowItem.instances.values():
            if not item.is_mount_or_quest_item() and item.has_known_source():
                integer_spec_ids: List[int] = []
                for scraped_spec_id in item.parsed_data[ItemConst.SPEC_IDS]:
                    if isinstance(scraped_spec_id, int):
                        integer_spec_ids.append(scraped_spec_id)
                    else:
                        print(f"{scraped_spec_id} is not an int. It is type {type(scraped_spec_id)}")
                if spec_id in integer_spec_ids:
                    items.add(item)
        return items

    @staticmethod
    def get_all_items_for_spec_and_slot(spec_id: int, slot_name: str) -> Set['WowItem']:
        items: Set['WowItem'] = set()
        for item in WowItem.get_all_items_for_spec(spec_id):
            if item.parsed_data['gear_slot'] == slot_name:
                items.add(item)
        return items

    @staticmethod
    def parse_statistics_across_all_items_and_write_json() -> None:
        # Requires all other items to have been scraped already
        for item_id in WowZone.get_all_item_ids():
            item = WowItem.instances[item_id]
            item.add_statistic_item_drop_chance_per_spec()
            item.add_statistic_dungeon_name()
            item.add_statistic_boss_position()
            item.convert_to_json_and_save_to_disk()
        # Also save zones to json
        for zone_id in WowZoneList.get_all_zone_ids():
            zone = WowZone.instances[zone_id]
            zone.convert_to_json_and_save_to_disk()

    def convert_to_json_and_save_to_disk(self) -> None:
        """Convert parsed data to JSON and save to disk."""
        json_str = json.dumps(self.parsed_data, indent=4)
        path = WowItem.json_folder / f"{self.item_id}.json"
        ScrapeUtils.Persistence.write_textfile(path, json_str)

    def add_statistic_dungeon_name(self) -> None:
        boss_name = self.parsed_data[ItemConst.DROPPED_BY]
        dungeon_name = WowZone.get_boss_zone_name(boss_name)
        self.parsed_data[ItemConst.DROPPED_IN] = dungeon_name
        dungeon_short_name = WowZone.get_shortened_boss_zone_name(boss_name)
        self.parsed_data[ItemConst.FROM] = dungeon_short_name

    def add_statistic_boss_position(self) -> None:
        boss_name = self.parsed_data[ItemConst.DROPPED_BY]
        position = WowZone.get_boss_position(boss_name)
        self.parsed_data[ItemConst.BOSS] = position

    def add_statistic_item_drop_chance_per_spec(self) -> None:
        spec_ids = WowSpec.get_all_spec_ids()
        for spec_id in spec_ids:
            items = WowItem.get_all_items_for_spec(spec_id)
            boss_loot_table_size = 0
            for item in items:
                if spec_id in self.parsed_data[ItemConst.SPEC_IDS]:
                    if item.parsed_data[ItemConst.DROPPED_BY] == self.parsed_data[ItemConst.DROPPED_BY]:
                        if item.parsed_data[ItemConst.GEAR_SLOT] is not None: #Ignore mounts/quest items
                            #Only spec ID 65 (PaladinHoly) reaches a print statement placed here for item 221100. Why?????
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
                slot = loot_category.get_equip_slot()
                spec_drop_rates: Dict[str, str] = {}
                best_chance = 0.0
                class_items_considered = 0
                for spec_id in WowSpec.get_all_spec_ids_for_class(wow_class):
                    abbr_name = WowSpec.get_abbr_from_id(spec_id)
                    chance_of_no_drops = 1.0
                    items_considered = 0
                    for item in list(WowItem.get_all_items_for_spec(spec_id)):
                        matching_slot = item.parsed_data[ItemConst.GEAR_SLOT] == slot.get_ingame_name()
                        matching_mainstat = loot_category.get_mainstat() is None or item.has_mainstat(loot_category.get_mainstat())
                        if matching_slot and matching_mainstat:
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
                    class_items_considered = max(items_considered, class_items_considered)

                    spec_drop_rates[abbr_name] = f"{chance_of_at_least_one:.0f}%" #({items_considered} items)
                spec_drop_rates[ItemConst.AVAILABLE] = f"{class_items_considered} items"
                spec_drop_rates[wow_class.get_abbr()] = f"{best_chance:.0f}%"
                for value in spec_drop_rates.values():
                    if value != "0%":
                        class_drop_rates[loot_category.get_abbr()] = spec_drop_rates

            json_str = json.dumps(class_drop_rates, indent=4)
            folder = WowItem.drop_chance_folder
            path = folder / f"{wow_class.get_abbr()}.json"
            ScrapeUtils.Persistence.write_textfile(path, json_str)

    @staticmethod
    def scrape_wowhead_item(item_id: int) -> None:
        """Scrape item data from Wowhead and save it."""
        WowItem._set_trimmer_ruleset_for_wowhead_items()
        url = f"https://www.wowhead.com/item={item_id}"
        html_content = ScrapeUtils.Html.fetch_url(url)

        if len(html_content) == 0:
            print(f"Warning: html_content is Empty for zone_id {item_id}")
        wow_item = WowItem(item_id, html_content)
        WowItem.register_instance(item_id, wow_item)

    def is_mount_or_quest_item(self) -> bool:
        return self.parsed_data[ItemConst.GEAR_SLOT] == "" or self.parsed_data[ItemConst.GEAR_SLOT] is None

    def has_known_source(self) -> bool:
        if ItemConst.FROM not in self.parsed_data:
            return False
        if self.parsed_data[ItemConst.FROM] == WowheadZone.UNKNOWN_VALUE:
            return False
        return True

    def has_mainstat(self, mainstat: Optional[WowStatPrimary]) -> bool:
        if mainstat is not None:
            return mainstat.get_ingame_name() in self.parsed_data[ItemConst.PRIMARY_STATS]
        return False

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
