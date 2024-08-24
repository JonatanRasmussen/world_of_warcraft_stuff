import re
from typing import List

class WowNpc:
    """Represents a WoW Npc (or boss) with data scraped from Wowhead."""

    def __init__(self, npc_id: int, display_name: str, href_name: str):
        self.npc_id = npc_id
        self.display_name = display_name
        self.href_name = href_name

    def print_info(self) -> None:
        print(f"Boss info: npc_id={self.npc_id}, display_name={self.display_name}, href_name={self.href_name}")

    def has_matching_name(self, boss_name: str) -> bool:
        href_boss_name = WowNpc.convert_display_name_to_href_name(boss_name)
        has_matching_href = self.href_name.lower() == href_boss_name.lower()
        has_matching_display_name = self.display_name == boss_name
        return has_matching_href or has_matching_display_name

    @staticmethod
    def get_boss_position(boss_name: str, boss_list: List['WowNpc']) -> str:
        for list_index, boss in enumerate(boss_list):
            if boss.has_matching_name(boss_name):
                position = f"{list_index + 1} of {len(boss_list)}"
                return position
        return "? of ?"

    @staticmethod
    def convert_display_name_to_href_name(display_name: str) -> str:
        """Convert npc name to the format used in wowhead urls"""
        # Remove apostrophes
        display_name = re.sub(r"'", '', display_name)
        # Replace non-alphanumeric characters with hyphens
        return re.sub(r'[^a-z0-9]+', '-', display_name.lower())

    @staticmethod
    def create_zone_encounter_boss_list(html: str) -> List['WowNpc']:
        """Create npc list based on html taken from a wowhead zone encounter overview."""
        npc_bosses: List[WowNpc] = []
        li_elements = re.findall(r'<li><div><a[^>]*>.*?</a>.*?</div></li>', html, re.DOTALL)

        for li in li_elements:
            npc_match = re.search(r'href="/npc=(\d+)/([^"]+)"', li)
            name_match = re.search(r'<a[^>]*>([^<]+)</a>', li)
            if npc_match:
                npc_id = int(npc_match.group(1))
                href_name = npc_match.group(2)
            else:
                npc_id = -1
                href_name = None

            display_name = name_match.group(1) if name_match else None
            if href_name is None:
                href_name = WowNpc.convert_display_name_to_href_name(str(display_name))
            if display_name:
                wow_npc = WowNpc(npc_id, display_name, href_name)
                npc_bosses.append(wow_npc)
        return npc_bosses
