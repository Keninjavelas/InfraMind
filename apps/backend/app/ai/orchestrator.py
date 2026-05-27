from app.ai.groq_client import GroqClient
from app.ai.prompts import cost, explain, security
from app.schemas.infra_schema import InfraSummary


class AIOrchestrator:
    def __init__(self):
        self.client = GroqClient()

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
