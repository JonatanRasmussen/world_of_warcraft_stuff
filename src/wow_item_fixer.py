from typing import Dict, List, Optional

from src.wow_consts.wow_role import WowRole
from src.wow_item_scraper import WowItemScraper

class WowItemFixer:
    """Hardcoded zone date for zones with bugged Wowhead pages."""

    _hardcoded_loot_tables: Dict[str, List[int]] = {
        # Mists of Tirna Scithe
        'Mistcaller': [
            178691, 178695, 178697, 178706, 178707,
            178710, 178715, 182305, 178705
        ],
        # The Necrotic Wake
        'Amarth, The Harvester': [
            178737, 178740, 178738, 178742, 178741,
            178739,
        ],
        'Surgeon Stitchflesh': [
            178750, 178744, 178748, 178772, 178751,
            178743, 178745, 178749,
        ],
        'Nalthor the Rimebinder': [
            178777, 178778, 178782, 178780, 178781,
            178783, 178779,
        ],
        # Siege of Boralus
        'Chopper Redhook': [
            162541, 159973, 159968, 159427, 159972,
            159969, 159965, 159251
        ],
        'Hadal Darkfathom': [
            159322, 159622, 159650, 159461, 159428,
            159386,
        ],
        "Viq'Goth": [
            231826, 231827, 231818, 231825, 231830,
            231822, 231824,
        ],
        # Grim Batol
        'Drahga Shadowburner': [
            133292, 133295, 133294, 133354, 133293,
            133363, 133296
        ],
    }

    hardcoded_item_loot_specs: Dict[int, List[WowRole]] = {
        # Tank trinkets with 'tankspec-only' in item description is not included
        # tww hc + tww s1.
        219298: [WowRole.DPS],
        219306: [WowRole.HEAL],
        219304: [WowRole.DPS],
        219310: [WowRole.HEAL],
        219294: [WowRole.DPS],
        219316: [WowRole.TANK],
        219320: [WowRole.HEAL],
        219319: [WowRole.DPS],
        219302: [WowRole.HEAL],
        219301: [WowRole.DPS],
        159622: [WowRole.DPS],
        178783: [WowRole.HEAL],
        178772: [WowRole.DPS],
        133304: [WowRole.HEAL],
        133291: [WowRole.TANK],
    }

    @staticmethod
    def try_fix_item_dropped_by(item_id: int, dropped_by: str) -> Optional[str]:
        boss = None
        for key, value in WowItemFixer._hardcoded_loot_tables.items():
            for itemid in value:
                if itemid == item_id:
                    boss = key
        if dropped_by == WowItemScraper.UNKNOWN_VALUE:
            if boss is None:
                print(f"Warning: {item_id} has unknown dropped_by, yet did not match any boss.")
            return boss
        if boss is not None and dropped_by != WowItemScraper.UNKNOWN_VALUE:
            print(f"Warning: {item_id} has a hardcoded dropped_by despite not needing it.")
        return None

    @staticmethod
    def try_fix_item_spec_ids(item_id: int) -> Optional[List[WowRole]]:
        wow_roles = WowItemFixer.hardcoded_item_loot_specs.get(item_id, None)
        if wow_roles:
            roles: List[WowRole] = []
            for role in wow_roles:
                roles.append(role)
            return roles
        return None
