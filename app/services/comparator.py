from collections import Counter, defaultdict
from typing import List, Dict

from app.models.paper import Paper
from app.models.comparison import ComparisonResult


class Comparator:
    """
    Responsible for cross-paper analysis.

    Takes structured Paper objects and produces aggregated signals
    used for downstream gap detection.
    """

    def run(self, papers: List[Paper]) -> ComparisonResult:
        if not papers:
            return self._empty_result()

        return ComparisonResult(
            common_methods=self._common_methods(papers),
            distinct_methods=self._distinct_methods(papers),
            dataset_overlap=self._count_field(papers, "datasets"),
            metric_overlap=self._count_field(papers, "metrics"),
            shared_limitations=self._shared_limitations(papers),
            unique_limitations=self._unique_limitations(papers),
            contradictions=self._detect_contradictions(papers),
        )

    # Core aggregation helpers

    def _count_field(self, papers: List[Paper], field: str) -> Dict[str, int]:
        """
        Generic counter for list-based fields like datasets, metrics.
        """
        counter = Counter()

        for paper in papers:
            values = getattr(paper, field, [])
            for v in values:
                if v:
                    counter[v] += 1

        return dict(counter)

    # -----------------------------
    # Methods analysis
    # -----------------------------

    def _common_methods(self, papers: List[Paper]) -> List[str]:
        counter = Counter()

        for p in papers:
            if p.method:
                counter[p.method] += 1

        return [m for m, c in counter.items() if c > 1]

    def _distinct_methods(self, papers: List[Paper]) -> List[str]:
        counter = Counter()

        for p in papers:
            if p.method:
                counter[p.method] += 1

        return [m for m, c in counter.items() if c == 1]

    # -----------------------------
    # Limitations (most important)
    # -----------------------------

    def _shared_limitations(self, papers: List[Paper]) -> List[str]:
        counter = Counter()

        for p in papers:
            for lim in p.limitations:
                if lim:
                    counter[lim] += 1

        return [l for l, c in counter.items() if c >= 2]

    def _unique_limitations(self, papers: List[Paper]) -> List[str]:
        counter = Counter()

        for p in papers:
            for lim in p.limitations:
                if lim:
                    counter[lim] += 1

        return [l for l, c in counter.items() if c == 1]

    # -----------------------------
    # Contradictions (basic version)
    # -----------------------------

    def _detect_contradictions(self, papers: List[Paper]) -> List[str]:
        """
        Naive contradiction detection based on key_results.
        This is intentionally simple and can be upgraded later.
        """
        results_map = defaultdict(list)

        for p in papers:
            if p.method and p.key_results:
                results_map[p.method].append(p.key_results)

        contradictions = []

        for method, results in results_map.items():
            if len(results) > 1:
                # naive heuristic: differing statements
                unique_results = set(results)
                if len(unique_results) > 1:
                    contradictions.append(
                        f"Conflicting results reported for method: {method}"
                    )

        return contradictions

    # -----------------------------
    # Fallback
    # -----------------------------

    def _empty_result(self) -> ComparisonResult:
        return ComparisonResult(
            common_methods=[],
            distinct_methods=[],
            dataset_overlap={},
            metric_overlap={},
            shared_limitations=[],
            unique_limitations=[],
            contradictions=[],
        )