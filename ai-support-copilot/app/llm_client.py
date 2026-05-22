from google import genai

from app.config import GOOGLE_API_KEY, MODEL_NAME


class LLMClient:
    def __init__(self):
        self.client = genai.Client(api_key=GOOGLE_API_KEY)

        self.model_name = MODEL_NAME

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

            return response.text

        except Exception as e:
            return f"Error generating response: {str(e)}"