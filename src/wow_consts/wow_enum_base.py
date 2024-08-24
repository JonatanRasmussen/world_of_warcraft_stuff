from enum import Enum
from typing import List, Optional, TypeVar, Type

WowEnumT = TypeVar('WowEnumT', bound='WowEnumBase')

class WowEnumBase(Enum):
    """Base class for all WoW enums."""

    @classmethod
    def get_all(cls: Type[WowEnumT]) -> List[WowEnumT]:
        return list(cls)

    @classmethod
    def get_all_abbrs(cls) -> List[str]:
        abbreviations: List[str] = []
        for enum in cls:
            abbreviations.append(enum.get_abbr())
        return abbreviations

    @classmethod
    def get_all_ingame_names(cls) -> List[str]:
        ingame_names: List[str] = []
        for enum in cls:
            ingame_names.append(enum.get_ingame_name())
        return ingame_names

    @classmethod
    def get_from_ingame_name(cls: Type[WowEnumT], ingame_name: str) -> Optional[WowEnumT]:
        for enum in cls:
            if enum.get_ingame_name() == ingame_name:
                return enum
        return None

    @classmethod
    def get_from_abbr(cls: Type[WowEnumT], abbr: str) -> WowEnumT:
        for enum in cls:
            if enum.get_abbr() == abbr:
                return enum
        raise ValueError(f"No enum matched the abbr {abbr}")


    def get_abbr(self) -> str:
        return ''.join(word.capitalize() for word in self.name.split('_'))

    def get_ingame_name(self) -> str:
        return self.value
