from app.ai.provider_base import AIProvider
from app.core.config import GROQ_API_KEY
from groq import Groq


class GroqClient(AIProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GROQ_API_KEY
        if not self.api_key:
            self.client = None
            print("WARNING: GROQ_API_KEY not set")
        else:
            self.client = Groq(api_key=self.api_key)

        # Use llama3-70b-8192 as default for complex reasoning
        self.model = "llama3-70b-8192"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self.client:
            return (
                "MOCK AI RESPONSE: Groq API key is missing. "
                "This is where the AI reasoning would appear based on the structured context."
            )

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=2048,
        )
        return completion.choices[0].message.content
