from typing import Optional
import inquirer  # type: ignore


def action_prompt(actions: list[str], page_size: int = 5) -> Optional[str]:
    """Prompts player to select an action from the list."""
    current_page = 0

    while True:
        list_offset = page_size * current_page

        choices = actions[list_offset : list_offset + page_size]

        if current_page > 0:
            choices.append("<Prev Page>")

        if list_offset + page_size < len(actions):
            choices.append("<Next Page>")

        choices.append("<Exit>")

        questions = [
            inquirer.List(
                name="choice",
                message="What do you want to do?",
                choices=choices,
            )
        ]

        choice = inquirer.prompt(questions)["choice"]  # type: ignore

        if choice == "<Prev Page>":
            current_page -= 1
            continue
        elif choice == "<Next Page>":
            current_page += 1
            continue
        elif choice == "<Exit>":
            return None
        else:
            return choice  # type: ignore


def main() -> None:
    """."""

    while True:
        questions = [
            inquirer.List(
                name="choice",
                message="What do you want to do?",
                choices=[
                    "List Active Practices",
                    "List Actions",
                    "<Pass>",
                ],
            )
        ]

        choice = inquirer.prompt(questions)["choice"]  # type: ignore

        if choice == "<Pass>":
            print("Player passes turn.")
            return

        elif choice == "List Actions":
            choice = action_prompt(
                [
                    "Mingle",
                    "Flirt",
                    "Stand Awkwardly",
                    "Dance",
                    "Eat",
                ],
                page_size=2,
            )

            if choice == None:
                pass
            else:
                print(f"Player chose to {choice}.")

        elif choice == "List Active Practices":

            print("Regency Ball")


if __name__ == "__main__":
    main()
