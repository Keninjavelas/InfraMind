from abc import ABC, abstractmethod


class AIProvider(ABC):

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generates AI output based on system and user prompts."""
        pass
