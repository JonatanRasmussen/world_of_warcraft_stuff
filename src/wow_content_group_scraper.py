import json
import re
from typing import Dict, List

from scrape_utils import ScrapeUtils

class WowContentGroupScraper:
    """Scrapes data from wowhead for a wow content group."""

    @staticmethod
    def scrape_zone_ids(wowhead_zone_subpage: str) -> List[int]:
        """Scrape zone id data from Wowhead and save it."""
        WowContentGroupScraper._set_trimmer_ruleset_for_content_group()
        url = f"https://www.wowhead.com/zones/{wowhead_zone_subpage}"
        html_content = ScrapeUtils.Html.fetch_url(url)
        if len(html_content) == 0:
            print(f"Warning: html_content is Empty for zone_list {wowhead_zone_subpage}")
        zone_ids = list(WowContentGroupScraper._extract_zone_ids(html_content).keys())
        return zone_ids

    @staticmethod
    def _extract_zone_ids(html: str) -> Dict[int, str]:
        zone_data = {}
        data_match = re.search(r'data: (\[.*?\])', html, re.DOTALL)
        if data_match:
            data_str = data_match.group(1)
            try:
                data = json.loads(data_str)
                for zone in data:
                    if 'id' in zone and 'name' in zone:
                        zone_data[zone['id']] = zone['name']
            except json.JSONDecodeError:
                print("Error decoding JSON data")
        return zone_data

    @staticmethod
    def _set_trimmer_ruleset_for_content_group() -> None:
        """In ScrapeUtils.Trimmer, register trimming ruleset for wowhead.com/zones"""
        target_url = "wowhead.com/zones"
        html_start = '<script type="text/javascript">//'
        html_end = '//]]></script>'
        ScrapeUtils.Trimmer.register_trimming_ruleset(target_url, html_start, html_end)