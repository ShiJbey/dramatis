"""Dramatis Helper Functions."""

from __future__ import annotations

from dramatis.state import StoryWorldState


def modify_opinion(
    state: StoryWorldState, subject_id: int, target_id: int, amount: int
) -> None:
    """Change the opinion from the subject to the target by a given amount."""
    return


def set_opinion(
    state: StoryWorldState, subject_id: int, target_id: int, value: int
) -> None:
    """Set the opinion from the subject to the target to a given value."""
    return


def modify_attraction(
    state: StoryWorldState, subject_id: int, target_id: int, amount: int
) -> None:
    """Change the attraction from the subject to the target by a given amount."""
    return


def set_attraction(
    state: StoryWorldState, subject_id: int, target_id: int, value: int
) -> None:
    """Set the attraction from the subject to the target to a given value."""
    return
