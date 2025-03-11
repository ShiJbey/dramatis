from __future__ import annotations

import random
from typing import Iterable
import logging

from dramatis.ai import (
    Action,
    ActionContext,
    Goal,
    SocialPractice,
    SocialPracticeContext,
)
from dramatis.entities import Character, Location
from dramatis.state import StoryWorldState
from dramatis.statuses import Status
from dramatis.traits import Trait


_logger = logging.getLogger(__name__)


def move_character_to_location(
    state: StoryWorldState, character_id: int, location_id: int
) -> None:
    """Move a character to a given location.

    Parameters
    ----------
    character_id:
        The UID of the character.
    location_id:
        The UID of the location.
    """

    character_comp = state.ecs_world.get_entity(character_id).get_component(Character)

    # Remove from any existing location
    if character_comp.location != -1:
        current_location_comp = state.ecs_world.get_entity(
            character_comp.location
        ).get_component(Location)

        character_comp.location = -1
        current_location_comp.characters.remove(character_id)

    # Add to the new location
    if location_id != -1:
        location_comp = state.ecs_world.get_entity(location_id).get_component(Location)

        character_comp.location = location_id
        location_comp.characters.append(character_id)

    # Update the SQL database
    cursor = state.sql_db.cursor()
    cursor.execute(
        "UPDATE Characters SET location=? WHERE uid=?;", (location_id, character_id)
    )
    state.sql_db.commit()
    cursor.close()


class _ProclivityScores:
    """Results of a proclivity calculation."""

    __slots__ = ("actions", "weights")

    actions: list[ActionContext]
    weights: list[int]

    def __init__(self, actions: list[ActionContext], weights: list[int]) -> None:
        self.actions = actions
        self.weights = weights


class StoryWorld:
    """Manages the state of the simulation.

    The StoryWorld class is the main entry point for managing a simulation.
    """

    __slots__ = ("state",)

    state: StoryWorldState

    def __init__(self, world_seed: str = "", sql_path: str = ":memory:") -> None:
        self.state = StoryWorldState(world_seed, sql_path)

    def character(self, name: str, is_player: bool = False) -> int:
        """Add a new character to the simulation."""
        return self.state.character(name, is_player)

    def location(self, name: str, is_default: bool = False) -> int:
        """Add a new location to the simulation."""
        return self.state.location(name, is_default)

    def register_trait(self, trait: Trait) -> None:
        """Register a trait with the simulation."""
        self.state.register_trait(trait)

    def register_status(self, status: Status) -> None:
        """Register a status with the simulation."""
        self.state.register_status(status)

    def register_action_tags(self, tags: Iterable[str]) -> None:
        """Register the given tags with the simulation."""
        self.state.register_action_tags(tags)

    def register_social_practice(self, social_practice: SocialPractice) -> None:
        """Register a social practice definition with the simulation."""
        self.state.register_social_practice(social_practice)

    def register_action(self, action: Action) -> None:
        """Register an action definition with the simulation."""
        self.state.register_action(action)

    def register_goal(self, goal: Goal) -> None:
        """Register a goal definition with the simulation."""
        self.state.register_goal(goal)

    def define_sifting_rules(self, drolta_script: str) -> None:
        """Define query rules and aliases."""
        self.state.define_sifting_rules(drolta_script)

    def step(self) -> None:
        """Tick the simulation one turn/time step."""

        if self.state.is_initialized is False:
            self._initialize_characters()
            self.state.is_initialized = True

        self._update_statuses()
        self._perform_character_actions()

    def run(self) -> None:
        """Run the simulation until the player exits or game reaches end-state."""
        self.state.is_running = True

        while self.state.is_running:
            self.step()

    def _initialize_global_practices(self) -> None:
        """Initialize global practices."""

        for name in self.state.global_practice_names:
            practice = self.state.social_practice_db.get_practice(name)
            practice_instance = SocialPracticeContext(practice)
            self.state.active_practices.append(practice_instance)
            self.state.global_practices.append(practice_instance)

    def _initialize_characters(self) -> None:
        """Place characters at locations and add them to practices."""
        if self.state.default_location == -1:
            raise RuntimeError("Default location not provided.")

        for _, (character_comp,) in self.state.ecs_world.query_components((Character,)):
            # Move to default location if not already places somewhere
            if character_comp.location == -1:
                move_character_to_location(
                    self.state, character_comp.uid, self.state.default_location
                )

            for practice in self.state.global_practices:
                practice.participants.append(character_comp.uid)

    def _update_statuses(self) -> None:
        """Update the state of all character's statuses."""
        for _, (character_comp,) in self.state.ecs_world.query_components((Character,)):
            for status_id, time_left in character_comp.statuses.items():
                if time_left == 0:
                    del character_comp.statuses[status_id]
                else:
                    character_comp.statuses[status_id] = time_left - 1

    def _perform_character_actions(self) -> None:
        """Characters perform their actions for this turn."""

        characters = list(self.state.ecs_world.query_components((Character,)))

        random.shuffle(characters)

        for _, (character_comp,) in characters:
            if character_comp.is_player:
                StoryWorld._handle_player_action_selection(self.state, character_comp)
            else:
                StoryWorld._handle_npc_action_selection(self.state, character_comp)

    @staticmethod
    def _handle_player_action_selection(
        state: StoryWorldState, character: Character
    ) -> None:
        """Player performs an action."""

        print(f"{character.name}'s turn:")
        input("What would you like to do? >> ")

        _logger.info("%s performed a player action.", character.name)

    @staticmethod
    def _handle_npc_action_selection(
        state: StoryWorldState, character: Character
    ) -> None:
        """NPC performs an action."""
        potential_actions: dict[int, Action] = {}

        StoryWorld._get_actions_from_goals(state, character, potential_actions)

        StoryWorld._get_actions_from_practices(state, character, potential_actions)

        if len(potential_actions) == 0:
            _logger.info("%s has no actions to perform.", character.name)
            return

        proclivity_scores = StoryWorld._get_proclivity_scores(
            state, character, potential_actions
        )

        chosen_action = state.rng.choices(
            population=proclivity_scores.actions,
            weights=proclivity_scores.weights,
            k=1,
        )[0]

        chosen_action.execute()

    @staticmethod
    def _get_actions_from_goals(
        state: StoryWorldState,
        character: Character,
        potential_actions: dict[int, Action],
    ) -> None:
        """Get potential actions from this character's goals."""
        return

    @staticmethod
    def _get_actions_from_practices(
        state: StoryWorldState,
        character: Character,
        potential_actions: dict[int, Action],
    ) -> None:
        """Get potential actions from this character's social practices."""
        return

    @staticmethod
    def _get_proclivity_scores(
        state: StoryWorldState,
        character: Character,
        potential_actions: dict[int, Action],
    ) -> _ProclivityScores:
        """Calculate the proclivity of each action."""
        return _ProclivityScores([], [])


class StoryWorldRepl:
    """Provides a REPL interface to players."""

    def run(self, story_world: StoryWorld) -> None:
        """Run the repl to get user input."""
