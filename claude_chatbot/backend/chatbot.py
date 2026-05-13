import os
import anthropic

try:
    import openai as _openai
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

SYSTEM_PROMPT = """You are a helpful, friendly, and knowledgeable AI assistant.
You provide clear, accurate, and concise responses. You maintain full context
across the conversation and can assist with coding, writing, analysis, math,
and general knowledge. When answering, be direct and avoid unnecessary filler."""


class TerminalChatbot:
    """Multi-turn terminal chatbot — Anthropic primary, OpenAI fallback."""

    def __init__(self) -> None:
        # Message history is provider-agnostic and reused for multi-turn context.
        self.messages: list[dict] = []
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")

        # Prefer Anthropic when configured, otherwise fall back to OpenAI.
        if anthropic_key:
            self._client = anthropic.Anthropic(api_key=anthropic_key)
            self.model = "claude-sonnet-4-6"
            self.provider = "anthropic"
            # Cache-control hint allows prompt caching optimizations on Anthropic.
            self._system = [
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ]
        elif openai_key and _OPENAI_AVAILABLE:
            self._client = _openai.OpenAI(api_key=openai_key)
            self.model = "gpt-4o"
            self.provider = "openai"
        else:
            raise EnvironmentError(
                "No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY."
            )

    def send(self, user_input: str) -> tuple[str, object]:
        # Append the latest user message before sending the full conversation.
        self.messages.append({"role": "user", "content": user_input})

        if self.provider == "anthropic":
            response = self._client.messages.create(
                model=self.model,
                max_tokens=8096,
                system=self._system,
                messages=self.messages,
            )
            # Anthropic can return multiple content blocks; keep the first text payload.
            reply = next(
                (block.text for block in response.content if block.type == "text"), ""
            )
            usage = response.usage
        else:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + self.messages,
            )
            reply = response.choices[0].message.content or ""
            usage = response.usage

        # Store assistant reply so the next turn has full context.
        self.messages.append({"role": "assistant", "content": reply})
        return reply, usage

    def reset(self) -> None:
        # Hard reset of local in-memory context.
        self.messages = []

    @property
    def turn_count(self) -> int:
        return len(self.messages) // 2
