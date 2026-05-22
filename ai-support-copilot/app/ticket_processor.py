from app.llm_client import LLMClient
from app.prompt_builder import PromptBuilder


class TicketProcessor:
    def __init__(self):
        self.client = LLMClient()

    def process_ticket(self, ticket: str):
        """
        Run complete AI workflow pipeline.
        """

        summarize_prompt = PromptBuilder.load_prompt(
            "summarize_prompt.txt",
            ticket
        )

        sentiment_prompt = PromptBuilder.load_prompt(
            "sentiment_prompt.txt",
            ticket
        )

        urgency_prompt = PromptBuilder.load_prompt(
            "urgency_prompt.txt",
            ticket
        )

        response_prompt = PromptBuilder.load_prompt(
            "response_prompt.txt",
            ticket
        )

        summary = self.client.generate_response(summarize_prompt)

        sentiment = self.client.generate_response(sentiment_prompt)

        urgency = self.client.generate_response(urgency_prompt)

        support_response = self.client.generate_response(response_prompt)

        return {
            "summary": summary,
            "sentiment": sentiment,
            "urgency": urgency,
            "support_response": support_response
        }