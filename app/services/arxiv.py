"""Simple arXiv fetcher used by the pipeline."""

from typing import Any, Dict, List

from app.services.arxiv_client import ArxivClient


def fetch_papers(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    client = ArxivClient()
    return client.search(query, max_results=max_results)
