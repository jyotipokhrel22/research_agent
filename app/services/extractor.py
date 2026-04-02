# app/services/extractor.py

from typing import Any, Dict, Optional
from app.models.paper import Paper
from app.services.llm import LLMClient
from app.utils.json_utils import safe_json_parse

def build_prompt(content: str) -> str:
    return f"""
You are extracting structured information from a research paper.

Return ONLY valid JSON.

Schema:
{{
  "paper_id": "...",
  "title": "...",
  "year": 2024,
  "problem": "...",
  "method": "...",
  "assumptions": ["..."],
  "datasets": ["..."],
  "metrics": ["..."],
  "baselines": ["..."],
  "key_results": "...",
  "limitations": ["..."],
  "future_work": ["..."],
  "domain": "..."
}}

Rules:
- Extract information that is clearly stated or strongly implied
- Do NOT invent new facts
- If a field is truly missing, return null or []
- Be concise and literal
- Return only JSON

Content:
{content}
"""

class PaperExtractor:
    def __init__(self, llm: LLMClient, max_retries: int = 2):
        self.llm = llm
        self.max_retries = max_retries

    def extract(self, content: str, defaults: Optional[Dict[str, Any]] = None) -> Optional[Paper]:
        """
        Main extraction entrypoint.

        Returns:
            Paper object if successful, else None
        """

        for attempt in range(self.max_retries + 1):
            try:
                prompt = build_prompt(content)

                response = self.llm.generate(prompt)

                data = safe_json_parse(response)

                if not data:
                    raise ValueError("Empty or invalid JSON")

                paper = self._build_paper(data, defaults or {})

                return paper

            except Exception as e:
                if attempt == self.max_retries:
                    return None

        return None

    def _build_paper(self, data: Dict[str, Any], defaults: Dict[str, Any]) -> Paper:
        # Keep required metadata stable even when the model omits them.
        merged = dict(data)
        merged["paper_id"] = merged.get("paper_id") or defaults.get("paper_id", "unknown-paper")
        merged["title"] = merged.get("title") or defaults.get("title", "untitled-paper")
        merged["year"] = merged.get("year") or defaults.get("year", 0)
        merged["abstract"] = merged.get("abstract") or defaults.get("abstract")
        return Paper(**merged)

    def run(self, raw_paper: dict) -> Optional[Paper]:
        abstract = raw_paper.get("summary") or raw_paper.get("abstract") or ""
        defaults = {
            "paper_id": raw_paper.get("paper_id") or raw_paper.get("id"),
            "title": raw_paper.get("title"),
            "year": raw_paper.get("year"),
            "abstract": abstract,
        }
        return self.extract(abstract, defaults=defaults)


Extractor = PaperExtractor
