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
from src.wow_item import WowItem
from src.wow_item_csv_exporter import WowItemCsvExporter
from src.wow_zone import WowZone, WowheadZone
from src.wow_zonelist import WowZoneList, WowheadZoneList
from src.output_validation import OutputValidation
from scrape_utils import ScrapeUtils


class MainWowheadPipeline:

    # Config: tww hc week OR tww s1 mplus
    scrape_hc_week = True

    @staticmethod
    def main() -> None:
        print("Starting code execution...")

        if MainWowheadPipeline.scrape_hc_week:
            # Treat it as a wowhead.com zone overview page
            WowItem.csv_folder = Path.cwd() / "output" / "tww_hc_week_csv"
            WowItem.drop_chance_folder = Path.cwd() / "output" / "tww_hc_week_drop_chances"
            zone_group_url = "war-within/dungeons"
            WowZoneList.scrape_wowhead_zone_list(zone_group_url)
            every_zone_id = WowZoneList.get_all_zone_ids()
        else:
            WowItem.csv_folder = Path.cwd() / "output" / "tww_s1_mplus_csv"
            WowItem.drop_chance_folder = Path.cwd() / "output" / "tww_s1_mplus_drop_chances"
            every_zone_id = [15093, 14971, 14883, 14979, 13334, 12916, 9354, 4950]
        for my_zone in every_zone_id:
            WowZone.scrape_wowhead_zone(my_zone)

        every_item_ids = WowZone.get_all_item_ids()
        for my_index, my_item in enumerate(every_item_ids):
            print(f"Scraping {my_item} ({my_index+1} of {len(every_item_ids)})")
            WowItem.scrape_wowhead_item(my_item)

        print("Creating item jsons...")
        WowItem.parse_statistics_across_all_items_and_write_json()

        print("Building csv files...")
        WowItemCsvExporter.export_items_to_csv_for_all_specs_and_classes()
        WowItemCsvExporter.create_fixed_size_csv()

        WowItem.sim_world_tour()

        OutputValidation.validate()
        print("Finished!")