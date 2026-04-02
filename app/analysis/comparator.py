from __future__ import annotations

"""Comparator phase logic for aggregated insights."""

import os
import sys
from collections import Counter
from pprint import pprint
from typing import Any, Dict, Iterable, List

if __name__ == "__main__" and __package__ is None:
    package_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
    if package_root not in sys.path:
        sys.path.insert(0, package_root)

from app.models.paper import Paper


NULL_TOKENS = {"", "null", "none", "n/a", "na", "unknown", "not specified"}


def _normalize(value: str) -> str:
    return value.lower().strip()


def _clean_text(value: str | None) -> str:
    if value is None:
        return ""
    cleaned = _normalize(value)
    if cleaned in NULL_TOKENS:
        return ""
    return cleaned


def _normalize_method(method: str) -> str:
    normalized = _clean_text(method)
    if not normalized:
        return ""
    normalized = normalized.replace("-", " ").replace("/", " ")
    stopwords = {"based", "approach", "method", "model", "framework", "system"}
    for token in normalized.split():
        if token not in stopwords:
            return token
    return normalized.split()[0]


def _normalize_dataset(value: str) -> str:
    normalized = _clean_text(value)
    if not normalized:
        return ""
    normalized = normalized.replace("_", "").replace("-", "").replace(" ", "")
    aliases = {
        "cifar10": "cifar10",
        "cifar100": "cifar100",
        "imagenet1k": "imagenet",
        "imagenet": "imagenet",
        "mscoco": "coco",
        "coco": "coco",
    }
    return aliases.get(normalized, normalized)


def _counter_from_items(items: Iterable[str]) -> Counter[str]:
    counter = Counter()
    for item in items:
        normalized = _clean_text(item)
        if normalized:
            counter[normalized] += 1
    return counter


def _to_sorted_dict(counter: Counter[str]) -> Dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def _build_method_clusters(method_distribution: Dict[str, int]) -> Dict[str, int]:
    clusters = {
        "transformer": {"transformer", "bert", "gpt", "vit"},
        "reinforcement_learning": {"rl", "reinforcement", "policy", "qlearning"},
        "graph": {"graph", "gnn", "gcn"},
        "diffusion": {"diffusion"},
    }

    cluster_counts: Dict[str, int] = {}
    for method, count in method_distribution.items():
        matched = False
        for cluster_name, keywords in clusters.items():
            if method in keywords:
                cluster_counts[cluster_name] = cluster_counts.get(cluster_name, 0) + count
                matched = True
                break
        if not matched:
            cluster_counts["other"] = cluster_counts.get("other", 0) + count

    return dict(sorted(cluster_counts.items()))


def _dataset_diversity_score(dataset_distribution: Dict[str, int], total_papers: int) -> float:
    if total_papers <= 0:
        return 0.0
    unique_datasets = len(dataset_distribution)
    return round(unique_datasets / total_papers, 3)


class Comparator:
    """Builds deterministic aggregate insights from extracted papers."""

    def __init__(self, papers: List[Paper]):
        self.papers = papers

    def run(self) -> Dict[str, Any]:
        method_distribution = _to_sorted_dict(
            _counter_from_items(
                _normalize_method(p.method) for p in self.papers if p.method
            )
        )

        dataset_distribution = _to_sorted_dict(
            _counter_from_items(
                _normalize_dataset(dataset)
                for p in self.papers
                for dataset in p.datasets
            )
        )

        metric_distribution = _to_sorted_dict(
            _counter_from_items(metric for p in self.papers for metric in p.metrics)
        )

        limitations: List[str] = []
        for paper in self.papers:
            for limitation in paper.limitations:
                normalized_limitation = _normalize(limitation)
                if normalized_limitation:
                    limitations.append(normalized_limitation)

        limitation_distribution = _to_sorted_dict(
            _counter_from_items(limitations)
        )

        return {
            "method_distribution": method_distribution,
            "method_clusters": _build_method_clusters(method_distribution),
            "dataset_distribution": dataset_distribution,
            "dataset_diversity_score": _dataset_diversity_score(
                dataset_distribution, len(self.papers)
            ),
            "metric_distribution": metric_distribution,
            "limitations": limitations,
            "limitation_distribution": limitation_distribution,
            "limitation_frequency": limitation_distribution,
        }


def example_usage() -> None:
    """Demonstrate Comparator output and ensure pattern visibility."""
    papers = [
        Paper(
            paper_id="test-001",
            title="Simple Method",
            year=2024,
            method="Transformer-based aggregator",
            datasets=["CIFAR-10"],
            metrics=["Accuracy", "F1"],
            limitations=["Limited to small vision benchmarks"],
        ),
        Paper(
            paper_id="test-002",
            title="SOTA on Continual Learning",
            year=2025,
            method="Transformer-based aggregator",
            datasets=["cifar10", "ImageNet"],
            metrics=["accuracy"],
            limitations=["Needs expensive training runs"],
        ),
        Paper(
            paper_id="test-003",
            title="Benchmarking Evaluation",
            year=2023,
            datasets=["ImageNet"],
            metrics=["f1"],
            limitations=[],
        ),
        Paper(
            paper_id="test-004",
            title="Weakness tracking",
            year=2022,
            method=None,
            datasets=[],
            metrics=["precision"],
            limitations=["Missing real-world validation"],
        ),
    ]

    comparator = Comparator(papers)
    output = comparator.run()

    print("\n=== Comparator Insights ===\n")
    pprint(output)

    print("\nKey signals:")
    pprint(
        {
            "method_distribution": output["method_distribution"],
            "dataset_distribution": output["dataset_distribution"],
            "limitation_distribution": output["limitation_distribution"],
        }
    )


if __name__ == "__main__":
    example_usage()
