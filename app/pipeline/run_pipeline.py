import os
import sys

if __name__ == "__main__" and __package__ is None:
    package_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
    if package_root not in sys.path:
        sys.path.insert(0, package_root)

from app.services.arxiv import fetch_papers  # your existing code
from app.services.extractor import Extractor  # your synthesis agent
from app.analysis.comparator import Comparator
from app.analysis.gap_detector import GapDetector
from app.services.llm import LLMClient


def run(query: str, k: int = 5):
    print(f"\n=== QUERY: {query} ===\n")

    # 1. Retrieve
    raw_papers = fetch_papers(query, max_results=k)

    # 2. Extract
    llm_client = LLMClient()
    extractor = Extractor(llm_client)
    structured = []

    for i, raw in enumerate(raw_papers):
        print(f"\n--- PAPER {i+1} ---")
        try:
            print("\nRAW INPUT:\n", raw.get("summary") or raw.get("abstract"))
            paper = extractor.run(raw)
            print(paper)
            if paper:
                structured.append(paper)
            else:
                print("Extractor returned None; skipping paper.")
        except Exception as e:
            print(f"Extraction failed: {e}")

    print(f"\nExtracted {len(structured)} papers")

    # 3. Comparator
    if not structured:
        print("\nNo valid papers extracted. Skipping comparator and gap detection.\n")
        return []

    comparator = Comparator(structured)
    comp_output = comparator.run()

    print("\n=== COMPARATOR OUTPUT ===\n")
    print(comp_output)

    # 4. Gap Detection
    gap_detector = GapDetector(llm_client)
    gaps = gap_detector.run(comp_output)

    print("\n=== FINAL GAPS ===\n")
    for g in gaps:
        print(g)

    return gaps


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the research pipeline.")
    parser.add_argument("--query", "-q", default="multi-agent research", help="Search query for arXiv")
    parser.add_argument("--max", "-k", type=int, default=3, help="Number of papers to fetch")
    args = parser.parse_args()

    run(args.query, k=args.max)
