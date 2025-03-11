from dramatis import ecs
from dramatis.ai import SocialPracticeContext


class Character(ecs.Component):
    """A character in a story world."""

    __slots__ = (
        "uid",
        "name",
        "traits",
        "statuses",
        "location",
        "is_player",
        "practices",
    )

    uid: int
    """The unique ID of the character."""
    name: str
    """The name of the character."""
    traits: set[int]
    """The traits attached to this character."""
    statuses: dict[int, int]
    """Status IDs mapped to the timeout times for a status."""
    location: int
    """The ID of the location where this character is. (No location = -1)"""
    is_player: bool
    """Is this character controlled by a player."""
    practices: list[SocialPracticeContext]
    """Social Practices this character belongs to."""

    def __init__(
        self,
        uid: int,
        name: str,
        is_player: bool = False,
    ) -> None:
        super().__init__()
        self.uid = uid
        self.name = name
        self.traits = set()
        self.statuses = {}
        self.location = -1
        self.is_player = is_player
        self.practices = []


class Location(ecs.Component):
    """A location in the story world."""

    __slots__ = ("uid", "name", "characters")

    uid: int
    """The unique ID of the location."""
    name: str
    """The name of the location."""
    characters: list[int]
    """IDs of characters currently at this location."""

    def __init__(self, uid: int, name: str) -> None:
        super().__init__()
        self.uid = uid
        self.name = name
        self.characters = []
