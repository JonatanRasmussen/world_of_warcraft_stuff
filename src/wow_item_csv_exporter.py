import csv
from copy import deepcopy
from io import StringIO
from pathlib import Path
from typing import Set, Dict, List

from src.wow_consts.wow_class import WowClass
from src.wow_consts.wow_loot_category import WowLootCategory
from src.wow_consts.wow_spec import WowSpec
from src.wow_item import WowItem
from scrape_utils import ScrapeUtils

class WowItemCsvExporter:

    ITEMS_FOR_SPEC_FOLDER = "items"
    ALL_ITEMS_CSV_NAME = "all_items.csv"
    ALL_COLUMNS_CSV_NAME = "all_columns.csv"

    @staticmethod
    def export_items_to_csv_for_all_specs_and_classes(all_items: List[WowItem], csv_path: Path) -> None:
        all_spec_ids = WowSpec.get_all_spec_ids()
        for wow_class in WowClass.get_all():
            class_spec_ids = WowSpec.get_all_spec_ids_for_class(wow_class)
            #for spec_id in class_spec_ids:
                #file_name = f"{WowSpec.get_abbr_from_id(spec_id)}.csv"
                #file_csv_path = csv_path / file_name
                #WowItemCsvExporter._export_items_to_csv([spec_id], file_csv_path, all_items)
            wow_class_csv_path = csv_path / f"{wow_class.get_abbr()}.csv"
            WowItemCsvExporter._export_items_to_csv(class_spec_ids, wow_class_csv_path, all_items)
        all_specs_csv_path = csv_path / WowItemCsvExporter.ALL_ITEMS_CSV_NAME
        WowItemCsvExporter._export_items_to_csv(all_spec_ids, all_specs_csv_path, all_items, empty_rows=False)
        all_columns_csv_path = csv_path / WowItemCsvExporter.ALL_COLUMNS_CSV_NAME
        WowItemCsvExporter._export_items_to_csv(all_spec_ids, all_columns_csv_path, all_items, all_columns=True, empty_rows=False)

    @staticmethod
    def _export_items_to_csv(spec_ids: List[int], csv_path: Path, all_items: List[WowItem], all_columns: bool = False, empty_rows: bool = True) -> None:
        original_items = set()
        for spec_id in spec_ids:
            original_items.update(WowItem.get_all_items_for_spec(spec_id, all_items))
        if not original_items:
            print(f"Warning: No items found for csv {csv_path}. Creating CSV anyway...")
        # Filter out mounts and quest items
        items: Set[WowItem] = deepcopy(original_items)
        sorted_items = WowItemCsvExporter._sort_items(items)
        columns = WowItemCsvExporter._get_columns_to_use(spec_ids)

        for item in sorted_items:
            item.prettify_table_by_removing_duplicate_droprates()

        if all_columns and len(sorted_items) != 0:
            row_data = all_items[0].create_csv_row_data()
            columns = list(row_data.keys())
        csv_content = StringIO()
        writer = csv.DictWriter(csv_content, fieldnames=columns, lineterminator='\n')
        writer.writeheader()

        write_header_next_week = False
        previous_week = None
        counter = 0
        for item in sorted_items:  # Write data for each item
            # Ensure all fields are present, use empty string for missing fields
            row_data = item.create_csv_row_data()
            row_data = {key: row_data.get(key, '') for key in columns}
            for key, value in row_data.items():
                if isinstance(value, list):  # Convert lists to strings for CSV compatibility
                    row_data[key] = ', '.join(map(str, value))
                # For slot statistics items, replace id with slot category name
                if key == WowItem.COLUMN_ITEM_ID and str(value) == "0":
                    row_data[key] = ''
                # For loot category (a.k.a. Type), dont show loot category on regular items
                if not all_columns:
                    if key == WowItem.COLUMN_LOOT_CATEGORY and ("(" and ")") not in value:
                        row_data[key] = ''

            current_week = row_data.get(WowItem.COLUMN_WEEK, '')
            if empty_rows and previous_week is not None and current_week != previous_week:
                # Write an empty row
                writer.writerow({key: '' for key in columns})

            if write_header_next_week:
                write_header_next_week = False
                writer.writerow({key: '' for key in columns})
                writer.writeheader()

            writer.writerow(row_data)
            previous_week = current_week

            if ('(' and ')') in row_data[WowItem.COLUMN_LOOT_CATEGORY]:
                counter += 1
                if counter >= 2 and empty_rows:
                    write_header_next_week = True
                    counter = 0

        ScrapeUtils.Persistence.write_textfile(csv_path, csv_content.getvalue())

    @staticmethod
    def _sort_items(sorted_item_list: Set['WowItem']) -> List['WowItem']:
        loot_category_order: Dict[str, int] = {category.name: index for index, category in enumerate(WowLootCategory)}

        def get_loot_category(item: 'WowItem') -> str:
            abbr = item.loot_category
            if "(" and ")" in item.loot_category:
                abbr = item.loot_category.split()[0]
            loot_category = WowLootCategory.get_from_abbr(abbr)
            return loot_category.name if loot_category else ''

        return sorted(
            list(sorted_item_list),
            key=lambda x: (
                loot_category_order.get(get_loot_category(x), len(WowLootCategory.get_all())+1),
                x.gear_slot or '',  # sort by slot #2 prio
                x.gear_type or '',  # sort by type #3 prio
                x.week or '',
                x.from_ or '',
                x.boss or '',
                x.name or '',
                x.item_id or ''  # Finally sort by id to avoid random row order
            )
        )

    @staticmethod
    def _sort_column_order(item_list: List['WowItem']) -> List[str]:
        columns: List[str] = []  # Create the fieldnames list with the desired order
        first_columns: List[str] = [WowItem.COLUMN_ITEM_ID, WowItem.COLUMN_WEEK, WowItem.COLUMN_FROM, WowItem.COLUMN_BOSS,
                                    WowItem.COLUMN_LOOT_CATEGORY, WowItem.COLUMN_GEAR_TYPE, WowItem.COLUMN_STATS,
                                    WowSpec.DK_BLOOD.get_abbr(), WowSpec.DK_FROST.get_abbr(), WowSpec.DK_UNHOLY.get_abbr()] # DK should alphabetically be before DH despite being shortened
        last_columns: List[str] = [WowItem.COLUMN_SPEC_IDS, WowItem.COLUMN_SPEC_NAMES]
        columns.extend(first_columns)

        # Get all unique keys from all items
        all_keys: Set[str] = set()
        for item in item_list:
            all_keys.update(item.create_csv_row_data().keys())

        middle_columns = sorted(list(all_keys - set(first_columns) - set(last_columns)))
        columns.extend(middle_columns)
        columns.extend(last_columns)
        return columns


    @staticmethod
    def _get_columns_to_use(spec_ids: List[int]) -> List[str]:
        columns_to_use = [
            WowItem.COLUMN_LOOT_CATEGORY,
            WowItem.COLUMN_FROM,
            WowItem.COLUMN_BOSS,
            WowItem.COLUMN_WEEK,
            WowItem.COLUMN_STATS,
        ]
        for spec_id in spec_ids:
            if spec_id == spec_ids[0]: #only do this once (but we need a spec_id)
                columns_to_use.append(WowSpec.get_spec_from_id(spec_id).get_class().get_abbr())
            columns_to_use.append(WowSpec.get_abbr_from_id(spec_id))
        columns_to_use.append(WowItem.COLUMN_ITEM_ID)
        return columns_to_use