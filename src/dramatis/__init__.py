"""Dramatis

Dramatis is a simple social simulation framework for for simulationist story telling.
It handles all the complexities of character AI and decision making, allowing the user
to focus on creating character behaviors. Dramatis adapts much of it's design from
previous simulationist storytelling tools such as Versu, Comme il Faut, Kismet,
Ensemble, and Neighborly (See the main repository for references to each).

"""

__version__ = "0.1.0"

from .ai import (
    Action,
    ActionContext,
    Goal,
    Proclivity,
    SocialPractice,
    SocialPracticeContext,
)
from .statuses import Status
from .story_world import StoryWorld
from .traits import Trait

__all__ = [
    "StoryWorld",
    "SocialPractice",
    "SocialPracticeContext",
    "Action",
    "ActionContext",
    "Goal",
    "Proclivity",
    "Trait",
    "Status",
]
