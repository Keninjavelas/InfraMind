from app.ai.groq_client import GroqClient
from app.ai.multi_providers import (
    AnthropicProvider,
    GeminiProvider,
    OllamaProvider,
    OpenAIProvider,
    OpenRouterProvider,
)
from app.ai.prompts import cost, explain, security
from app.schemas.infra_schema import InfraSummary


class AIOrchestrator:
    def __init__(
        self,
        provider: str = "groq",
        api_key: str = None,
        model: str = None,
        base_url: str = None,
    ):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = self._initialize_client()

    def _initialize_client(self):
        # Auto-detect logic: If provider is "auto", use user key if present, else fallback to Groq with server key
        if self.provider == "auto":
            if self.api_key:
                # If key starts with gsk_, assume Groq
                if self.api_key.startswith("gsk_"):
                    return GroqClient(api_key=self.api_key)
                # If key starts with sk-ant, assume Anthropic
                elif self.api_key.startswith("sk-ant"):
                    return AnthropicProvider(api_key=self.api_key)
                # If key starts with sk-, assume OpenAI
                elif self.api_key.startswith("sk-"):
                    return OpenAIProvider(api_key=self.api_key)
                # Default to OpenAI if sk- pattern matches or other
                return OpenAIProvider(api_key=self.api_key)
            else:
                return GroqClient()  # Fallback to server-side Groq

        if self.provider == "groq":
            return GroqClient(api_key=self.api_key)
        elif self.provider == "openai":
            return OpenAIProvider(api_key=self.api_key, model=self.model or "gpt-4o")
        elif self.provider == "anthropic":
            return AnthropicProvider(
                api_key=self.api_key, model=self.model or "claude-3-5-sonnet-20240620"
            )
        elif self.provider == "gemini":
            return GeminiProvider(
                api_key=self.api_key, model=self.model or "gemini-1.5-pro"
            )
        elif self.provider == "openrouter":
            return OpenRouterProvider(
                api_key=self.api_key, model=self.model or "anthropic/claude-3.5-sonnet"
            )
        elif self.provider == "ollama":
            return OllamaProvider(
                host=self.base_url or "http://localhost:11434",
                model=self.model or "llama3",
            )

        return GroqClient(api_key=self.api_key)

    def _summary_to_json(self, summary: InfraSummary) -> str:
        return summary.model_dump_json(indent=2)

    def explain_infrastructure(
        self, summary: InfraSummary, query: str = "Explain this infrastructure."
    ) -> str:
        context = self._summary_to_json(summary)
        prompt = explain.build_explain_prompt(context, query)
        return self.client.generate(explain.SYSTEM_PROMPT, prompt)

    def review_security(
        self, summary: InfraSummary, query: str = "What are the biggest security risks?"
    ) -> str:
        context = self._summary_to_json(summary)
        prompt = security.build_security_prompt(context, query)
        return self.client.generate(security.SYSTEM_PROMPT, prompt)

    def review_cost(
        self, summary: InfraSummary, query: str = "How can I optimize costs here?"
    ) -> str:
        context = self._summary_to_json(summary)
        prompt = cost.build_cost_prompt(context, query)
        return self.client.generate(cost.SYSTEM_PROMPT, prompt)
