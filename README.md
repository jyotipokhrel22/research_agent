# Research Intelligence System (Current Build)

This repository contains a multi-stage research analysis pipeline that processes arXiv papers into structured insights and research gaps.

## Pipeline Overview

Current pipeline flow:

`User Query -> arXiv Retrieval -> LLM Extraction -> Comparator -> Gap Detection`

Planned future flow:

`... -> RAG -> Normalization (advanced) -> Advanced Reasoning -> API/Systemization`

## What Is Implemented Now

### Phase 1: Extraction Stabilization (Implemented)
- `Paper` schema with validators (`app/models/paper.py`)
- LLM-based extraction of structured fields (`app/services/extractor.py`)
- arXiv ingestion client (`app/services/arxiv_client.py`, `app/services/arxiv.py`)
- Resilient fallback for required fields (`paper_id`, `title`, `year`, `abstract`) when model output is incomplete

### Phase 2: Comparator (Implemented)
- Deterministic pure-Python aggregation (`app/analysis/comparator.py`)
- Minimal normalization and null filtering
- Outputs:
  - `method_distribution`
  - `method_clusters`
  - `dataset_distribution`
  - `dataset_diversity_score`
  - `metric_distribution`
  - `limitations`
  - `limitation_distribution`
  - `limitation_frequency`
- Important design decision: `missing_signals` are intentionally **not** passed downstream to avoid trivial gap generation.

### Phase 3: Gap Detection (Implemented)
- LLM-powered gap synthesis from comparator output (`app/analysis/gap_detector.py`)
- Strict validation layer:
  - schema enforcement
  - evidence must be list and contain at least 2 entries
  - evidence grounding against comparator JSON
  - confidence type/range checks
  - deduplication and hard output cap
  - rejection of trivial/invalid gap patterns (`missing_`, `_count`, generic statements)
- Prompt constraints force non-trivial synthesized insights.

## Runtime Modes

### Real Mode (recommended)
Uses real arXiv + OpenRouter model.

Requirements:
- `arxiv` package installed
- `openai` package installed
- OpenRouter API key configured

Environment variables:
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL` (optional; falls back to `MODEL_NAME` in `app/config.py`)

### Stub/Offline Mode
If dependencies or keys are missing, system falls back to deterministic stubs so the pipeline can still be executed for local testing.

## How To Run

### Run full pipeline
```bash
python app/pipeline/run_pipeline.py --query "multi agent reinforcement learning communication" --max 8
```

### Run comparator example only
```bash
python -m app.analysis.comparator
```

### Run gap detector example only
```bash
python -m app.analysis.gap_detector
```

## Verification Checklist (Real Papers)

Use this checklist for a valid end-to-end run:

1. Retrieval returns real abstracts (no stub warning).
2. Extraction succeeds for multiple papers (target >= 5).
3. Comparator output is non-empty for method/dataset/limitation distributions.
4. Gap output has 1-3 high-quality gaps (not key restatements).
5. Each gap has >=2 evidence lines present in comparator output.
6. Evidence is specific and actionable (not generic "improve performance").

## Current Known Limitations

- Comparator method clustering is rule-based and lightweight.
- Dataset normalization is alias/rule-based (not semantic clustering).
- Gap quality depends on extraction quality and paper coverage.
- No RAG/chunk-level retrieval yet (abstract-heavy extraction).

## Next Planned Work

### Phase 4: RAG
- Section chunking (methods/experiments/limitations)
- Embedding + retrieval
- Retrieval-augmented extraction

### Phase 5: Normalization
- Stronger canonical mapping for methods/datasets

### Phase 6: Advanced Reasoning
- contradiction detection
- temporal comparison
- optional multi-agent refinement

### Phase 7: Systemization
- FastAPI endpoints
- async pipeline
- caching for LLM/retrieval

## Main Source Files

- Pipeline entrypoint: `app/pipeline/run_pipeline.py`
- Extraction: `app/services/extractor.py`
- LLM client: `app/services/llm.py`
- arXiv retrieval: `app/services/arxiv_client.py`, `app/services/arxiv.py`
- Comparator: `app/analysis/comparator.py`
- Gap detection: `app/analysis/gap_detector.py`
- Paper schema: `app/models/paper.py`
