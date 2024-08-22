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
from scrape_utils import ScrapeUtils

class WowItemCsvExporter:

    @staticmethod
    def create_fixed_size_csv() -> None:
        """
        Create a fixed-size CSV file containing all class and slot combinations.
        Each combination is represented by a fixed-length row section in the CSV.
        """
        nested_csv_tables: Dict[str, List[WowItem]] = {}
        for wow_class in WowClass.get_all():
            for slot in WowEquipSlot.get_all_ingame_names():
                items: List[WowItem] = []
                key = f"{wow_class.get_abbr()} {slot}"
                for spec_id in WowSpec.get_all_spec_ids_for_class(wow_class):
                    items.extend(list(WowItem.get_all_items_for_spec_and_slot(int(spec_id), slot)))

                # Sort items and ensure exactly a fixed_length number of items
                items = WowItemCsvExporter._sort_items(set(items))
                rows_for_slot = WowItemCsvExporter._decide_number_of_rows_in_fixed_csv(WowEquipSlot.get_from_ingame_name(slot))
                if len(items) > rows_for_slot:
                    print(f"Warning: More than {rows_for_slot} items for {key}. Truncating to {rows_for_slot}.")
                    items = items[:rows_for_slot]
                elif len(items) < rows_for_slot:
                    empty_item = WowItem(-1, "")  # Create an empty item
                    empty_item.parsed_data = {key: "" for key in WowItemCsvExporter._sort_column_order(items)}
                    items.extend([empty_item] * (rows_for_slot - len(items)))

                nested_csv_tables[key] = items

        # Prepare CSV content
        csv_content = StringIO()
        writer = None

        for key, items in nested_csv_tables.items():
            if writer is None:
                columns = ['category'] + WowItemCsvExporter._sort_column_order(items)
                writer = csv.DictWriter(csv_content, fieldnames=columns, lineterminator='\n')
                writer.writeheader()

            i = 0
            for item in items:
                i += 1
                row_data = {'category': f"{key} #{i}"}
                row_data.update({col: item.parsed_data.get(col, '') for col in columns if col != 'category'})
                for col, value in row_data.items():
                    if isinstance(value, list):
                        row_data[col] = ', '.join(map(str, value))
                writer.writerow(row_data)

        # Save CSV file
        spreadsheet_csv_path = WowItem.csv_folder / "all_class_slots.csv"
        ScrapeUtils.Persistence.write_textfile(spreadsheet_csv_path, csv_content.getvalue())

    @staticmethod
    def export_items_to_csv_for_all_specs_and_classes() -> None:
        all_spec_ids = WowSpec.get_all_spec_ids()
        for wow_class in WowClass.get_all():
            class_spec_ids = WowSpec.get_all_spec_ids_for_class(wow_class)
            for spec_id in class_spec_ids:
                file_name = f"{WowSpec.get_abbr_from_id(spec_id)}.csv"
                csv_path = WowItem.csv_folder / file_name
                WowItemCsvExporter._export_items_to_csv([spec_id], csv_path)
            wow_class_csv_path = WowItem.csv_folder / f"{wow_class.get_abbr()}.csv"
            WowItemCsvExporter._export_items_to_csv(class_spec_ids, wow_class_csv_path)
        all_specs_csv_path = WowItem.csv_folder / "all_items.csv"
        WowItemCsvExporter._export_items_to_csv(all_spec_ids, all_specs_csv_path)

    @staticmethod
    def _export_items_to_csv(spec_ids: List[int], csv_path: Path) -> None:
        items = set()
        for spec_id in spec_ids:
            items.update(WowItem.get_all_items_for_spec(spec_id))
        if not items:
            print(f"Warning: No items found for csv {csv_path}. Creating CSV anyway...")
        # Filter out mounts and quest items
        sorted_items = WowItemCsvExporter._sort_items(items)
        columns = WowItemCsvExporter._get_columns_to_use(spec_ids) #WowItemCsvExporter._sort_column_order(sorted_items)
        csv_content = StringIO()
        writer = csv.DictWriter(csv_content, fieldnames=columns, lineterminator='\n')
        writer.writeheader()
        for item in sorted_items:  # Write data for each item
            # Ensure all fields are present, use empty string for missing fields
            row_data = {key: item.parsed_data.get(key, '') for key in columns}
            for key, value in row_data.items():
                if isinstance(value, list):  # Convert lists to strings for CSV compatibility
                    row_data[key] = ', '.join(map(str, value))
            writer.writerow(row_data)
        ScrapeUtils.Persistence.write_textfile(csv_path, csv_content.getvalue())

    @staticmethod
    def _decide_number_of_rows_in_fixed_csv(loot_category: Optional[WowEquipSlot]) -> int:
        if loot_category == WowEquipSlot.TRINKET:
            return 24
        if loot_category in (WowEquipSlot.ONEHAND, WowEquipSlot.TWOHAND):
            return 24
        return 24

    @staticmethod
    def _sort_items(sorted_item_list: Set['WowItem']) -> List['WowItem']:

        gear_slot_order: Dict[str, int] = {slot.value: index for index, slot in enumerate(WowEquipSlot)}
        return sorted(
            list(sorted_item_list),
            key=lambda x: (
                gear_slot_order.get(str(x.parsed_data.get(ItemConst.GEAR_SLOT)), len(WowEquipSlot.get_all())+1),
                x.parsed_data.get(ItemConst.GEAR_SLOT) or '',  # sort by slot #1 prio
                x.parsed_data.get(ItemConst.GEAR_TYPE) or '',  # sort by type #2 prio
                x.parsed_data.get(ItemConst.DROPPED_IN) or '',
                x.parsed_data.get(ItemConst.BOSS) or '',
                x.parsed_data.get(ItemConst.ITEM_ID) or ''  # Finally sort by id to avoid random row order
            )
        )

    @staticmethod
    def _sort_column_order(item_list: List['WowItem']) -> List[str]:
        columns: List[str] = []  # Create the fieldnames list with the desired order
        first_columns: List[str] = [ItemConst.ITEM_ID, ItemConst.FROM, ItemConst.BOSS,
                                    ItemConst.GEAR_SLOT, ItemConst.GEAR_TYPE, ItemConst.STATS,
                                    WowSpec.DK_BLOOD.get_abbr(), WowSpec.DK_FROST.get_abbr(), WowSpec.DK_UNHOLY.get_abbr(),]
        last_columns: List[str] = [ItemConst.SPEC_IDS, ItemConst.SPEC_NAMES]
        columns.extend(first_columns)
        all_keys: Set[str] = set()  # Get all unique keys from all items
        for item in item_list:
            all_keys.update(item.parsed_data.keys())
        middle_columns = sorted(list(all_keys - set(first_columns) - set(last_columns)))
        columns.extend(middle_columns)
        columns.extend(last_columns)
        return columns


    @staticmethod
    def _get_columns_to_use(spec_ids: List[int]) -> List[str]:
        columns_to_use = [ItemConst.ITEM_ID, ItemConst.FROM, ItemConst.BOSS,
                          ItemConst.GEAR_SLOT, ItemConst.GEAR_TYPE, ItemConst.STATS]
        for spec_id in spec_ids:
            columns_to_use.append(WowSpec.get_abbr_from_id(spec_id))
        return columns_to_use