from pathlib import Path
from typing import Optional, Set, Dict, Any, List, Iterable

from src.wow_npc import WowNpc
from src.wow_consts.wow_equip_type_armor import WowEquipTypeArmor
from src.wow_consts.wow_loot_category import WowLootCategory
from src.wow_consts.wow_equip_slot import WowEquipSlot
from src.wow_consts.wow_role import WowRole
from src.wow_consts.wow_class import WowClass
from src.wow_consts.wow_spec import WowSpec
from src.wow_consts.wow_stat_primary import WowStatPrimary
from src.wow_item_scraper import WowItemScraper
from src.wow_item_fixer import WowItemFixer

class WowItem:
    """Represents a WoW item with data scraped from Wowhead."""

    json_folder: Path = Path.cwd() / "output" / "wowhead_items"

    UNINITIALIZED_VALUE = "NOT_INITIALIZED"
    UNKNOWN_VALUE = WowItemScraper.UNKNOWN_VALUE
    EMPTY_ITEM_ID = 0
    DROP_CHANCE_REPLACEMENT = ""
    EMPTY_GEAR_TYPE_VALUE = "Other"

    # Column names that needs referencing by WowItemCsvExporter
    COLUMN_ITEM_ID = 'ID'
    COLUMN_NAME = 'Name'
    COLUMN_FROM = 'Dungeon'
    COLUMN_BOSS = 'Boss'
    COLUMN_GEAR_SLOT = 'gear_slot'
    COLUMN_GEAR_TYPE = 'gear_type'
    COLUMN_STATS = 'stats'
    COLUMN_LOOT_CATEGORY = 'Type'
    COLUMN_WEEK = 'Week'
    COLUMN_SPEC_IDS = 'spec_ids'
    COLUMN_SPEC_NAMES = 'spec_names'

    def __init__(self, item_id: int, scrape_from_wowhead: bool = True):
        """Initialize WowItem by scraping data via WowItemScraper"""
        self.item_id = item_id
        if scrape_from_wowhead:
            scraper = WowItemScraper.scrape_wowhead_item(item_id)
        else:
            scraper = WowItemScraper.create_empty(item_id)
        self.name = scraper.name
        self.item_level = scraper.item_level
        self.bind = scraper.bind
        self.gear_slot = scraper.gear_slot
        self.gear_type = WowEquipTypeArmor.assign_non_empty_gear_type(scraper.gear_type)
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
        self.dropped_in = WowItem.UNINITIALIZED_VALUE
        self.from_ = WowItem.UNINITIALIZED_VALUE # 'from' is a keyword in Python, so using 'from_'
        self.week = WowItem.UNINITIALIZED_VALUE
        self.boss = WowItem.UNINITIALIZED_VALUE
        self.drop_chances: Dict[str, str] = {}
        self.check_if_any_hardcoded_values_exist_for_this_item()
        self.loot_category = self.set_loot_category()

    @classmethod
    def create_empty(cls) -> 'WowItem':
        return WowItem(WowItem.EMPTY_ITEM_ID, scrape_from_wowhead=False)

    def set_loot_category(self) -> str:
        if self.item_id == WowItem.EMPTY_ITEM_ID or self.is_mount_or_quest_item():
            return WowItem.UNKNOWN_VALUE
        loot_category = WowLootCategory.get_from_gear_slot_and_stats(self.item_id, self.gear_slot, self.stats)
        if loot_category is None:
            return WowItem.UNKNOWN_VALUE
        return loot_category.get_abbr()

    def check_if_any_hardcoded_values_exist_for_this_item(self) -> None:
        """Check in WowItemFixer if any hardcoded dropped_by values are provided for this item_id"""
        if not self.is_mount_or_quest_item():
            optional_fixed_dropped_by = WowItemFixer.try_fix_item_dropped_by(self.item_id, self.dropped_by)
            if optional_fixed_dropped_by is not None:
                self.dropped_by = optional_fixed_dropped_by
            optional_hardcoded_roles = WowItemFixer.try_fix_item_spec_ids(self.item_id)
            if optional_hardcoded_roles is not None:
                spec_ids: List[int] = []
                for wow_role in optional_hardcoded_roles:
                    spec_ids.extend(WowSpec.get_all_spec_ids_for_role(wow_role))
                    self.gear_type = WowLootCategory.get_trinket_gear_type(wow_role)
                    self.stats = WowLootCategory.get_trinket_category(self.gear_type, self.stats)
                self.spec_ids = spec_ids
                self.spec_names = WowItemScraper.extract_spec_names(spec_ids)

    def create_csv_row_data(self) -> Dict[str, Any]:
        row_data = {
            WowItem.COLUMN_ITEM_ID: self.item_id,
            WowItem.COLUMN_NAME: self.name,
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
            WowItem.COLUMN_STATS: self.stats,
            WowItem.COLUMN_LOOT_CATEGORY: self.loot_category,
            'dropped_in': self.dropped_in,
            WowItem.COLUMN_FROM: self.from_,
            WowItem.COLUMN_WEEK: self.week,
            WowItem.COLUMN_BOSS: self.boss,
            WowItem.COLUMN_SPEC_IDS: ', '.join(map(str, self.spec_ids)), #Moved to end
            WowItem.COLUMN_SPEC_NAMES: ', '.join(map(str, self.spec_names)), #Moved to end
        }
        # Add each drop chance as a separate column
        for key, value in self.drop_chances.items():
            row_data[key] = value
        return row_data

    @staticmethod
    def get_all_items_for_spec(spec_id: int, all_items: List['WowItem']) -> Set['WowItem']:
        items: Set['WowItem'] = set()
        for item in all_items:
            if not item.is_mount_or_quest_item():
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

    @staticmethod
    def count_items_with_special_id(all_items: Iterable['WowItem']) -> int:
        count = 0
        for item in all_items:
            if item.item_id == WowItem.EMPTY_ITEM_ID:
                count += 1
        return count

    @staticmethod
    def validate_each_hardcoded_item_spec_exists_in_items(all_items: Iterable['WowItem']) -> None:
        for hardcoded_item in WowItemFixer.hardcoded_item_loot_specs:
            found = False
            for item in all_items:
                if item.item_id == hardcoded_item:
                    found = True
            if not found:
                print(f"Warning: item {hardcoded_item} was not found in all_items!")

    def add_zone_data_to_item(self, zone_name: str, short_zone_name: str, week: str, bosses: List[WowNpc]) -> None:
        self.dropped_in = zone_name
        self.from_ = short_zone_name
        self.week = week
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
        self.calculate_drop_chance_per_class()

    def calculate_drop_chance_per_class(self) -> None:
        for wow_class in WowClass.get_all():
            class_spec_ids = WowSpec.get_all_spec_ids_for_class(wow_class)
            drop_chances: List[int] = []
            for class_spec_id in class_spec_ids:
                spec_abbr = WowSpec.get_abbr_from_id(class_spec_id)
                drop_chance_str = self.drop_chances[spec_abbr].rstrip('%')
                try:
                    drop_chances.append(int(drop_chance_str))
                except ValueError:
                    print(f"Warning: {drop_chance_str} could not be parsed to a number")
            self.drop_chances[wow_class.get_abbr()] = f"{max(drop_chances)}%"

    def prettify_table_by_removing_duplicate_droprates(self) -> None:
        replacement = WowItem.DROP_CHANCE_REPLACEMENT
        for spec in WowSpec.get_all():
            wow_class = spec.get_class()
            spec_ids_for_class = WowSpec.get_all_spec_ids_for_class(wow_class)
            for spec_id in spec_ids_for_class:
                class_spec = WowSpec.get_spec_from_id(spec_id)
                if class_spec.get_abbr() in self.drop_chances:
                    drop_chance = self.drop_chances[class_spec.get_abbr()]
                    if not drop_chance == replacement:
                        if self.drop_chances[wow_class.get_abbr()] == drop_chance:
                            self.drop_chances[class_spec.get_abbr()] = replacement

    def is_mount_or_quest_item(self) -> bool:
        return self.gear_slot == "" or self.gear_slot is None or self.gear_type == "Cosmetic"

    def has_known_source(self) -> bool:
        if self.from_ == WowItemScraper.UNKNOWN_VALUE:
            return False
        return True

    def has_mainstat(self, mainstat: Optional[WowStatPrimary]) -> bool:
        if mainstat is not None:
            return mainstat.get_ingame_name() in self.primary_stats
        return False

    def has_role(self, role: Optional[WowRole]) -> bool:
        if self.gear_slot == WowEquipSlot.TRINKET.get_ingame_name():
            return WowLootCategory.get_trinket_gear_type(role) == self.gear_type
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

    def is_duplicate(self, all_items: List['WowItem']) -> bool:
        if not self.item_id == WowItem.EMPTY_ITEM_ID:
            for item in all_items:
                if item.item_id == self.item_id:
                    return True
        return False