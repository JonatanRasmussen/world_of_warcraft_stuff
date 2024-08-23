from typing import List

from src.wow_content_group import WowContentGroup

class WowContentGroupFactory:

    @staticmethod
    def create_tww_hc_week() -> WowContentGroup:
        group_name = "tww_hc_week"
        zone_ids: List[int] = []
        wowhead_suburl = "war-within/dungeons"
        content_group = WowContentGroup(group_name, zone_ids, wowhead_suburl)
        #Remove fake dungeon zzoldPriory
        content_group.zone_ids.remove(15055)
        return content_group

    @staticmethod
    def create_tww_mplus_s1() -> WowContentGroup:
        group_name = "tww_s1_mplus"
        zone_ids = [15093, 14971, 14883, 14979, 13334, 12916, 9354, 4950]
        return WowContentGroup(group_name, zone_ids)