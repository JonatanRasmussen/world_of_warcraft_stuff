from pathlib import Path
from typing import Optional, Set, Dict, Any, List

from src.wow_npc import WowNpc
from src.wow_consts.wow_role import WowRole
from src.wow_consts.wow_spec import WowSpec
from src.wow_consts.wow_stat_primary import WowStatPrimary
from src.wow_item_scraper import WowItemScraper

class WowItem:
    """Represents a WoW item with data scraped from Wowhead."""

    json_folder: Path = Path.cwd() / "output" / "wowhead_items"

    _DEFAULT = "DEFAULT"

    # Column names that needs referencing by WowItemCsvExporter
    COLUMN_ITEM_ID = 'item_id'
    COLUMN_FROM = 'from'
    COLUMN_BOSS = 'boss'
    COLUMN_GEAR_SLOT = 'gear_slot'
    COLUMN_GEAR_TYPE = 'gear_type'
    COLUMN_STATS = 'stats'
    COLUMN_SPEC_IDS = 'spec_ids'
    COLUMN_SPEC_NAMES = 'spec_names'

    def __init__(self, item_id: int):
        """Initialize WowItem by scraping data via WowItemScraper"""
        self.item_id = item_id
        scraper = WowItemScraper.scrape_wowhead_item(item_id)
        self.name = scraper.name
        self.item_level = scraper.item_level
        self.bind = scraper.bind
        self.gear_slot = scraper.gear_slot
        self.gear_type = scraper.gear_type
        self.unique = scraper.unique
        self.primary_stats = scraper.primary_stats
        self.secondary_stats = scraper.secondary_stats
        self.required_level = scraper.required_level
        self.sell_price = scraper.sell_price
        self.dropped_by = scraper.dropped_by
        self.spec_ids = scraper.spec_ids
        self.spec_names = scraper.spec_names
        self.mainstat = scraper.mainstat
        self.distribution = scraper.distribution
        self.stats = scraper.stats
        # end of data from scraper
        self.dropped_in = WowItem._DEFAULT
        self.from_ = WowItem._DEFAULT # 'from' is a keyword in Python, so using 'from_'
        self.boss = WowItem._DEFAULT
        self.drop_chances: Dict[str, str] = {}

    def create_csv_row_data(self) -> Dict[str, Any]:
        row_data = {
            WowItem.COLUMN_ITEM_ID: self.item_id,
            'name': self.name,
            'item_level': self.item_level,
            'bind': self.bind,
            WowItem.COLUMN_GEAR_SLOT: self.gear_slot,
            WowItem.COLUMN_GEAR_TYPE: self.gear_type,
            'unique': self.unique,
            'primary_stats': ', '.join(map(str, self.primary_stats)),
            'secondary_stats': ', '.join(map(str, self.secondary_stats)),
            'required_level': self.required_level,
            'sell_price': self.sell_price,
            'dropped_by': self.dropped_by,
            'mainstat': self.mainstat,
            'distribution': self.distribution,
            WowItem.COLUMN_STATS: ', '.join(map(str, self.stats)),
            'dropped_in': self.dropped_in,
            WowItem.COLUMN_FROM: self.from_,
            WowItem.COLUMN_BOSS: self.boss,
            WowItem.COLUMN_SPEC_IDS: ', '.join(map(str, self.spec_ids)), #Moved to end
            WowItem.COLUMN_SPEC_NAMES: ', '.join(self.spec_names), #Moved to end
        }
        # Add each drop chance as a separate column
        for key, value in self.drop_chances.items():
            row_data[key] = value
        return row_data

    @staticmethod
    def get_all_items_for_spec(spec_id: int, all_items: List['WowItem']) -> Set['WowItem']:
        items: Set['WowItem'] = set()
        for item in all_items:
            if not item.is_mount_or_quest_item() and item.has_known_source():
                spec_ids: List[int] = []
                for scraped_spec_id in item.spec_ids:
                    if isinstance(scraped_spec_id, int):
                        spec_ids.append(scraped_spec_id)
                    else:
                        print(f"{scraped_spec_id} is not an int. It is type {type(scraped_spec_id)}")
                if spec_id in spec_ids:
                    items.add(item)
        return items

    @staticmethod
    def get_all_items_for_spec_and_slot(spec_id: int, slot_name: str, all_items: List['WowItem']) -> Set['WowItem']:
        items: Set['WowItem'] = set()
        for item in WowItem.get_all_items_for_spec(spec_id, all_items):
            if item.gear_slot == slot_name:
                items.add(item)
        return items

    def add_zone_data_to_item(self, zone_name: str, short_zone_name: str, bosses: List[WowNpc]) -> None:
        self.dropped_in = zone_name
        self.from_ = short_zone_name
        self.boss = WowNpc.get_boss_position(self.dropped_by, bosses)

    def calculate_drop_chance_per_spec(self, all_items: List['WowItem']) -> None:
        for spec_id in WowSpec.get_all_spec_ids():
            spec_abbr = WowSpec.get_abbr_from_id(spec_id)
            item_id_to_boss_mappings: Dict[int, str] = {}
            items = WowItem.get_all_items_for_spec(spec_id, all_items)
            if self not in items:
                self.drop_chances[spec_abbr] = f"{0}%"
            else:
                for item in items:
                    if spec_id in item.spec_ids:
                        if not item.is_mount_or_quest_item():
                            href_name = WowNpc.convert_display_name_to_href_name(item.dropped_by)
                            item_id_to_boss_mappings[item.item_id] = href_name

                # Now count how many items each boss drops
                boss_count_dict: Dict[str, int] = {}
                for value in item_id_to_boss_mappings.values():
                    if value in boss_count_dict:
                        boss_count_dict[value] += 1
                    else:
                        boss_count_dict[value] = 1
                # Finally, update the drop chance of self
                self_boss = WowNpc.convert_display_name_to_href_name(self.dropped_by)
                if self_boss in boss_count_dict:
                    self.drop_chances[spec_abbr] = f"{100 // boss_count_dict[self_boss]}%"
                else:
                    print("Error: This should not be possible!")

    """ def add_statistic_item_drop_chance_per_spec(self) -> None:
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
            self.parsed_data[column_name] = drop_chance """

    def is_mount_or_quest_item(self) -> bool:
        return self.gear_slot == "" or self.gear_slot is None

    def has_known_source(self) -> bool:
        if self.from_ == WowItemScraper.UNKNOWN_VALUE:
            return False
        return True

    def has_mainstat(self, mainstat: Optional[WowStatPrimary]) -> bool:
        if mainstat is not None:
            return mainstat.get_ingame_name() in self.primary_stats
        return False

    def drops_for_mainstat(self, mainstat: WowStatPrimary) -> bool:
        specs_within_mainstat = WowSpec.get_all_spec_ids_for_mainstat(mainstat)
        for spec_id in specs_within_mainstat:
            spec = WowSpec.get_spec_from_id(spec_id)
            drop_chance = self.drop_chances[spec.get_abbr()].rstrip('%')
            if drop_chance == 0 or drop_chance == "0":
                return False
        return True

    def drops_for_role(self, role: WowRole) -> bool:
        specs_within_role = WowSpec.get_all_spec_ids_for_role(role)
        for spec_id in specs_within_role:
            spec = WowSpec.get_spec_from_id(spec_id)
            drop_chance = self.drop_chances[spec.get_abbr()].rstrip('%')
            if drop_chance == 0 or drop_chance == "0":
                return False
        return True