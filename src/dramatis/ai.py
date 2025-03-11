from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Iterable, Optional


class ActionContext:
    """Contextual information about an instance of an action."""

    initiator: int
    recipient: int
    subject: int
    location: Optional[int]
    action: Action
    practice: SocialPracticeContext

    def __init__(
        self,
        initiator: int,
    ) -> None:
        self.initiator = initiator

    def execute(self) -> None:
        """Execute the action instance."""
        self.action.execute(self)


class SocialPracticeContext:
    """Contextual information about an instance of a social practice."""

    parent: Optional[SocialPracticeContext]
    practice: SocialPractice
    participants: list[int]

    def __init__(
        self,
        practice: SocialPractice,
        participants: Optional[list[int]] = None,
        parent: Optional[SocialPracticeContext] = None,
    ) -> None:
        self.practice = practice
        self.participants = list(participants) if participants else []
        self.parent = parent


class Proclivity:
    """A consideration function for characters taking actions."""

    __slots__ = ("score", "conditions")

    score: int
    """The score to return if the proclivity applies."""
    conditions: list[Callable[[ActionContext], bool]]
    """Conditions that must pass for the score to be returned."""

    def __init__(self, score: int) -> None:
        self.score = score
        self.conditions = []

    def where(self, condition: Callable[[ActionContext], bool]) -> Proclivity:
        """Add a condition to a proclivity."""
        self.conditions.append(condition)
        return self

    def check_preconditions(self, ctx: ActionContext) -> bool:
        """Check if the preconditions pass."""
        return all(cond(ctx) for cond in self.conditions)


class ActionTagDatabase:
    """Manages all valid tags for actions."""

    __slots__ = ("_uid_to_tag_map", "_tag_to_uid_map", "_next_tag_uid")

    _next_tag_uid: int
    """The UID associated with the next tag added to the database."""
    _uid_to_tag_map: dict[int, str]
    """Maps UIDs to text tags."""
    _tag_to_uid_map: dict[str, int]
    """Maps tags to UIDs."""

    def __init__(self) -> None:
        self._next_tag_uid = 1
        self._uid_to_tag_map = {}
        self._tag_to_uid_map = {}

    def get_tags(self) -> list[str]:
        """List all the tags in the database."""
        return list(self._uid_to_tag_map.values())

    def get_tag_by_uid(self, uid: int):
        """Get a tag using its UID."""
        return self._uid_to_tag_map[uid]

    def tag_exists(self, tag: str) -> bool:
        """Check if the given tag is in the database."""
        return tag in self._tag_to_uid_map

    def get_tag_uid(self, tag: str) -> int:
        """Get the UID for a given tag."""
        return self._tag_to_uid_map[tag]

    def add_tag(self, tag: str) -> None:
        """Add a new tag to the database."""
        self._uid_to_tag_map[self._next_tag_uid] = tag
        self._tag_to_uid_map[tag] = self._next_tag_uid
        self._next_tag_uid += 1


class Action(ABC):
    """An action taken by a character.

    Parameters
    ----------
    name:
        A unique name assigned to this action.
    description:
        A textual description of the action. Each action has a subject, target. You can
        substitute their names into the description. For example, `"[subject] flirted
        with [target]."`. This description is used by the simulation to create the final
        event descriptions in the event logs.
    tags:
        Tags associated with an action.
    conditions:
        Where-clauses for a Drolta query to see if this action is available.
    """

    __slots__ = ("name", "description", "tags", "conditions")

    name: str
    """The name of this action."""
    description: str
    """A template string with the description text."""
    tags: set[str]
    """A collection of tags associated with this action."""
    conditions: str
    """Preconditions for this action."""

    def __init__(
        self, name: str, description: str, tags: Iterable[str], conditions: str
    ) -> None:
        self.name = name
        self.description = description
        self.tags = set(tags)
        self.conditions = conditions

    @abstractmethod
    def execute(self, ctx: ActionContext) -> None:
        """Execute the action."""
        raise NotImplementedError()


class ActionDatabase:
    """Manages a database of actions registered with a simulation."""

    __slots__ = ("_name_to_action_map",)

    _name_to_action_map: dict[str, Action]

    def __init__(self) -> None:
        self._name_to_action_map = {}

    def add_action(self, action: Action) -> None:
        """Add an action to the database."""
        self._name_to_action_map[action.name] = action

    def get_action(self, name: str) -> Action:
        """Get an action from the database."""
        return self._name_to_action_map[name]


class SocialPractice(ABC):
    """A social context that provides action suggestions to characters."""

    __slots__ = ("name", "description", "actions", "is_global")

    name: str
    """The unique name of this social practice."""
    description: str
    """A description template for this practice."""
    actions: list[str]
    """Actions available within this practice."""
    is_global: bool
    """Is this practice always present and available to all characters."""

    def __init__(
        self, name: str, description: str, actions: list[str], is_global: bool = False
    ) -> None:
        self.name = name
        self.description = description
        self.actions = actions
        self.is_global = is_global

    @abstractmethod
    def is_valid(self, ctx: SocialPracticeContext) -> bool:
        """Check if a social practice is valid."""
        raise NotImplementedError()


class SocialPracticeDatabase:
    """Manages a database of social practices registered with a simulation"""

    __slots__ = ("_name_to_practice_map",)

    _name_to_practice_map: dict[str, SocialPractice]

    def __init__(self) -> None:
        self._name_to_practice_map = {}

    def add_practice(self, social_practice: SocialPractice) -> None:
        """Add a social practice to the database."""
        self._name_to_practice_map[social_practice.name] = social_practice

    def get_practice(self, name: str) -> SocialPractice:
        """Get a practice from the database."""
        return self._name_to_practice_map[name]


class Goal(SocialPractice, ABC):
    """A special type of social practice representing a character's want."""

    def __init__(self, name: str, description: str, actions: list[str]) -> None:
        super().__init__(name, description, actions)


class GoalDatabase:
    """Manages a database of goals registered with a simulation."""

    __slots__ = ("_name_to_goal_map",)

    _name_to_goal_map: dict[str, Goal]

    def __init__(self) -> None:
        self._name_to_goal_map = {}

    def add_goal(self, goal: Goal) -> None:
        """Add a goal to the database."""
        self._name_to_goal_map[goal.name] = goal
