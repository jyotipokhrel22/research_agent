from __future__ import annotations

import json
import os

from app.config import MODEL_NAME, OPENROUTER_API_KEY

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class LLMClient:
    """Wraps an OpenAI-compatible client, with a stub fallback when unavailable."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        resolved_api_key = api_key or OPENROUTER_API_KEY or os.getenv("OPENAI_API_KEY")
        resolved_model = model or os.getenv("OPENROUTER_MODEL") or MODEL_NAME

        if OpenAI is None or resolved_api_key is None:
            print("OpenAI package unavailable; using deterministic offline LLM stub.")
            self.client = None
            self.model = resolved_model
        else:
            self.client = OpenAI(
                api_key=resolved_api_key,
                base_url="https://openrouter.ai/api/v1",
            )
            self.model = resolved_model
            print(f"Using OpenRouter model: {self.model}")

    def generate(self, prompt: str) -> str:
        if self.client is None:
            return self._stub_response(prompt)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You extract structured research data. Always return valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        content = response.choices[0].message.content
        return self._clean(content)

    def _clean(self, text: str) -> str:
        """Remove common markdown wrappers around JSON."""
        if not text:
            return ""

        return text.replace("```json", "").replace("```", "").strip()

    def _stub_response(self, prompt: str) -> str:
        """Return deterministic JSON in offline mode based on prompt intent."""
        normalized_prompt = prompt.lower()

        if "schema" in normalized_prompt and '"paper_id"' in normalized_prompt:
            paper = {
                "paper_id": "stub-paper",
                "title": "Stub Extracted Paper",
                "year": 2025,
                "problem": "multi-agent coordination with limited communication",
                "method": "policy-gradient reinforcement learning with communication",
                "assumptions": ["cooperative setting", "partial observability"],
                "datasets": ["hanabi"],
                "metrics": ["score"],
                "baselines": [],
                "key_results": "Improves cooperative score over non-communication baselines.",
                "limitations": ["evaluated mainly on one benchmark"],
                "future_work": ["evaluate on additional cooperative environments"],
                "domain": "multi-agent reinforcement learning",
            }
            return json.dumps(paper)

        gaps = [
            {
                "gap": "Evaluation breadth is narrow",
                "evidence": [
                    "\"dataset_distribution\": {\"hanabi\": 1}",
                    "\"limitation_distribution\": {\"evaluated mainly on one benchmark\": 1}"
                ],
                "why_it_matters": "Limited benchmark diversity weakens confidence in generalization claims.",
                "proposed_direction": "Evaluate methods on additional cooperative MARL benchmarks beyond Hanabi.",
                "confidence": 0.45,
            }
        ]
        return json.dumps(gaps)
