import re
from pathlib import Path
from typing import List, Dict

from src.wow_consts.wow_loot_category import WowLootCategory
from src.wow_item import WowItem
from src.wow_zone import WowZone
from src.wow_content_group_scraper import WowContentGroupScraper
from src.wow_item_csv_exporter import WowItemCsvExporter
from src.output_validation import OutputValidation
from src.sim_world_tour import SimWorldTour

class WowContentGroup:
    """Represents a set of WoW zones (m+ dungeon pool or similar)."""

    TWW_HC_WEEK = "tww_hc_week"
    TWW_S1_MPLUS = "tww_s1_mplus"

    COMBINED_NAME = "all"

    def __init__(self, group_name: str, group_abbr: str, zone_ids: List[int], wowhead_zone_subpage: str = ""):
        """Initialize WowZoneGroup with zone list and HTML content."""
        self.group_name = group_name
        self.group_abbr = group_abbr
        self.output_folder = WowContentGroup._convert_group_name_to_folder(group_name)
        self.output_path = WowContentGroup._create_output_path(group_name)
        self.zone_ids = zone_ids
        if len(zone_ids) == 0:
            self.zone_ids = WowContentGroupScraper.scrape_zone_ids(wowhead_zone_subpage)
        self.wow_zones: List[WowZone] = []
        self.world_tour_sim: Dict[str, Dict[str, Dict[str, str]]] = {}
        self.gearslot_statistics: List[WowItem] = []

    def cascade_scrape_zones_and_its_items(self) -> None:
        for zone_id in self.zone_ids:
            wow_zone = WowZone(zone_id)
            self.wow_zones.append(wow_zone)

    def get_all_wow_items(self) -> List[WowItem]:
        all_items: List[WowItem] = []
        for zone in self.wow_zones:
            all_items.extend(zone.get_all_wow_items())
        return list(set(all_items))

    def calculate_drop_chance_for_all_wow_items(self) -> None:
        all_items = self.get_all_wow_items()
        for item in all_items:
            item.calculate_drop_chance_per_spec(all_items)

    def sim_world_tour(self) -> None:
        all_items = self.get_all_wow_items()
        world_tour_path = self.output_path / SimWorldTour.WORLD_TOUR_FOLDER
        self.world_tour_sim = SimWorldTour.sim_world_tour(all_items, world_tour_path)

    def create_gearslot_statistics(self) -> None:
        self.gearslot_statistics = SimWorldTour.create_gearslot_statistics(self.group_abbr, self.world_tour_sim)

    def export_items_to_csv_for_all_specs_and_classes(self) -> None:
        all_items = self.get_all_wow_items() + self.gearslot_statistics
        path = self.output_path / WowItemCsvExporter.ITEMS_FOR_SPEC_FOLDER
        WowItemCsvExporter.export_items_to_csv_for_all_specs_and_classes(all_items, path)

    @staticmethod
    def export_csv_for_two_groups(groups: List['WowContentGroup']) -> None:
        all_items: List[WowItem] = []
        for group in groups:
            all_items.extend(group.get_all_wow_items())
            all_items.extend(group.gearslot_statistics)
        all_items_no_dupes = list(set(all_items))
        path = WowContentGroup._create_output_path(WowContentGroup.COMBINED_NAME)
        WowItemCsvExporter.export_items_to_csv_for_all_specs_and_classes(all_items_no_dupes, path)

    def validate_that_each_boss_has_loot(self) -> None:
        all_items = self.get_all_wow_items()
        for zone in self.wow_zones:
            zone.validate_that_each_boss_has_loot(all_items)

    @staticmethod
    def _convert_group_name_to_folder(group_name: str) -> str:
        """Convert npc name to the format used in wowhead urls"""
        return re.sub(r'[^a-z0-9]+', '_', group_name.lower())

    @staticmethod
    def _create_output_path(group_name: str) -> Path:
        folder = WowContentGroup._convert_group_name_to_folder(group_name)
        base_output_folder = OutputValidation.BASE_OUTPUT_FOLDER
        return Path.cwd() / base_output_folder / folder