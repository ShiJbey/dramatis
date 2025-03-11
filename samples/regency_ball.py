"""Dramatis: Regency Ball Sample

This script implement a regency ball simulation inspired by Netflix's Bridgerton series.

"""

import logging

import dramatis


class RegencyBallSocialPractice(dramatis.SocialPractice):
    """The global social practice available to all characters."""

    def __init__(self) -> None:
        super().__init__(
            name="RegencyBall",
            description="There is a ball happening",
            actions=["mingle", "flirt", "stand_awkwardly", "dance", "eat"],
            is_global=True,
        )

    def is_valid(self, ctx: dramatis.SocialPracticeContext) -> bool:
        return True


class MingleAction(dramatis.Action):
    """A character just stands idle."""

    def __init__(self) -> None:
        super().__init__(
            name="mingle",
            description="[performer] is mingling with [recipient]",
            tags=["social"],
            conditions="",
        )

    def execute(self, ctx: dramatis.ActionContext) -> None:
        # subject = ctx["subject"]
        # target = ctx["target"]
        # ctx.storyworld.modify_opinion(subject, target, 1)
        # ctx.storyworld.modify_opinion(target, subject, 1)
        pass


class FlirtAction(dramatis.Action):
    """A character just stands idle."""

    def __init__(self) -> None:
        super().__init__(
            name="flirt",
            description="[performer] is flirting with [recipient]",
            tags=["social", "romance"],
            conditions="",
        )

    def execute(self, ctx: dramatis.ActionContext) -> None:
        return


class StandAwkwardlyAction(dramatis.Action):
    """A character just stands idle."""

    def __init__(self) -> None:
        super().__init__(
            name="stand_awkwardly",
            description="[performer] is standing awkwardly.",
            tags=[],
            conditions="",
        )

    def execute(self, ctx: dramatis.ActionContext) -> None:
        return


class DanceAction(dramatis.Action):
    """A character just stands idle."""

    def __init__(self) -> None:
        super().__init__(
            name="dance",
            description="[performer] is dancing.",
            tags=["social", "dance"],
            conditions="",
        )

    def execute(self, ctx: dramatis.ActionContext) -> None:
        return


class EatAction(dramatis.Action):
    """A character eats food."""

    def __init__(self) -> None:
        super().__init__(
            name="eat",
            description="[performer] is eating",
            tags=["food"],
            conditions="",
        )

    def execute(self, ctx: dramatis.ActionContext) -> None:
        return


def main() -> None:
    """Main function."""

    # Logging for console prints and debugging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        force=True,
    )

    # (1) The first thing you need to do is create a new StoryWorld instance.
    # This will manage the entire simulation, including characters, and
    # locations. For this simulation, let's model characters interacting at
    # a regency ball.

    regency_ball = dramatis.StoryWorld()

    regency_ball.register_action_tags(
        ["social", "food", "drink", "nothing", "romance", "dance"]
    )

    # The function below adds new Drolta story query rules to the simulation to
    # help with action definitions, social inference rules, and story-sifting.
    regency_ball.define_sifting_rules(
        """
        -- DEFINE DROLTA RULE(S) HERE
        """
    )

    # We need to give characters some things to do while at the ball.
    # Lets add some actions for mingling, flirting, standing awkwardly, dancing, eating.

    regency_ball.register_social_practice(RegencyBallSocialPractice())
    regency_ball.register_action(MingleAction())
    regency_ball.register_action(FlirtAction())
    regency_ball.register_action(StandAwkwardlyAction())
    regency_ball.register_action(DanceAction())
    regency_ball.register_action(EatAction())

    regency_ball.register_trait(
        dramatis.Trait(
            name="extrovert",
            conflicting_traits=["introvert"],
            proclivities=[
                dramatis.Proclivity(3).where(lambda ctx: "social" in ctx.action.tags),
                dramatis.Proclivity(3).where(lambda ctx: "dance" in ctx.action.tags),
            ],
        )
    )

    regency_ball.register_trait(
        dramatis.Trait(
            name="introvert",
            conflicting_traits=["extrovert"],
            proclivities=[
                dramatis.Proclivity(-3).where(lambda ctx: "social" in ctx.action.tags),
                dramatis.Proclivity(-3).where(lambda ctx: "dance" in ctx.action.tags),
            ],
        )
    )

    regency_ball.register_trait(
        dramatis.Trait(
            name="hopeless-romantic",
            proclivities=[
                dramatis.Proclivity(3).where(lambda ctx: "romance" in ctx.action.tags),
            ],
        )
    )

    # Now, let's add a few characters to the mix

    regency_ball.character("Alice")
    regency_ball.character("Jabari")
    regency_ball.character("Cassidy")
    regency_ball.character("Terry")
    regency_ball.character("Wynn")
    regency_ball.character("Ridley")
    regency_ball.character("Avery")
    regency_ball.character("Morgan")
    regency_ball.character("Drew")

    regency_ball.location("Rose Garden")
    regency_ball.location("Dance Hall", is_default=True)
    regency_ball.location("Balcony")
    regency_ball.location("Library")

    # Step the simulation for 100 turns
    num_turns = 100
    for _ in range(num_turns):
        regency_ball.step()


if __name__ == "__main__":
    main()
