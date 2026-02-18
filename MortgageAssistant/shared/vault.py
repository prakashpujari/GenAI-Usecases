from __future__ import annotations

from typing import Dict
from uuid import uuid4

from shared.aws_clients import dynamodb_resource
from shared.config import settings


class SecureVault:
    def __init__(self) -> None:
        self._table = dynamodb_resource().Table(settings.dynamodb_table)

    def store_pii(self, document_id: str, pii_map: Dict[str, str]) -> Dict[str, str]:
        token_storage = {}
        text_to_token: Dict[str, str] = {}
        for pii_text, _pii_type in pii_map.items():
            token = str(uuid4())
            text_to_token[pii_text] = token
            token_storage[token] = pii_text

        if token_storage:
            self._table.put_item(
                Item={
                    "document_id": document_id,
                    "tokens": token_storage,
                }
            )

        return text_to_token

    def resolve_token(self, document_id: str, token: str) -> str | None:
        response = self._table.get_item(Key={"document_id": document_id})
        item = response.get("Item")
        if not item:
            return None
        return item.get("tokens", {}).get(token)
