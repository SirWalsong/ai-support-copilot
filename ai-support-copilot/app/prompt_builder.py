from pathlib import Path


PROMPTS_DIR = Path("prompts")


class PromptBuilder:
    @staticmethod
    def load_prompt(prompt_file: str, ticket: str) -> str:
        """
        Load prompt template and inject ticket content.
        """

        prompt_path = PROMPTS_DIR / prompt_file

        with open(prompt_path, "r", encoding="utf-8") as file:
            template = file.read()

        return template.format(ticket=ticket)