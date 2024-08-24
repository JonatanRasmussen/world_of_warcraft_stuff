from .wow_enum_base import WowEnumBase

class WowStatBase(WowEnumBase):
    """Base class for WoW primary and secondary stats providing common methods."""

    def get_single_letter_name(self) -> str:
        return self.name[0]