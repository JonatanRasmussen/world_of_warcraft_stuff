import json
from typing import Dict, List
from pathlib import Path

from src.wow_consts.wow_class import WowClass
from src.wow_consts.wow_equip_slot import WowEquipSlot
from src.wow_consts.wow_loot_category import WowLootCategory
from src.wow_consts.wow_spec import WowSpec
from src.wow_item import WowItem
from scrape_utils import ScrapeUtils

class SimWorldTour:
    """Simulate the expected loot outcome after doing each zone exactly once"""

    WORLD_TOUR_FOLDER = "sim"
    ITEM_AVAILABLE_COUNT = "Available"
    SOURCES_STR = "sources"

    # Group categories
    HC = "Hc"
    HC_CSV_VALUE = "1st/2nd week"
    M0 = "M0"
    M0_CSV_VALUE = "m0 week"
    DEFAULT_GROUP_CATEGORY_VALUE = ""

    @staticmethod
    def sim_world_tour(all_items: List['WowItem'], sim_path: Path) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Sim each spec looting 1 of each item available to them and calculate slot drop rates"""
        # Warning: high levels of indentation. Viewer discretion is adviced!
        all_class_drop_rates: Dict[str, Dict[str, Dict[str, str]]] = {}
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
                    for item in list(WowItem.get_all_items_for_spec(spec_id, all_items)):
                        matching_slot = item.gear_slot == slot.get_ingame_name()
                        matching_mainstat = loot_category.get_mainstat() is None or item.has_mainstat(loot_category.get_mainstat())
                        matching_role = loot_category.get_equip_slot() != WowEquipSlot.TRINKET or item.has_role(loot_category.get_role())
                        if matching_slot and matching_mainstat and matching_role:
                            drop_chance = item.drop_chances[abbr_name].rstrip('%')
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
                spec_drop_rates[SimWorldTour.ITEM_AVAILABLE_COUNT] = f"{class_items_considered} {SimWorldTour.SOURCES_STR}"
                spec_drop_rates[wow_class.get_abbr()] = f"{best_chance:.0f}%"
                for value in spec_drop_rates.values():
                    if value not in ("0%", f"0 {SimWorldTour.SOURCES_STR}"):
                        class_drop_rates[loot_category.get_abbr()] = spec_drop_rates

            json_str = json.dumps(class_drop_rates, indent=4)
            path = sim_path / f"{wow_class.get_abbr()}.json"
            ScrapeUtils.Persistence.write_textfile(path, json_str)
            all_class_drop_rates[wow_class.get_abbr()] = class_drop_rates
        return all_class_drop_rates

    @staticmethod
    def create_gearslot_statistics(abbr: str, world_tour_sim: Dict[str, Dict[str, Dict[str, str]]]) -> List[WowItem]:
        """Create a 'fake' WowItem that summarizes the findings of SimWorldTour"""
        formatted_abbr = SimWorldTour._format_group_abbr(abbr)
        gearslot_statistics: List[WowItem] = []
        for wow_class, loot_category_drop_chances in world_tour_sim.items():
            for loot_category, spec_drop_chances in loot_category_drop_chances.items():
                empty_item = WowItem.create_empty()
                empty_item.spec_ids.clear() #Is populated by all spec_ids by default if none was scraped
                empty_item.name = f"{loot_category} items for ({wow_class})"
                empty_item.week = abbr
                empty_item.from_ = f"{loot_category} ({wow_class})"
                empty_item.dropped_in = formatted_abbr
                empty_item.gear_slot = WowLootCategory.convert_abbr_to_ingame_equipslot(loot_category)
                empty_item.gear_type = formatted_abbr
                empty_item.boss = spec_drop_chances.get(SimWorldTour.ITEM_AVAILABLE_COUNT, f"? {SimWorldTour.SOURCES_STR}")
                for spec_abbr, drop_chance in spec_drop_chances.items():
                    # spec drop chance dict contains wow class and total item count. Ignore those.
                    if spec_abbr != wow_class and spec_abbr != SimWorldTour.ITEM_AVAILABLE_COUNT:
                        empty_item.drop_chances[spec_abbr] = drop_chance
                        spec_id = WowSpec.get_item_id_from_abbr(spec_abbr)
                        empty_item.spec_ids.append(spec_id)
                gearslot_statistics.append(empty_item)
        return gearslot_statistics

    @staticmethod
    def _format_group_abbr(group_abbr: str) -> str:
        """Quick and dirty implementation to put HC first and M0 last in alphabetical sorting"""
        # This results in correct row indexes for WowItems created by create_gearslot_statistics()
        if group_abbr == SimWorldTour.HC:
            return SimWorldTour.HC_CSV_VALUE
        if group_abbr == SimWorldTour.M0:
            return SimWorldTour.M0_CSV_VALUE
        return SimWorldTour.DEFAULT_GROUP_CATEGORY_VALUE