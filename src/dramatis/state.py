"""Story World State Data."""

import random
import sqlite3
from typing import Iterable

from drolta.engine import QueryEngine

from dramatis import ecs
from dramatis.ai import (
    Action,
    ActionDatabase,
    ActionTagDatabase,
    Goal,
    GoalDatabase,
    SocialPractice,
    SocialPracticeContext,
    SocialPracticeDatabase,
)
from dramatis.entities import Character, Location
from dramatis.errors import InvalidTagError
from dramatis.statuses import Status, StatusDatabase
from dramatis.traits import Trait, TraitDatabase

_DB_CONFIG = """

DROP TABLE IF EXISTS characters;
DROP TABLE IF EXISTS relationships;
DROP TABLE IF EXISTS relationship_tags;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS traits;
DROP TABLE IF EXISTS statuses;

CREATE TABLE Characters (
    uid INT NOT NULL PRIMARY KEY,
    name TEXT,
    location INT,
    FOREIGN KEY (location) REFERENCES Locations(uid)
) STRICT;

CREATE TABLE Relationships (
    owner INT NOT NULL,
    target INT NOT NULL,
    opinion INT NOT NULL,
    attraction INT NOT NULL,
    PRIMARY KEY (owner, target)
) STRICT;


CREATE TABLE RelationshipTags (
    uid INT NOT NULL,
    tag TEXT NOT NULL,
    FOREIGN KEY (uid) REFERENCES Relationships(uid)
) STRICT;


CREATE TABLE Locations (
    uid INT NOT NULL PRIMARY KEY,
    name TEXT
) STRICT;

CREATE TABLE Traits (
    uid INT NOT NULL,
    trait TEXT NOT NULL,
    FOREIGN KEY (uid) REFERENCES Characters(uid)
) STRICT;

CREATE TABLE Statuses (
    uid INT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (uid) REFERENCES Characters(uid)
) STRICT;
"""


class StoryWorldState:
    """Manages the state of the simulation."""

    __slots__ = (
        "trait_db",
        "status_db",
        "sql_db",
        "action_tag_db",
        "action_db",
        "social_practice_db",
        "goal_db",
        "ecs_world",
        "world_seed",
        "rng",
        "default_location",
        "is_initialized",
        "global_practice_names",
        "global_practices",
        "active_practices",
        "query_engine",
        "is_running",
    )

    action_tag_db: ActionTagDatabase
    """All tags defined for action."""
    trait_db: TraitDatabase
    """All database defined for this simulation."""
    status_db: StatusDatabase
    """All statuses defined for this simulation."""
    action_db: ActionDatabase
    """All the action registered with the simulation."""
    social_practice_db: SocialPracticeDatabase
    """All the social practices registered with the simulation."""
    goal_db: GoalDatabase
    """All the goals registered with the simulation."""
    sql_db: sqlite3.Connection
    """SQLite database connection."""
    ecs_world: ecs.World
    """The ECS that manages all the entities in the world."""
    world_seed: str
    """The seed used by the random number generator."""
    rng: random.Random
    """A random number generator instance."""
    default_location: int
    """The default starting location for all characters."""
    is_initialized: bool
    """Has the simulation already started."""
    global_practice_names: list[str]
    """Names of all global practices."""
    global_practices: list[SocialPracticeContext]
    """Instances of all the global practices."""
    active_practices: list[SocialPracticeContext]
    """Practices currently active."""
    query_engine: QueryEngine
    """Query engine for precondition queries."""
    is_running: bool
    """IS the game currently running."""

    def __init__(self, world_seed: str = "", sql_path: str = ":memory:") -> None:
        self.trait_db = TraitDatabase()
        self.status_db = StatusDatabase()
        self.action_tag_db = ActionTagDatabase()
        self.action_db = ActionDatabase()
        self.social_practice_db = SocialPracticeDatabase()
        self.goal_db = GoalDatabase()
        self.sql_db = sqlite3.Connection(sql_path)
        self.sql_db.executescript(_DB_CONFIG)
        self.sql_db.commit()
        self.ecs_world = ecs.World()
        self.world_seed = world_seed if world_seed else str(random.randint(0, 999_999))
        self.rng = random.Random(self.world_seed)
        self.default_location = -1
        self.is_initialized = False
        self.global_practice_names = []
        self.global_practices = []
        self.active_practices = []
        self.query_engine = QueryEngine()
        self.is_running = False

    def character(self, name: str, is_player: bool) -> int:
        """Add a new character to the simulation."""
        character = self.ecs_world.entity()
        character.name = name
        character.add_component(Character(character.uid, name, is_player=is_player))

        cursor = self.sql_db.cursor()
        cursor.execute(
            "INSERT INTO Characters (uid, name) VALUES (?, ?);",
            (character.uid, name),
        )
        self.sql_db.commit()
        cursor.close()

        return character.uid

    def location(self, name: str, is_default: bool = False) -> int:
        """Add a new location to the simulation."""
        location = self.ecs_world.entity()
        location.name = name
        location.add_component(Location(location.uid, name))

        cursor = self.sql_db.cursor()
        cursor.execute(
            "INSERT INTO Locations (uid, name) VALUES (?, ?);",
            (location.uid, name),
        )
        self.sql_db.commit()
        cursor.close()

        if is_default:
            self.default_location = location.uid

        return location.uid

    def register_trait(self, trait: Trait) -> None:
        """Register a trait with the simulation."""
        self.trait_db.add_trait(trait)

    def register_status(self, status: Status) -> None:
        """Register a status with the simulation."""
        self.status_db.add_status(status)

    def register_action_tags(self, tags: Iterable[str]) -> None:
        """Register the given tags with the simulation."""
        for t in tags:
            self.action_tag_db.add_tag(t)

    def register_social_practice(self, social_practice: SocialPractice) -> None:
        """Register a social practice definition with the simulation."""
        self.social_practice_db.add_practice(social_practice)
        if social_practice.is_global:
            self.global_practice_names.append(social_practice.name)

    def register_action(self, action: Action) -> None:
        """Register an action definition with the simulation."""
        # Validate the tags in the action
        for tag in action.tags:
            if self.action_tag_db.tag_exists(tag) is False:
                raise InvalidTagError(tag)

        self.action_db.add_action(action)

    def register_goal(self, goal: Goal) -> None:
        """Register a goal definition with the simulation."""
        self.goal_db.add_goal(goal)

    def define_sifting_rules(self, drolta_script: str) -> None:
        """Define query rules and aliases."""
        self.query_engine.execute_script(drolta_script)
