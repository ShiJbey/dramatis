"""Dramatis Error classes."""


class InvalidTagError(Exception):
    """Exception raised when an invalid tag is associated with an action."""

    def __init__(self, tag: str) -> None:
        self.message = f"'{tag}' is not a registered tag."
        super().__init__(self.message)
