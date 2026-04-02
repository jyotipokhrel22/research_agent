from __future__ import annotations

"""Phase 3: Gap detection powered by structured comparator output and the LLM."""

import json
from pprint import pprint
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.llm import LLMClient
else:
    LLMClient = Any


class GapDetector:
    """Converts comparator aggregates into actionable research gaps via an LLM."""

    REQUIRED_FIELDS = {
        "gap",
        "evidence",
        "why_it_matters",
        "proposed_direction",
        "confidence",
    }

    def __init__(self, llm_client: LLMClient, max_gaps: int = 5):
        self.llm_client = llm_client
        self.max_gaps = max_gaps

    def run(self, comparator_output: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not comparator_output.get("method_distribution") and not comparator_output.get("dataset_distribution"):
            print("Comparator output is empty. Skipping gap detection.")
            return []
        prompt = self._build_prompt(comparator_output)
        raw_response = self.llm_client.generate(prompt)
        print("\n=== RAW LLM RESPONSE ===\n")
        print(raw_response)
        gaps = self._parse_response(raw_response)
        validated = self._validate_gaps(gaps, comparator_output)
        validated.sort(key=lambda gap: gap["confidence"], reverse=True)
        deduped = self._deduplicate(validated)
        return deduped[: self.max_gaps]

    def _build_prompt(self, comparator_output: Dict[str, Any]) -> str:
        instructions = [
            "You are a research analyst identifying NON-TRIVIAL gaps.",
            "Produce a JSON array where each item contains the keys "
            '"gap", "evidence", "why_it_matters", '
            '"proposed_direction", and "confidence".',
            "A gap MUST be a synthesized insight across multiple papers.",
            "A gap MUST be based on distributions or repeated patterns.",
            "A gap MUST be expressed in natural language, not key names.",
            "Each gap MUST combine at least 2 signals (e.g., dataset_distribution + limitation_distribution).",
            f"Limit yourself to at most {self.max_gaps} gaps.",
            "Set confidence between 0 and 1 depending on how strong the evidence is.",
            "STRICTLY FORBIDDEN: using field names like missing_datasets_count.",
            "STRICTLY FORBIDDEN: mentioning '_count' anywhere.",
            "STRICTLY FORBIDDEN: restating raw input keys as the gap.",
            "STRICTLY FORBIDDEN: generic suggestions like 'use more data'.",
            "If you cannot find such gaps, return an empty list [].",
            "Return ONLY valid JSON.",
            "Do not include explanations, comments, or markdown wrappers.",
        ]

        return "\n".join(instructions) + "\n\nComparator output:\n" + json.dumps(
            comparator_output, indent=2
        )

    def _is_evidence_grounded(
        self, evidence: List[str], comparator_output: Dict[str, Any]
    ) -> bool:
        blob = json.dumps(comparator_output).lower()
        for entry in evidence:
            normalized_entry = entry.lower().strip()
            if normalized_entry not in blob:
                return False
        return True

    def _deduplicate(self, gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        unique = []
        for gap in gaps:
            key = gap["gap"].lower().strip()
            if key in seen:
                continue
            seen.add(key)
            unique.append(gap)
        return unique

    def _parse_response(self, raw: str) -> List[Dict[str, Any]]:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            print("Failed to parse LLM response as JSON")
            return []

        if not isinstance(parsed, list):
            print("LLM response is not a list. Ignoring.")
            return []
        return parsed

    def _is_trivial_gap(self, gap_text: str, why_it_matters: str) -> bool:
        combined = f"{gap_text} {why_it_matters}".lower()
        trivial_markers = [
            "improve performance",
            "future work",
            "more research is needed",
            "additional experiments",
            "further evaluation",
        ]
        if len(gap_text.strip()) < 20:
            return True
        return any(marker in combined for marker in trivial_markers)

    def _is_invalid_gap(self, gap_text: str) -> bool:
        normalized = gap_text.lower()
        banned_patterns = [
            "missing_",
            "_count",
            "lack of data",
            "need more data",
            "improve performance",
        ]
        return any(pattern in normalized for pattern in banned_patterns)

    def _validate_gaps(
        self, gaps: List[Dict[str, Any]], comparator_output: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        validated: List[Dict[str, Any]] = []
        for gap in gaps:
            if not self.REQUIRED_FIELDS.issubset(gap):
                continue

            evidence = gap["evidence"]
            if not isinstance(evidence, list):
                continue

            if self._is_invalid_gap(str(gap["gap"])):
                continue

            if self._is_trivial_gap(str(gap["gap"]), str(gap["why_it_matters"])):
                continue

            if len(evidence) < 2:
                continue

            if not self._is_evidence_grounded(evidence, comparator_output):
                continue

            try:
                confidence = float(gap["confidence"])
            except (TypeError, ValueError):
                continue

            if not 0 <= confidence <= 1:
                continue

            validated.append(
                {
                    "gap": gap["gap"],
                    "evidence": evidence,
                    "why_it_matters": gap["why_it_matters"],
                    "proposed_direction": gap["proposed_direction"],
                    "confidence": confidence,
                }
            )

        return validated


class _StubLLMClient:
    """Minimal LLM client used for offline example output."""

    def generate(self, prompt: str) -> str:
        gaps = [
            {
                "gap": "Dataset coverage is concentrated on two benchmarks",
                "evidence": [
                    "\"dataset_distribution\": {\"cifar10\": 2, \"imagenet\": 2}",
                    "\"limitation_distribution\": {\"limited to small vision benchmarks\": 1, \"needs expensive training runs\": 1, \"missing real-world validation\": 1}"
                ],
                "why_it_matters": "Generalization claims are weak when evaluation is concentrated in a narrow benchmark set.",
                "proposed_direction": "Add at least one non-ImageNet-style benchmark and one real-world task suite for evaluation.",
                "confidence": 0.55,
            },
            {
                "gap": "Method concentration is narrow relative to evaluation breadth",
                "evidence": [
                    "\"method_distribution\": {\"transformer\": 2}",
                    "\"dataset_distribution\": {\"cifar10\": 2, \"imagenet\": 2}"
                ],
                "why_it_matters": "A concentrated method landscape can hide whether gains come from architecture novelty or dataset selection effects.",
                "proposed_direction": "Compare at least one non-transformer baseline under the same datasets and metrics.",
                "confidence": 0.4,
            },
        ]
        return json.dumps(gaps)


def example_usage() -> None:
    """Demonstrate gap detector output with sample comparator data."""
    sample_comparator_output = {
        "method_distribution": {"transformer": 2},
        "method_clusters": {"transformer": 2},
        "dataset_distribution": {"cifar10": 2, "imagenet": 2},
        "dataset_diversity_score": 0.5,
        "metric_distribution": {"accuracy": 2, "f1": 2, "precision": 1},
        "limitations": [
            "limited to small vision benchmarks",
            "needs expensive training runs",
            "missing real-world validation",
        ],
        "limitation_distribution": {
            "limited to small vision benchmarks": 1,
            "needs expensive training runs": 1,
            "missing real-world validation": 1,
        },
        "limitation_frequency": {
            "limited to small vision benchmarks": 1,
            "needs expensive training runs": 1,
            "missing real-world validation": 1,
        },
    }

    detector = GapDetector(_StubLLMClient())
    gaps = detector.run(sample_comparator_output)

    print("\n=== Detected Research Gaps ===\n")
    pprint(gaps)


if __name__ == "__main__":
    example_usage()
