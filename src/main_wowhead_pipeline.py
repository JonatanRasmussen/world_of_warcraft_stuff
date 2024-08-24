from typing import List, Callable

from src.output_validation import OutputValidation
from src.wow_content_group import WowContentGroup
from src.wow_content_group_factory import WowContentGroupFactory

class MainWowheadPipeline:

    factories: List[Callable[[], WowContentGroup]] = [
        WowContentGroupFactory.create_tww_hc_week,
        WowContentGroupFactory.create_tww_mplus_s1,
    ]
    validation_passed: List[bool] = []

    @staticmethod
    def main() -> None:
        for factory in MainWowheadPipeline.factories:
            print("Starting code execution...")
            content_group: WowContentGroup = factory()
            content_group.cascade_scrape_zones_and_its_items()

            print("Calculating drop chances for each item")
            content_group.calculate_drop_chance_for_all_wow_items()

            print("Generating csv files...")
            content_group.export_items_to_csv_for_all_specs_and_classes()

            print("Simming world tour...")
            content_group.sim_world_tour()

            print("Validating that each boss has items...")
            content_group.validate_that_each_boss_has_loot()

            is_valid = OutputValidation.validate(content_group.output_folder)
            MainWowheadPipeline.validation_passed.append(is_valid)
            print("Finished!\n")
        print(f"Validation passed summary: {MainWowheadPipeline.validation_passed}")