from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from openai import OpenAI
from .pii import redact_pii, contains_pii


@dataclass(frozen=True)
class LlmClient:
    api_key: str
    model: str
    embed_model: str

    def _client(self) -> OpenAI:
        return OpenAI(api_key=self.api_key)

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        sanitized = [redact_pii(text) for text in texts]
        if any(contains_pii(text) for text in sanitized):
            raise ValueError("PII detected after redaction")
        client = self._client()
        response = client.embeddings.create(model=self.embed_model, input=sanitized)
        return [item.embedding for item in response.data]

    def safe_chat(self, system_prompt: str, user_prompt: str) -> str:
        sanitized_system = redact_pii(system_prompt)
        sanitized_user = redact_pii(user_prompt)
        if contains_pii(sanitized_system) or contains_pii(sanitized_user):
            raise ValueError("PII detected after redaction")
        client = self._client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": sanitized_system},
                {"role": "user", "content": sanitized_user},
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content or ""
