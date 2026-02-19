from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from openai import OpenAI
from .pii import redact_pii, contains_pii
from .logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class LlmClient:
    api_key: str
    model: str
    embed_model: str

    def _client(self) -> OpenAI:
        return OpenAI(api_key=self.api_key)

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        logger.info(f"Embedding texts: {len(list(texts))} texts")
        texts_list = list(texts)
        sanitized = [redact_pii(text) for text in texts_list]
        if any(contains_pii(text) for text in sanitized):
            logger.error("PII detected after redaction in embed_texts")
            raise ValueError("PII detected after redaction")
        logger.info(f"Calling OpenAI embeddings API with model={self.embed_model}")
        client = self._client()
        response = client.embeddings.create(model=self.embed_model, input=sanitized)
        embeddings = [item.embedding for item in response.data]
        logger.info(f"Successfully generated {len(embeddings)} embeddings")
        return embeddings

    def safe_chat(self, system_prompt: str, user_prompt: str) -> str:
        logger.info(f"Safe chat: system_prompt_length={len(system_prompt)}, user_prompt_length={len(user_prompt)}")
        sanitized_system = redact_pii(system_prompt)
        sanitized_user = redact_pii(user_prompt)
        if contains_pii(sanitized_system) or contains_pii(sanitized_user):
            logger.error("PII detected after redaction in safe_chat")
            raise ValueError("PII detected after redaction")
        logger.info(f"Calling OpenAI chat API with model={self.model}")
        client = self._client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": sanitized_system},
                {"role": "user", "content": sanitized_user},
            ],
            temperature=0.0,
        )
        result = response.choices[0].message.content or ""
        logger.info(f"Chat response received: {len(result)} characters")
        return result
