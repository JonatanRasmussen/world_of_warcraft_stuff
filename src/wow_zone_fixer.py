from typing import Dict, List, Optional

from src.wow_npc import WowNpc

class WowZoneFixer:
    """Hardcoded zone date for zones with bugged Wowhead pages."""

    release_category_hc = "Hc"
    release_category_m0_s1 = "m0"
    release_category_both = "both"
    release_week_category_missing = ""


    _hardcoded_boss_lists: Dict[int, List[WowNpc]] = {
        # Siege of Boralus (fix for wowhead showing both Alliance and Horde version of bosses)
        9354: [
            WowNpc(144160, "Chopper Redhook", "chopper-redhook"),
            WowNpc(129208, "Dread Captain Lockwood", "dread-captain-lockwood"),
            WowNpc(130836, "Hadal Darkfathom", "hadal-darkfathom"),
            WowNpc(128652, "Viq'Goth", "viqgoth")
        ],
        # The Stonevaults (fix for E.D.N.A. being called e-d-n-a on items but e-d-n-a- in href)
        14883: [
            WowNpc(210108, "E.D.N.A.", "e-d-n-a"),
            WowNpc(210156, "Skarmorak", "skarmorak"),
            WowNpc(213216, "Master Machinists", "speaker-dorlita"), #dorlita / dorlitam
            WowNpc(213119, "Void Speaker Eirich", "void-speaker-eirich"),
        ],
    }

    _hardcoded_item_lists: Dict[int, List[int]] = {
        # Grim Batol (fix for legacy dungeon loot table. Also, Drahga Shadowburner is missing)
        4950: [
            133282, 133283, 133284, 133285, 133286,
            133287, 133288, 133289, 133290, 133291,
            133297, 133298, 133299, 133300, 133301,
            133302, 133303, 133304, 133305, 133306,
            133308, 133309, 133353, 133374, 133292,
            133295, 133294, 133354, 133293, 133363,
            133296,
        ],
        # Siege of Boralus (fix for wowhead showing both Alliance and Horde version of loot)
        9354: [
            159237, 159250, 159309, 159320, 159322,
            159372, 159379, 159386, 159428, 159429,
            159434, 159461, 159622, 159623, 159649,
            159650, 159251, 159427, 159965, 159968,
            159969, 159972, 159973, 162541, 231826,
            231827, 231818, 231825, 231830, 231822,
            231824, 159256, 159651
        ],
        # The Dawnbreaker (fix for last boss' loot missing from zone loot table)
        14971: [
            219311, 219312, 221132, 221133, 221134,
            221135, 221136, 221137, 221138, 221139,
            221140, 221141, 221142, 221202, 225574,
            212453, 212437, 225586, 212391, 212448,
            212440, 212398, 225583,
        ],
        # The Stonevaults (fix for E.D.N.A. boss' loot missing from zone loot table)
        14883: [
            219300, 219301, 219302, 219303, 221079,
            221080, 221081, 221082, 221083, 221084,
            221085, 221086, 221087, 221088, 221089,
            221090, 221091, 221092, 221094, 221095,
            226683, 221077, 221076, 221074, 221078,
            219315, 221073, 221075,
        ],
    }

    _manually_inspected_loot_table_sizes: Dict[int, int] = {
        15093: 19,
        14883: 14,
        14979: 28,
        14938: 23,
        15103: 26,
        14882: 25,
        14954: 21,
        13334: 32,
        12916: 33,
    }

    _release: Dict[int, str] = {
        14938: release_category_hc,
        15103: release_category_hc,
        14882: release_category_hc,
        14954: release_category_hc,
        15093: release_category_both,
        14971: release_category_both,
        14883: release_category_both,
        14979: release_category_both,
        13334: release_category_m0_s1,
        12916: release_category_m0_s1,
        9354: release_category_m0_s1,
        4950: release_category_m0_s1,
    }
    """ 12916,
    9354,
    4950, """

    @staticmethod
    def get_release_week(zone_id: int) -> str:
        missing = WowZoneFixer.release_week_category_missing
        return WowZoneFixer._release.get(zone_id, missing)

    @staticmethod
    def missing_source_is_ok(zone_id: int) -> bool:
        return zone_id in [] #for now, missing sources should be hardcoded in

    @staticmethod
    def try_fix_boss_list(zone_id: int) -> Optional[List[WowNpc]]:
        return WowZoneFixer._hardcoded_boss_lists.get(zone_id, None)

    @staticmethod
    def try_fix_item_list(zone_id: int) -> Optional[List[int]]:
        WowZoneFixer.validate_no_duplicates_in_hardcoded_item_lists()
        return WowZoneFixer._hardcoded_item_lists.get(zone_id, None)

    @staticmethod
    def has_expected_loot_table_size(zone_id: int, item_ids: List[int]) -> bool:
        manual_count = WowZoneFixer._manually_inspected_loot_table_sizes.get(zone_id, -1)
        if manual_count == -1:
            return True # If no expected loot table size exists, do not raise a warning
        automated_count = len(item_ids)
        if automated_count == manual_count:
            return True
        if automated_count > manual_count:
            many_or_few = "many"
        else:
            many_or_few = "few"
        print(f"Warning: Too {many_or_few} items found! Expected: {manual_count}, actual: {automated_count}")
        return False

    @staticmethod
    def validate_no_duplicates_in_hardcoded_item_lists() -> None:
        for key, item_list in WowZoneFixer._hardcoded_item_lists.items():
            item_set = set(item_list)
            if len(item_set) != len(item_list):
                print(f"Warning: Duplicate item_id in {key}: lengths {len(item_set)} != {len(item_list)}")





