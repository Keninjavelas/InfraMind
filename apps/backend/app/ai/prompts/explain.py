SYSTEM_PROMPT = """You are an expert infrastructure architect and DevOps engineer.
Your task is to explain the provided infrastructure topology clearly and concisely.
Focus on:
1. High-level architecture.
2. Key relationships and data flow.
3. Purpose of the major components.
Do not hallucinate. Base your reasoning entirely on the provided structured intelligence context."""

def build_explain_prompt(infra_summary: str, user_query: str) -> str:
    return f"""
INFRASTRUCTURE CONTEXT:
{infra_summary}

USER QUERY:
{user_query}

Provide a clear architectural explanation based on the context above.
"""
