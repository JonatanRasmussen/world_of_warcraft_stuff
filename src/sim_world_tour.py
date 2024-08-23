import json
from typing import Dict, List
from pathlib import Path

from src.wow_consts.wow_class import WowClass
from src.wow_consts.wow_loot_category import WowLootCategory
from src.wow_consts.wow_spec import WowSpec
from src.wow_item import WowItem
from scrape_utils import ScrapeUtils

class SimWorldTour:

    WORLD_TOUR_FOLDER = "sim"
    ITEM_AVAILABLE_COUNT = "Available"

    @staticmethod
    def sim_world_tour(all_items: List['WowItem'], sim_path: Path) -> None:
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
                    if items_considered == 1 or items_considered == 2:
                        pass
                    for item in list(WowItem.get_all_items_for_spec(spec_id, all_items)):
                        matching_slot = item.gear_slot == slot.get_ingame_name()
                        matching_mainstat = loot_category.get_mainstat() is None or item.has_mainstat(loot_category.get_mainstat())
                        if matching_slot and matching_mainstat:
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
                spec_drop_rates[SimWorldTour.ITEM_AVAILABLE_COUNT] = f"{class_items_considered} items"
                spec_drop_rates[wow_class.get_abbr()] = f"{best_chance:.0f}%"
                for value in spec_drop_rates.values():
                    if value not in ("0%", "0 items"):
                        class_drop_rates[loot_category.get_abbr()] = spec_drop_rates

            json_str = json.dumps(class_drop_rates, indent=4)
            path = sim_path / f"{wow_class.get_abbr()}.json"
            ScrapeUtils.Persistence.write_textfile(path, json_str)