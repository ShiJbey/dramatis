# Dramatis: A simple agent-based social sim engine for Python

Dramatis is a simplified social simulation engine I made for a late-stage dissertation project. It provides Python classes and functions to build micro-story-worlds where characters interact with each other, and navigate social relationships.

It is designed to be a very simple. You cannot embody any particular character. The output of the simulation is provided as a SQLite database file and a text log containing descriptions of all events that have occurred.

It takes modeling lessons from both of my previous social sim projects ([Minerva](https://github.com/ShiJbey/minerva) and [Neighborly](https://github.com/ShiJbey/neighborly)) and gives users a much simpler sandbox to work with. This project is borrows adapts its core mechanics from [Kismet](https://github.com/adamsumm/Kismet), a specialized language/engine for social simulation.

## Installation

You can install Dramatis directly from GitHub.

```bash
pip install git+https://github.com/ShiJbey/dramatis.git
```

## Getting Started

```python
import enum
import dramatis

# (1) The first thing you need to do is create a new StoryWorld instance.
# This will manage the entire simulation, including characters, and
# locations. For this simulation, let's model characters interacting at
# a house party.

house_party = dramatis.StoryWorld()

# (2) Now let's add a few characters to the mix

alice = house_party.character("Alice")
jabari = house_party.character("Jabari")
cassidy = house_party.character("Cassidy")
terry = house_party.character("Terry")
wynn = house_party.character("Wynn")
ridley = house_party.character("Ridley")
avery = house_party.character("Avery")
morgan = house_party.character("Morgan")
drew = house_party.character("Drew")

# (3) So, we have characters, but there isn't anything for them to do.
# By default, Dramatis includes an idle action that characters can choose.
# We need to add actions they can perform while attending this house
# party. Lets add some actions for mingling, flirting, playing beer
# pong, standing awkwardly, dancing, eating.

# The function below defines new action tags that can be associated with
# actions. If a tag is used and not defined first, you will get an error.
# If you want to list all tags currently defined, use the .list_action_tags()
# method on the StoryWorld class.
house_party.define_action_tags(["socialize", "food", "drink"])

# You can call define_action_tags() multiple times to add new tags
house_party.define_action_tags(["activity", "alcohol"])

# The function below adds new Drolta story query rules to the simulation to
# help with action definitions, social inference rules, and story-sifting.
house_party.define_sifting_rules(
"""
-- DEFINE DROLTA RULE(S) HERE
"""
)

class MingleAction(dramatis.Action):
    """An action where two characters talk to each other."""

    def __init__(self) -> None:


house_party.add_action(MingleAction())
house_party.add_action(FlirtAction())
house_party.add_action(BeerPongAction())
house_party.add_action(StandAwkwardlyAction())
house_party.add_action(DanceAction())
house_party.add_action(EatAction())
house_party.add_action(DrinkAction())
```

## Documentation

All public-facing classes and methods come with full documentation in Python. Your IDE should automatically display tooltips about arguments and class descriptions. Dramatis uses

### StoryWorld

The storyworld class is the main entry point for managing a simulation.

### Actions

Actions have the following fields that must be supplied:

- `description`: A textual description of the action. Each action has a subject, target. You can substitute their names into the description. For example, `"[subject] flirted with [target]."`. This description is used by the simulation to create the final event descriptions in the event logs.
- `cooldown`: The amount of time that must pass between concurrent selection of this action for the character(s) involved.
- `required_time`: The amount of time required for an action to complete.
- `tags`: Tags associated with an action.

```python
import dramatis
import drolta   # Drolta handles story patterns.

class IdleAction(dramatis.Action):
    """A character does nothing"""

    def __init__(self) -> None:
        super().__init__(
            name="idle",
            description="[subject] is idle.",
            cooldown=0,
            required_time=0,
            tags=[],
        )


class MingleAction(dramatis.Action):
    """Two character's have a simple chat."""

    def __init__(self) -> None:
        super().__init__(
            name="mingle",
            description="[subject] and [target] are having chatting",
            cooldown=1,
            required_time=2,
            tags=["socialize"],
            query="""
            FIND ?subject, ?target
            WHERE
                character(id=?subject)
                character(id=?target)
                (?subject != ?target);
            """,
        )

    def execute(ctx: dramatis.ActionContext) -> None:
        subject = ctx["subject"]
        target = ctx["target"]
        ctx.storyworld.modify_opinion(subject, target, 1)
        ctx.storyworld.modify_opinion(target, subject, 1)

mingle = dramatis.Action(MingleAction())
```
