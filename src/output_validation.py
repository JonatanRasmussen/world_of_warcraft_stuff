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
from scrape_utils import ScrapeUtils



class OutputValidation:

    @staticmethod
    def validate() -> None:
        test_folder: Path = Path.cwd() / "tests"
        csv_folder = WowItem.csv_folder
        all_class_slots_csv = "all_class_slots.csv"
        all_items_csv = "all_items.csv"
        real_out1 = ScrapeUtils.Persistence.read_textfile(csv_folder / all_class_slots_csv)
        real_out2 = ScrapeUtils.Persistence.read_textfile(csv_folder / all_items_csv)
        test_out1 = ScrapeUtils.Persistence.read_textfile(test_folder / all_class_slots_csv)
        test_out2 = ScrapeUtils.Persistence.read_textfile(test_folder / all_items_csv)
        out1_match = real_out1 == test_out1
        out2_match = real_out2 == test_out2
        if not out1_match:
            print("Warning: output1 does not match expected output!")
            #OutputValidation.print_differences(real_out1, test_out1)
        elif not out2_match:
            print("Warning: output2 does not match expected output!")
            #OutputValidation.print_differences(real_out2, test_out2)
        else:
            print("Validation was passed.")

    @staticmethod
    def print_differences(actual: str, expected: str) -> None:
        expected_lines = expected.splitlines()
        actual_lines = actual.splitlines()
        for i, (expected_line, actual_line) in enumerate(zip(expected_lines, actual_lines), start=1):
            if expected_line != actual_line:
                print(f"Line {i} differs:")
                print(f"Expected: {expected_line}")
                print(f"Actual:   {actual_line}")
                break
        if len(expected_lines) != len(actual_lines):
            print("File lengths differ.")
            print(f"Expected file length: {len(expected_lines)} lines.")
            print(f"Actual file length: {len(actual_lines)} lines.")
