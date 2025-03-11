from __future__ import annotations

from typing import Iterable, Optional

from dramatis.ai import Proclivity


class Trait:
    """A trait associated with a character."""

    __slots__ = ("uid", "name", "conflicting_traits", "proclivities")

    uid: int
    """The unique ID of this trait."""
    name: str
    """The name of this trait."""
    conflicting_traits: set[str]
    """The names of traits that conflict with this trait."""
    proclivities: list[Proclivity]
    """Proclivities added to the character when this trait is attached."""

    def __init__(
        self,
        name: str,
        conflicting_traits: Optional[Iterable[str]] = None,
        proclivities: Optional[Iterable[Proclivity]] = None,
    ) -> None:
        self.uid = -1
        self.name = name
        self.conflicting_traits = (
            set(conflicting_traits) if conflicting_traits else set()
        )
        self.proclivities = list(proclivities) if proclivities else []


class TraitDatabase:
    """The database of all traits defined for a story world."""

    __slots__ = ("_uid_to_trait_map", "_name_to_uid_map", "_next_trait_uid")

    _next_trait_uid: int
    """The UID assigned to the next trait in the database."""
    _uid_to_trait_map: dict[int, Trait]
    """Trait UIDs mapped to trait instances."""
    _name_to_uid_map: dict[str, int]
    """Trait names mapped to UIDs."""

    def __init__(self) -> None:
        self._next_trait_uid = 1
        self._uid_to_trait_map = {}
        self._name_to_uid_map = {}

    def get_traits(self) -> list[Trait]:
        """Get all traits in the database."""
        return list(self._uid_to_trait_map.values())

    def get_trait_by_name(self, name: str) -> Trait:
        """Get a trait using it's name."""
        uid = self._name_to_uid_map[name]
        return self._uid_to_trait_map[uid]

    def get_trait_by_uid(self, uid: int) -> Trait:
        """Get a trait using its UID."""
        return self._uid_to_trait_map[uid]

    def add_trait(self, trait: Trait) -> None:
        """Add a trait to the database."""
        trait.uid = self._next_trait_uid
        self._next_trait_uid += 1
        self._uid_to_trait_map[trait.uid] = trait
        self._name_to_uid_map[trait.name] = trait.uid
