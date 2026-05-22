from app.config import MODEL_NAME


class LLMClient:
    def __init__(self):
        self.model_name = MODEL_NAME

    def generate_response(self, prompt: str) -> str:
        """
        Sends prompt to model and returns AI response.
        """

        # TEMPORARY MOCK RESPONSE
        # We will replace this with real Antigravity inference next.
        
        return f"[MOCK AI RESPONSE from {self.model_name}] -> {prompt}"