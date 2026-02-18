from __future__ import annotations

import json
from typing import List

import httpx
from openai import OpenAI

from shared.aws_clients import bedrock_runtime_client
from shared.config import settings


class LlmProvider:
    def __init__(self) -> None:
        self._openai = OpenAI(api_key=settings.openai_api_key)
        self._bedrock = bedrock_runtime_client()

    def embed_openai(self, text: str) -> List[float]:
        response = self._openai.embeddings.create(
            model=settings.openai_embed_model,
            input=text,
        )
        return response.data[0].embedding

    def embed_bedrock(self, text: str) -> List[float]:
        payload = json.dumps({"inputText": text})
        response = self._bedrock.invoke_model(
            modelId=settings.bedrock_embed_model,
            body=payload,
        )
        body = json.loads(response["body"].read().decode("utf-8"))
        return body["embedding"]

    def chat_openai(self, prompt: str, max_tokens: int, temperature: float) -> str:
        response = self._openai.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    def chat_bedrock(self, prompt: str, max_tokens: int, temperature: float) -> str:
        payload = json.dumps(
            {
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        )
        response = self._bedrock.invoke_model(
            modelId=settings.bedrock_chat_model,
            body=payload,
        )
        body = json.loads(response["body"].read().decode("utf-8"))
        content = body.get("content", "")
        if isinstance(content, list) and content:
            return content[0].get("text", "")
        if isinstance(content, dict):
            return content.get("text", "")
        return content or ""


async def call_service(url: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=settings.request_timeout_s) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
