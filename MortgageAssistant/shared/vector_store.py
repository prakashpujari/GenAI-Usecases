from __future__ import annotations

from typing import Any, Dict, List
from opensearchpy import OpenSearch

from shared.config import settings


def get_opensearch_client() -> OpenSearch:
    return OpenSearch(hosts=[settings.opensearch_endpoint])


def index_embedding(record: Dict[str, Any]) -> None:
    client = get_opensearch_client()
    client.index(index=settings.opensearch_index, body=record)


def search_embeddings(
    query_vector: List[float],
    loan_id: str,
    document_types: List[str] | None,
    k: int = 5,
) -> List[Dict[str, Any]]:
    client = get_opensearch_client()
    must_filters: List[Dict[str, Any]] = [{"term": {"metadata.loan_id": loan_id}}]
    if document_types:
        must_filters.append({"terms": {"metadata.document_type": document_types}})

    query = {
        "size": k,
        "query": {
            "bool": {
                "filter": must_filters,
                "must": {
                    "knn": {
                        "embedding": {
                            "vector": query_vector,
                            "k": k,
                        }
                    }
                },
            }
        },
    }

    response = client.search(index=settings.opensearch_index, body=query)
    return [hit["_source"] for hit in response.get("hits", {}).get("hits", [])]
