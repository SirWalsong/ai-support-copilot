from google import genai
from google.genai import types

from app.config import GOOGLE_API_KEY, MODEL_NAME
from app.agent_tools import update_ticket_status, add_internal_note, escalate_ticket


class LLMClient:
    def __init__(self):
        # Initialize the modern google-genai Client
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_name = MODEL_NAME

    def generate_response(self, prompt: str) -> str:
        """
        Generate a one-shot response (backward compatible).
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def create_chat_session(self, system_instruction: str, history=None):
        """
        Initialize a stateful conversational chat session with Gemini,
        loaded with the system instruction and registered agent tools.
        """
        try:
            # Configure tools and system instructions
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                # In google-genai, passing python functions in the tools list
                # automatically sets up local execution/function calling!
                tools=[update_ticket_status, add_internal_note, escalate_ticket],
                temperature=0.2  # Lower temperature for more consistent tool execution
            )

            # Create a chat session with the provided model, configuration, and optional history
            chat = self.client.chats.create(
                model=self.model_name,
                config=config,
                history=history
            )

            return chat
        except Exception as e:
            print(f"Error creating chat session: {str(e)}")
            raise e