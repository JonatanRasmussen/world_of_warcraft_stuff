import re
from typing import List

from src.wow_npc import WowNpc
from scrape_utils import ScrapeUtils

class WowZoneScraper:
    """Scrapes data from Wowhead for specified WowZone"""

    def __init__(self, zone_id: int, html_string: str):
        """Scrape wowhead data for zone_id"""
        self.zone_id = zone_id
        self.html_string = html_string
        self.zone_name = self.extract_name()
        self.bosses = WowNpc.create_zone_encounter_boss_list(html_string)
        self.item_ids = self.extract_item_ids()

    def print_extracted_info(self) -> None:
        print(f"Info: Zone_id {self.zone_id} was parsed as {self.zone_name} "
              f"with {len(self.bosses)} bosses and "
              f"{len(self.item_ids)} items")

    @staticmethod
    def scrape_wowhead_zone(zone_id: int) -> 'WowZoneScraper':
        """Scrape zone data from Wowhead and save it."""
        WowZoneScraper._set_trimmer_ruleset_for_wowhead_zone()
        url = f"https://www.wowhead.com/zone={zone_id}"
        html_content = ScrapeUtils.Html.fetch_url(url)
        if len(html_content) == 0:
            print(f"Warning: html_content is Empty for zone_id {zone_id}")
        return WowZoneScraper(zone_id, html_content)


    def extract_item_ids(self) -> List[int]:
        gatherer_data_pattern = r'WH\.Gatherer\.addData\(3, 1, ({.*?})\);'
        gatherer_data_matches = re.findall(gatherer_data_pattern, self.html_string, re.DOTALL)
        item_ids = []
        for gatherer_data_str in gatherer_data_matches:
            item_id_pattern = r'"(\d+)":\s*{'
            item_ids.extend([int(item_id) for item_id in re.findall(item_id_pattern, gatherer_data_str)])
        return item_ids

    def extract_name(self) -> str:
        # Method 1: Check the h1 tag
        h1_pattern = r'<h1 class="heading-size-1[^"]*"><span[^>]*>([^<]+)</span></h1>'
        match = re.search(h1_pattern, self.html_string)
        if match:
            return match.group(1)

        # Method 2: Check for zone data in WH.Gatherer.addData
        gatherer_pattern = r'WH\.Gatherer\.addData\(7,\s*1,\s*{[^}]*"name_enus":"([^"]+)"'
        match = re.search(gatherer_pattern, self.html_string)
        if match:
            return match.group(1)

        # Method 3: Check for Mapper initialization
        mapper_pattern = r'var myMapper = new Mapper\({[^}]*"name":"([^"]+)"'
        match = re.search(mapper_pattern, self.html_string)
        if match:
            return match.group(1)

        # Method 4: Look for the name in the URL or other metadata
        links_pattern = r'WH\.Links\.show\(this,\s*{[^}]*"typeId":(\d+)'
        match = re.search(links_pattern, self.html_string)
        if match:
            type_id = match.group(1)
            type_id_pattern = rf'"{type_id}":{{"name_enus":"([^"]+)"'
            match = re.search(type_id_pattern, self.html_string)
            if match:
                return match.group(1)

        # Method 5: Look for the name in the article content
        article_pattern = r'\[zone=\d+\]([^\[]+)\[\/zone\]'
        match = re.search(article_pattern, self.html_string)
        if match:
            return match.group(1)

        print(f"Warning: Zone with ID {self.zone_id} failed to parse its zone name from the wowhead html!")
        return "Zone could not be parsed"

    @staticmethod
    def _set_trimmer_ruleset_for_wowhead_zone() -> None:
        """In ScrapeUtils.Trimmer, register trimming ruleset for wowhead.com/zone"""
        target_url = "wowhead.com/zone="
        html_start = '<div class="text">'
        html_end = 'var tabsRelated = new Tabs'
        ScrapeUtils.Trimmer.register_trimming_ruleset(target_url, html_start, html_end)
