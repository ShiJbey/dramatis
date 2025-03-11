from __future__ import annotations

from typing import Iterable, Optional

from dramatis.ai import Proclivity


class Status:
    """A status associated with a character."""

    __slots__ = ("uid", "name", "proclivities", "duration")

    uid: int
    """The unique ID of this status."""
    name: str
    """The name of this status."""
    proclivities: list[Proclivity]
    """Proclivities added to the character when this status is attached."""
    duration: int
    """The max amount of time this status lasts."""

    def __init__(
        self,
        name: str,
        duration: int,
        proclivities: Optional[Iterable[Proclivity]] = None,
    ) -> None:
        self.uid = -1
        self.name = name
        self.duration = duration
        self.proclivities = list(proclivities) if proclivities else []


class StatusDatabase:
    """The database of all statuses defined for a story world."""

    __slots__ = ("_uid_to_status_map", "_name_to_uid_map", "_next_status_uid")

    _next_status_uid: int
    """The UID assigned to the next status in the database."""
    _uid_to_status_map: dict[int, Status]
    """Status UIDs mapped to status instances."""
    _name_to_uid_map: dict[str, int]
    """Status names mapped to UIDs."""

    def __init__(self) -> None:
        self._next_status_uid = 1
        self._uid_to_status_map = {}
        self._name_to_uid_map = {}

    def get_statuses(self) -> list[Status]:
        """Get all statuses in the database."""
        return list(self._uid_to_status_map.values())

    def get_status_by_name(self, name: str) -> Status:
        """Get a status using it's name."""
        uid = self._name_to_uid_map[name]
        return self._uid_to_status_map[uid]

    def get_status_by_uid(self, uid: int) -> Status:
        """Get a status using its UID."""
        return self._uid_to_status_map[uid]

    def add_status(self, status: Status) -> None:
        """Add a status to the database."""
        status.uid = self._next_status_uid
        self._next_status_uid += 1
        self._uid_to_status_map[status.uid] = status
        self._name_to_uid_map[status.name] = status.uid
